import inspect
from copy import deepcopy
from enum import StrEnum
from typing import TYPE_CHECKING

import networkx as nx
from networkx import Graph, is_connected
from numpy import array, max, min, pi, sign
from numpy.core.numeric import Inf, allclose
from numpy.lib.function_base import average
from numpy.random import rand

from pydistsim.algorithm import Algorithm
from pydistsim.channeltype import ChannelType
from pydistsim.conf import settings
from pydistsim.environment import Environment
from pydistsim.logger import logger
from pydistsim.node import Node
from pydistsim.sensor import CompositeSensor
from pydistsim.utils.helpers import pydistsim_equal_objects

if TYPE_CHECKING:
    from pydistsim.algorithm import Algorithm
    from pydistsim.message import Message

AlgorithmsParam = tuple[type[Algorithm] | tuple[type[Algorithm], dict]]


class Network(Graph):
    """
    Represents a network in a distributed simulation.

    The Network class extends the Graph class and provides additional functionality for managing nodes, algorithms, and network properties.
    """

    def __init__(
        self,
        environment=None,
        channelType=None,
        algorithms: AlgorithmsParam = (),
        networkRouting=True,
        graph=None,
        **kwargs,
    ):
        """
        Initialize a Network instance.

        :param environment: The environment in which the network operates. If not provided, a new Environment instance will be created.
        :type environment: Environment, optional
        :param channelType: The type of channel to be used for communication. If not provided, a new ChannelType instance will be created using the environment.
        :type channelType: ChannelType, optional
        :param algorithms: The algorithms to be executed on the network. If not provided, the default algorithms defined in settings.ALGORITHMS will be used.
        :type algorithms: AlgorithmsParam, optional
        :param networkRouting: Flag indicating whether network routing is enabled. Defaults to True.
        :type networkRouting: bool, optional
        :param graph: The graph representing the network topology. Defaults to None.
        :type graph: NetworkX graph, optional
        :param kwargs: Additional keyword arguments.
        """
        self._environment = environment or Environment()
        self.channelType = channelType or ChannelType(self._environment)
        self.channelType.environment = self._environment
        self.pos = {}
        self.ori = {}
        self.labels = {}
        super().__init__(graph)
        self.algorithms = algorithms or settings.ALGORITHMS
        self.algorithmState = {"index": 0, "step": 1, "finished": False}
        self.outbox = []
        self.networkRouting = networkRouting
        self.simulation = None
        logger.info("Instance of Network has been initialized.")

    def copy(self, as_view=False):
        """Return a copy of the graph."""
        return deepcopy(self)

    def subnetwork(self, nbunch, pos=None):
        """
        Returns a Network instance with the specified nodes.

        :param nbunch: A list of nodes to include in the subnetwork.
        :type nbunch: list
        :param pos: Optional dictionary of node positions.
        :type pos: dict, optional
        :return: A Network instance representing the subnetwork.
        :rtype: Network
        """
        if not pos:
            pos = self.pos
        H = self.copy()
        for node in self.nodes():
            node_H = H.node_by_id(node.id)
            if node in nbunch:
                # Copy node attributes
                H.pos.update({node_H: pos[node][:2]})
                if len(pos[node]) > 2:
                    H.ori.update({node_H: pos[node][2]})
                else:
                    H.ori.update({node_H: deepcopy(self.ori[node])})
                H.labels.update({node_H: deepcopy(self.labels[node])})
                node_H.network = H
            else:
                H.remove_node(node_H)

        # Copy network attributes and reinitialize algorithms
        H.algorithms = deepcopy(self._algorithms_param) or settings.ALGORITHMS
        H.algorithmState = {"index": 0, "step": 1, "finished": False}
        H.outbox = []
        H.simulation = None

        assert isinstance(H, Network)
        return H

    def nodes_sorted(self):
        """
        Sort nodes by id, important for message ordering.

        :param data: A boolean value indicating whether to include node data in the sorted list.
        :type data: bool
        :return: A sorted list of nodes.
        :rtype: list
        """
        return list(sorted(self.nodes(), key=lambda k: k.id))

    @property
    def algorithms(self):
        """
        Set algorithms by passing tuple of Algorithm subclasses.

        >>> net.algorithms = (Algorithm1, Algorithm2,)

        For params pass tuples in form (Algorithm, params) like this

        >>> net.algorithms = ((Algorithm1, {'param1': value,}), Algorithm2)

        """
        return self._algorithms

    @algorithms.setter
    def algorithms(self, algorithms: AlgorithmsParam):
        self.reset()
        self._algorithms = ()
        if not isinstance(algorithms, tuple):
            raise PyDistSimNetworkError(NetwkErrorMsg.ALGORITHM)
        for algorithm in algorithms:
            if inspect.isclass(algorithm) and issubclass(algorithm, Algorithm):
                self._algorithms += (algorithm(self),)
            elif (
                isinstance(algorithm, tuple)
                and len(algorithm) == 2
                and issubclass(algorithm[0], Algorithm)
                and isinstance(algorithm[1], dict)
            ):
                self._algorithms += (algorithm[0](self, **algorithm[1]),)
            else:
                raise PyDistSimNetworkError(NetwkErrorMsg.ALGORITHM)

        # If everything went ok, set algorithms param for coping
        self._algorithms_param = algorithms

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, environment):
        """If net environment is changed all nodes are moved into and
        corresponding channelType environment must be changed also."""
        self._environment = environment
        self.channelType.environment = environment
        for node in self.nodes_sorted():
            self.remove_node(node)
            self.add_node(node)
        logger.warning("All nodes are moved into new environment.")

    def remove_node(self, node):
        """
        Remove a node from the network.

        :param node: The node to be removed.
        :type node: Node
        :raises PyDistSimNetworkError: If the node is not in the network.
        """
        if node not in self.nodes():
            logger.error("Node not in network")
            raise PyDistSimNetworkError(NetwkErrorMsg.NODE_NOT_IN_NET)
        super().remove_node(node)
        del self.pos[node]
        del self.labels[node]
        node.network = None
        logger.debug("Node with id %d is removed." % node.id)

    def add_node(self, node=None, pos=None, ori=None, commRange=None):
        """
        Add node to network.

        :param node: node to add, default: new node is created
        :type node: Node, optional
        :param pos: position (x,y), default: random free position in environment
        :type pos: tuple, optional
        :param ori: orientation from 0 to 2*pi, default: random orientation
        :type ori: float, optional
        :param commRange: communication range of the node, default: None
        :type commRange: float, optional

        :return: the added node
        :rtype: Node

        :raises PyDistSimNetworkError: if the given node is already in another network or the given position is not free space

        """
        if not node:
            node = Node(commRange=commRange)
        assert isinstance(node, Node)
        if not node.network:
            node.network = self
        else:
            logger.exception("Node is already in another network, can't add.")
            raise PyDistSimNetworkError(NetwkErrorMsg.NODE)

        pos = pos if pos is not None else self.find_random_pos(n=100)
        ori = ori if ori is not None else rand() * 2 * pi
        ori = ori % (2 * pi)

        if self._environment.is_space(pos):
            super().add_node(node)
            self.pos[node] = array(pos)
            self.ori[node] = ori
            self.labels[node] = str(node.id)
            logger.debug("Node %d is placed on position %s." % (node.id, pos))
            self.recalculate_edges([node])
        else:
            logger.error("Given position is not free space.")
            raise PyDistSimNetworkError(NetwkErrorMsg.NODE_SPACE)
        return node

    def node_by_id(self, id_):
        """
        Returns the first node with the given id.

        :param id_: The id of the node to search for.
        :type id_: int
        :return: The node with the given id.
        :rtype: Node
        :raises PyDistSimNetworkError: If the network does not have a node with the given id.
        """
        for n in self.nodes():
            if n.id == id_:
                return n
        logger.error("Network has no node with id %d." % id_)
        raise PyDistSimNetworkError(NetwkErrorMsg.NODE_NOT_IN_NET)

    def avg_degree(self):
        """
        Calculate the average degree of the network.

        :return: The average degree of the network.
        :rtype: float
        """
        return average(list(deg for _, deg in self.degree()))

    def modify_avg_degree(self, value):
        """
        Modifies (increases) average degree based on the given value by
        modifying nodes' commRange.

        :param value: The desired average degree value.
        :type value: float

        :raises AssertionError: If all nodes do not have the same commRange.
        :raises AssertionError: If the given value is not greater than the current average degree.

        This method increases the average degree of the network by modifying the communication range
        (`commRange`) of the nodes. It ensures that all nodes have the same communication range.

        The method uses a step-wise approach to gradually increase the average degree until it reaches
        the desired value. It adjusts the communication range of each node in the network by adding a
        step size calculated based on the difference between the desired average degree and the current
        average degree.

        The step size is determined by the `step_factor` parameter, which controls the rate of change
        in the communication range. If the step size overshoots or undershoots the desired average
        degree, the `step_factor` is halved to reduce the step size for the next iteration.

        Once the average degree reaches the desired value, the method logs the modified degree.

        Note: This method assumes that the network is initially connected and all nodes have the same
        communication range.

        Example usage:
            network.modify_avg_degree(5.0)
        """
        # assert all nodes have the same commRange
        assert allclose([n.commRange for n in self], self.nodes_sorted()[0].commRange)
        # TODO: implement decreasing of degree, preserve connected network
        assert value + settings.DEG_ATOL > self.avg_degree()  # only increment
        step_factor = 7.0
        steps = [0]
        # TODO: while condition should call validate
        while not allclose(self.avg_degree(), value, atol=settings.DEG_ATOL):
            steps.append((value - self.avg_degree()) * step_factor)
            for node in self:
                node.commRange += steps[-1]
            # variable step_factor for step size for over/undershoot cases
            if len(steps) > 2 and sign(steps[-2]) != sign(steps[-1]):
                step_factor /= 2
        logger.debug("Modified degree to %f" % self.avg_degree())

    def get_current_algorithm(self):
        """
        Try to return the current algorithm based on the algorithmState.

        :return: The current algorithm.
        :rtype: Algorithm or None

        :raises PyDistSimNetworkError: If there are no algorithms defined in the network.
        """
        if len(self.algorithms) == 0:
            logger.error("There is no algorithm defined in the network.")
            raise PyDistSimNetworkError(NetwkErrorMsg.ALGORITHM_NOT_FOUND)

        if self.algorithmState["finished"]:
            if len(self.algorithms) > self.algorithmState["index"] + 1:
                self.algorithmState["index"] += 1
                self.algorithmState["step"] = 1
                self.algorithmState["finished"] = False
            else:
                return None

        return self.algorithms[self.algorithmState["index"]]

    def reset(self):
        logger.info("Resetting network.")
        self.algorithmState = {"index": 0, "step": 1, "finished": False}
        self.reset_all_nodes()

    def show(self, *args, **kwargs):
        fig = self.get_fig(*args, **kwargs)
        fig.show()

    def savefig(self, fname="network.png", figkwargs={}, *args, **kwargs):
        self.get_fig(*args, **kwargs).savefig(fname, **figkwargs)

    def get_fig(
        self,
        positions=None,
        edgelist=None,
        nodeColor="r",
        show_labels=True,
        labels=None,
        dpi=100,
        node_size=30,
    ):
        """
        Get the figure object representing the network visualization.

        :param positions: A dictionary mapping node IDs to their positions in the network.
        :type positions: dict, optional
        :param edgelist: A list of edges to be drawn in the network.
        :type edgelist: list, optional
        :param nodeColor: The color of the nodes in the network.
        :type nodeColor: str, optional
        :param show_labels: Whether to show labels for the nodes.
        :type show_labels: bool, optional
        :param labels: A dictionary mapping node IDs to their labels.
        :type labels: dict, optional
        :param dpi: The resolution of the figure in dots per inch.
        :type dpi: int, optional
        :param node_size: The size of the nodes in the network.
        :type node_size: int, optional
        :return: The figure object representing the network visualization.
        :rtype: matplotlib.figure.Figure
        """
        try:
            from matplotlib import pyplot as plt
        except ImportError as e:
            raise ImportError("Matplotlib required for show()") from e

        # TODO: environment when positions defined
        fig_size = tuple(array(self._environment.im.shape) / dpi)

        # figsize in inches
        # default matplotlibrc is dpi=80 for plt and dpi=100 for savefig
        fig = plt.figure(figsize=fig_size, dpi=dpi, frameon=False)
        plt.imshow(self._environment.im, cmap="binary_r", vmin=0, origin="lower")
        if positions:
            # truncate positions to [x, y], i.e. lose theta
            for k, v in list(positions.items()):
                positions[k] = v[:2]
            pos = positions
            net = self.subnetwork(list(pos.keys()))
        else:
            pos = self.pos
            net = self
        labels = labels or net.labels
        nx.draw_networkx_edges(net, pos, alpha=0.6, edgelist=edgelist)
        nx.draw_networkx_nodes(
            net, pos, node_size=node_size, node_color=nodeColor, cmap="YlOrRd"
        )
        if show_labels:
            label_pos = {}
            from math import sqrt

            label_delta = sqrt(node_size * 0.6) * dpi / 100
            for n in net.nodes():
                label_pos[n] = pos[n].copy() + label_delta
            nx.draw_networkx_labels(
                net,
                label_pos,
                labels=labels,
                horizontalalignment="left",
                verticalalignment="bottom",
            )
        # plt.axis('off')
        return fig

    def recalculate_edges(self, nodes=[]):
        """
        Recalculate edges for given nodes or for all self.nodes().

        :param nodes: A list of nodes to recalculate edges for. If not provided, edges will be recalculated for all nodes in the network.
        :type nodes: list, optional

        Edge between nodes n1 and n2 are added if both are ChannelType.in_comm_range of each other.
        """
        if not nodes:
            nodes = self.nodes()
        for n1 in nodes:
            for n2 in self.nodes():
                if n1 != n2:
                    if self.channelType.in_comm_range(self, n1, n2):
                        super().add_edge(n1, n2)
                    elif self.has_edge(n1, n2):
                        self.remove_edge(n1, n2)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """
        Add an edge to the network.

        :param u_of_edge: The source node of the edge.
        :param v_of_edge: The target node of the edge.
        :param attr: Additional attributes to be assigned to the edge.
        """
        logger.warning("Edges are auto-calculated from channelType and commRange")
        super().add_edge(u_of_edge, v_of_edge, **attr)

    def find_random_pos(self, n=100):
        """
        Returns a random position in the environment.

        :param n: The maximum number of iterations to find a free space.
        :type n: int
        :return: The random position found.
        :rtype: tuple
        """
        n_init = n
        while n > 0:
            pos = rand(self._environment.dim) * tuple(
                reversed(self._environment.im.shape)
            )
            if self._environment.is_space(pos):
                break
            n -= 1
        logger.debug("Random position found in %d iterations." % (n_init - n))
        return pos

    def reset_all_nodes(self):
        """
        Reset all nodes in the network.

        :return: None
        """
        for node in self.nodes():
            node.reset()
        logger.info("Resetting all nodes.")

    def communicate(self):
        """
        Pass all messages from node's outboxes to its neighbors inboxes.

        This method collects messages from each node's outbox and delivers them to the appropriate destination.
        If the message is a broadcast, it is sent to all neighbors.
        If the message has a specific next hop, it is sent directly to that node.
        If the message has a specific destination, it is sent to that neighbor if it is reachable.
        If network routing is enabled, the message is sent to the destination using network routing.

        :return: None
        """
        # Collect messages
        for node in self.nodes_sorted():
            self.outbox.extend(node.outbox)
            node.outbox = []
        while self.outbox:
            message = self.outbox.pop()
            if message.destination is None and message.nexthop is None:
                # broadcast
                self.broadcast(message)
            elif message.nexthop is not None:
                # Node routing
                try:
                    self.send(message.nexthop, message)
                except PyDistSimMessageUndeliverable as e:
                    print(e.message)
            elif message.destination is not None:
                # Destination is neighbor
                if (
                    message.source in self.nodes()
                    and message.destination in self.neighbors(message.source)
                ):
                    self.send(message.destination, message)
                elif self.networkRouting:
                    # Network routing
                    # TODO: program network routing so it goes hop by hop only
                    #       in connected part of the network
                    self.send(message.destination, message)
                else:
                    raise PyDistSimMessageUndeliverable(
                        "Can't deliver message.", message
                    )

    def broadcast(self, message: "Message"):
        """
        Broadcasts a message to all neighbors of the source node.

        :param message: The message to be broadcasted.
        :type message: Message
        :raises PyDistSimMessageUndeliverable: If the source node is not in the network.
        """
        if message.source in self.nodes():
            for neighbor in self.neighbors(message.source):
                neighbors_message = message.copy()
                neighbors_message.destination = neighbor
                self.send(neighbor, neighbors_message)
        else:
            raise PyDistSimMessageUndeliverable(
                "Source not in network. Can't broadcast",
                message,
            )

    def send(self, destination: "Node", message: "Message"):
        """
        Send a message to a destination node in the network.

        :param destination: The destination node to send the message to.
        :type destination: Node
        :param message: The message to be sent.
        :type message: Message
        :raises PyDistSimMessageUndeliverable: If the destination is not in the network.
        """
        logger.debug(f"Sending message from {repr(message.source)} to {destination}.")
        if destination in self.nodes():
            destination.push_to_inbox(message)
        else:
            raise PyDistSimMessageUndeliverable("Destination not in network.", message)

    def get_size(self):
        """Returns network width and height based on nodes positions."""
        return max(list(self.pos.values()), axis=0) - min(
            list(self.pos.values()), axis=0
        )

    def get_dic(self):
        """
        Return all network data in the form of a dictionary.

        :return: A dictionary containing the network data.
        :rtype: dict
        """
        algorithms = {
            "%d %s"
            % (ind, alg.name): (
                "active" if alg == self.algorithms[self.algorithmState["index"]] else ""
            )
            for ind, alg in enumerate(self.algorithms)
        }
        pos = {
            n: "x: %.2f y: %.2f theta: %.2f deg"
            % (self.pos[n][0], self.pos[n][1], self.ori[n] * 180.0 / pi)
            for n in self.nodes_sorted()
        }
        return {
            "nodes": pos,  # A dictionary mapping node IDs to their positions in the network.
            "algorithms": algorithms,  # A dictionary mapping algorithm names to their status (active or not).
            "algorithmState": {
                "name": (  # The name of the current algorithm.
                    self.get_current_algorithm().name
                    if self.get_current_algorithm()
                    else ""
                ),
                "step": self.algorithmState[  # The current step of the algorithm.
                    "step"
                ],
                "finished": self.algorithmState[  # Whether the algorithm has finished or not.
                    "finished"
                ],
            },
        }

    def get_tree_net(self, treeKey):
        """
        Returns a new network with edges that are not in a tree removed.

        :param treeKey: The key in the nodes' memory that defines the tree. It can be a list of tree neighbors or a dictionary with 'parent' (node) and 'children' (list) keys.
        :type treeKey: str

        :return: A new network object with only the edges that are part of the tree.
        :rtype: Network

        The tree is defined in the nodes' memory under the specified treeKey. The method iterates over all nodes in the network and checks if the treeKey is present in their memory. If it is, it retrieves the tree neighbors or children and adds the corresponding edges to the tree_edges_ids list. It also adds the tree nodes to the tree_nodes list.

        After iterating over all nodes, a subnetwork is created using the tree_nodes. Then, the method removes any edges from the subnetwork that are not present in the tree_edges_ids list.

        Finally, the resulting subnetwork, representing the tree, is returned.
        """
        tree_edges_ids = []
        tree_nodes = []
        for node in self.nodes_sorted():
            neighbors_in_tree = []
            if treeKey not in node.memory:
                continue
            if isinstance(node.memory[treeKey], list):
                neighbors_in_tree = node.memory[treeKey]
            elif (
                isinstance(node.memory[treeKey], dict)
                and "children" in node.memory[treeKey]
            ):
                neighbors_in_tree = node.memory[treeKey]["children"]
            tree_edges_ids.extend(
                [
                    (node.id, neighbor.id)
                    for neighbor in neighbors_in_tree
                    if neighbor in self.nodes()
                ]
            )
            tree_nodes.extend(
                neighbor for neighbor in neighbors_in_tree if neighbor in self.nodes()
            )
            if tree_nodes:
                tree_nodes.append(node)

        treeNet = self.subnetwork(tree_nodes)
        for u, v in treeNet.edges():
            if (u.id, v.id) not in tree_edges_ids and (
                v.id,
                u.id,
            ) not in tree_edges_ids:
                treeNet.remove_edge(u, v)
        return treeNet

    def validate_params(self, params):
        """
        Validate if given network params match its real params.

        :param params: A dictionary containing the network parameters to validate.
        :type params: dict

        :raises AssertionError: If any of the network parameters do not match the real parameters.
        """
        logger.info("Validating params")
        count = params.get("count", None)  #  for unit tests
        if count:
            if isinstance(count, list):
                assert len(self) in count
            else:
                assert len(self) == count
        n_min = params.get("n_min", 0)
        n_max = params.get("n_max", Inf)
        assert len(self) >= n_min and len(self) <= n_max
        for param, value in list(params.items()):
            if param == "connected":
                assert not value or is_connected(self)
            elif param == "degree":
                assert allclose(self.avg_degree(), value, atol=settings.DEG_ATOL)
            elif param == "environment":
                assert self.environment.__class__ == value.__class__
            elif param == "channelType":
                assert self.channelType.__class__ == value.__class__
            elif param == "comm_range":
                for node in self:
                    assert node.commRange == value
            elif param == "sensors":
                compositeSensor = CompositeSensor(Node(), value)
                for node in self:
                    assert all(
                        map(
                            lambda s1, s2: pydistsim_equal_objects(s1, s2),
                            node.sensors,
                            compositeSensor.sensors,
                        )
                    )
            elif param == "aoa_pf_scale":
                for node in self:
                    for sensor in node.sensors:
                        if sensor.name() == "AoASensor":
                            assert sensor.probabilityFunction.scale == value
            elif param == "dist_pf_scale":
                for node in self:
                    for sensor in node.sensors:
                        if sensor.name() == "DistSensor":
                            assert sensor.probabilityFunction.scale == value
            # TODO: refactor this part as setting algorithms resets nodes
            """
                elif param=='algorithms':
                    alg = self._algorithms
                    self.algorithms = value
                    assert(all(map(lambda a1, a2: pydistsim_equal_objects(a1, a2),
                                   alg, self.algorithms)))
                    #restore alg
                    self._algorithms = alg
                """


class PyDistSimMessageUndeliverable(Exception):
    def __init__(self, e, message):
        self.e = e
        self.message = message

    def __str__(self):
        return self.e + repr(self.message)


class NetwkErrorMsg(StrEnum):
    ALGORITHM = (
        "Algorithms must be in tuple (AlgorithmClass,)"
        " or in form: ((AlgorithmClass, params_dict),)."
        "AlgorithmClass should be subclass of Algorithm"
    )
    NODE = "Node is already in another network."
    NODE_SPACE = "Given position is not free space."
    NODE_NOT_IN_NET = "Node not in network."
    ALGORITHM_NOT_FOUND = "Algorithm not found in network."


class PyDistSimNetworkError(Exception):

    def __init__(self, type_):
        if isinstance(type_, NetwkErrorMsg):
            self.message = type_.value
        else:
            self.message = "Unknown error."

    def __str__(self):
        return self.message
