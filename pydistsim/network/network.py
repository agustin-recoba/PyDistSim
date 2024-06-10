import inspect
from collections.abc import Iterable
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, Optional

from networkx import (
    DiGraph,
    Graph,
    draw_networkx_edges,
    draw_networkx_labels,
    draw_networkx_nodes,
    is_connected,
    is_strongly_connected,
)
from numpy import array, max, min, pi
from numpy.core.numeric import Inf, allclose
from numpy.lib.function_base import average
from numpy.random import rand

from pydistsim.algorithm import BaseAlgorithm
from pydistsim.conf import settings
from pydistsim.logger import logger
from pydistsim.network.communicationproperties import (
    CommunicationPropertiesModel,
    UnorderedCommunication,
)
from pydistsim.network.environment import Environment
from pydistsim.network.exceptions import (
    MessageUndeliverableException,
    NetworkErrorMsg,
    NetworkException,
)
from pydistsim.network.node import Node
from pydistsim.observers import NodeObserver, ObserverManagerMixin
from pydistsim.sensor import CompositeSensor
from pydistsim.utils.helpers import (
    pydistsim_equal_objects,
    sort_by_sortedness,
    with_typehint,
)

if TYPE_CHECKING:
    from pydistsim.algorithm import BaseAlgorithm
    from pydistsim.message import Message

AlgorithmsParam = tuple[type["BaseAlgorithm"] | tuple[type["BaseAlgorithm"], dict]]


class NetworkMixin(ObserverManagerMixin, with_typehint(Graph)):
    """
    Mixin to extend Graph and DiGraph. The result represents a network in a distributed simulation.

    The Network classes (:class:`Network` and :class:`BidirectionalNetwork`) extend the Graph class and provides additional functionality
    for managing nodes, algorithms, and network properties.
    """

    def __init__(
        self,
        incoming_graph_data=None,  # Correct subclassing of Graph
        environment: Environment = None,
        algorithms: AlgorithmsParam = (),
        networkRouting: bool = True,
        communication_properties: CommunicationPropertiesModel | None = None,
        **kwargs,
    ):
        """
        :param environment: The environment in which the network operates. If not provided, a new Environment instance will be created.
        :type environment: Environment, optional
        :param algorithms: The algorithms to be executed on the network. If not provided, the default algorithms defined in settings.ALGORITHMS will be used.
        :type algorithms: AlgorithmsParam, optional
        :param networkRouting: Flag indicating whether network routing is enabled. Defaults to True.
        :type networkRouting: bool, optional
        :param graph: The graph representing the network topology. Defaults to None.
        :type graph: NetworkX graph, optional
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(incoming_graph_data)
        self._environment = environment or Environment()
        self.pos = {}
        self.ori = {}
        self.labels = {}
        self.algorithms = algorithms or settings.ALGORITHMS
        self.algorithmState = {"index": 0, "step": 1, "finished": False}
        self.networkRouting = networkRouting
        self.simulation = None
        self.communication_properties = communication_properties or UnorderedCommunication
        logger.info("Instance of Network has been initialized.")

    #### Overriding methods from Graph and DiGraph ####

    @staticmethod
    def to_directed_class():
        return Network

    @staticmethod
    def to_undirected_class():
        return BidirectionalNetwork

    def copy(self, as_view=False):
        """Return a copy of the graph."""
        return deepcopy(self)

    def remove_node(self, node, skip_check=False):
        """
        Remove a node from the network.

        :param node: The node to be removed.
        :type node: Node
        :raises NetworkException: If the node is not in the network.
        """
        if not skip_check and node not in self.nodes():
            logger.error("Node not in network")
            raise NetworkException(NetworkErrorMsg.NODE_NOT_IN_NET)
        super().remove_node(node)
        del self.pos[node]
        del self.labels[node]
        node.network = None
        logger.debug("Node with id {} is removed.", node.id)

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

        :raises NetworkException: if the given node is already in another network or the given position is not free space

        """
        if not node:
            node = Node(commRange=commRange)

        assert isinstance(node, Node)

        if node.network:
            logger.exception("Node is already in another network, can't add.")
            raise NetworkException(NetworkErrorMsg.NODE)

        node.network = self

        pos = pos if pos is not None else self._environment.find_random_pos(n=100)
        ori = ori if ori is not None else rand() * 2 * pi
        ori = ori % (2 * pi)

        if not self._environment.is_space(pos):
            logger.error("Given position is not free space.")
            raise NetworkException(NetworkErrorMsg.NODE_SPACE)

        super().add_node(node)
        self.pos[node] = array(pos)
        self.ori[node] = ori
        self.labels[node] = str(node.id)
        logger.debug("Node {} is placed on position {}.", node.id, pos)
        self._copy_observers_to_nodes(node)
        return node

    #### Network attribute management ####

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
            raise NetworkException(NetworkErrorMsg.ALGORITHM)
        for algorithm in algorithms:
            if inspect.isclass(algorithm) and issubclass(algorithm, BaseAlgorithm):
                self._algorithms += (algorithm(self),)
            elif (
                isinstance(algorithm, tuple)
                and len(algorithm) == 2
                and issubclass(algorithm[0], BaseAlgorithm)
                and isinstance(algorithm[1], dict)
            ):
                self._algorithms += (algorithm[0](self, **algorithm[1]),)
            else:
                raise NetworkException(NetworkErrorMsg.ALGORITHM)

        # If everything went ok, set algorithms param for coping
        self._algorithms_param = algorithms

    @property
    def environment(self):
        return self._environment

    def _set_environment(self, environment: Environment):
        """
        Setter for environment. Override this method if default
        behavior is not enough.

        :param environment: The new environment for the network.
        :type environment: Environment
        """
        self._environment = environment

    @environment.setter
    def environment(self, environment: Environment):
        self._set_environment(environment)

    def add_observers(self, *observers):
        super().add_observers(*observers)
        self._copy_observers_to_nodes()

    def _copy_observers_to_nodes(self, *nodes):
        if not nodes:
            nodes = self.nodes()

        for node in nodes:
            node.add_observers(
                *(obs for obs in self.observers if isinstance(obs, NodeObserver))
            )  # Register observers to the nodes, too (only if they are NodeNetworkObservers)

    def clear_observers(self):
        super().clear_observers()
        for node in self.nodes():
            node.clear_observers()

    def reset(self):
        """
        Reset the network to its initial state.

        Does not reset the observers of the network nor the observers of the nodes.
        """
        logger.info("Resetting network.")
        self.algorithmState = {"index": 0, "step": 1, "finished": False}
        self.reset_all_nodes()

    def reset_all_nodes(self):
        """
        Reset all nodes in the network.

        :return: None
        """
        logger.info("Resetting all nodes.")
        for node in self.nodes():
            node: "Node"
            node.reset()

    #### Network methods ####

    def is_connected(self):
        if self.is_directed():
            return is_strongly_connected(self)
        return is_connected(self)

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
        H.simulation = None
        H.clear_observers()

        assert isinstance(H, NetworkMixin)
        return H

    def get_tree_net(self, treeKey, downstream_only=False):
        """
        Returns a new network with edges that are not in a tree removed.

        :param treeKey: The key in the nodes' memory that defines the tree. It can be a list of tree neighbors or a dictionary with 'parent' (node) and 'children' (list) keys.
        :type treeKey: str
        :param downstream_only: A flag indicating whether to include only downstream edges in the tree. Defaults to False. Downstream edges are edges from parent to children.
        :type downstream_only: bool

        :return: A new network object with only the edges that are part of the tree. If downstream_only is True, the network is directed.
        :rtype: NetworkMixin

        The tree is defined in the nodes' memory under the specified treeKey. The method iterates over all nodes in the network and checks if the treeKey is present in their memory. If it is, it retrieves the tree neighbors or children and adds the corresponding edges to the tree_edges_ids list. It also adds the tree nodes to the tree_nodes list.

        After iterating over all nodes, a subnetwork is created using the tree_nodes. Then, the method removes any edges from the subnetwork that are not present in the tree_edges_ids list.

        Finally, the resulting subnetwork, representing the tree, is returned.

        """
        tree_edges_ids = []
        tree_nodes = []
        for node in self.nodes():
            print(f"{node.memory=}")
            neighbors_in_tree = []
            if treeKey not in node.memory:
                continue
            if isinstance(node.memory[treeKey], list):
                if downstream_only:
                    raise NetworkException(NetworkErrorMsg.LIST_TREE_DOWNSTREAM_ONLY)
                neighbors_in_tree = node.memory[treeKey]
            elif isinstance(node.memory[treeKey], dict) and "children" in node.memory[treeKey]:
                neighbors_in_tree += node.memory[treeKey]["children"]
                if (
                    not downstream_only
                    and "parent" in node.memory[treeKey]
                    and node.memory[treeKey]["parent"] is not None
                ):
                    neighbors_in_tree.append(node.memory[treeKey]["parent"])

            tree_edges_ids.extend(
                [(node.id, neighbor.id) for neighbor in neighbors_in_tree if neighbor in self.neighbors(node)]
            )
            tree_nodes.extend(neighbor for neighbor in neighbors_in_tree if neighbor in self.neighbors(node))
            if neighbors_in_tree:
                print(f"{node}, {tree_edges_ids=}")
                tree_nodes.append(node)

        treeNet = self.subnetwork(tree_nodes)
        if downstream_only:
            treeNet = treeNet.to_directed()
        for u, v in tuple(treeNet.edges()):
            if (u.id, v.id) not in tree_edges_ids:
                treeNet.remove_edge(u, v)
        return treeNet

    def nodes_sorted(self):
        """
        Sort nodes by id, important for message ordering.

        :param data: A boolean value indicating whether to include node data in the sorted list.
        :type data: bool
        :return: A sorted tuple of nodes.
        :rtype: tuple
        """
        return tuple(sorted(self.nodes(), key=lambda k: k.id))

    def node_by_id(self, id_):
        """
        Returns the first node with the given id.

        :param id_: The id of the node to search for.
        :type id_: int
        :return: The node with the given id.
        :rtype: Node
        :raises NetworkException: If the network does not have a node with the given id.
        """
        for n in self.nodes():
            if n.id == id_:
                return n

        logger.error("Network has no node with id {}.", id_)
        raise NetworkException(NetworkErrorMsg.NODE_NOT_IN_NET)

    def avg_degree(self):
        """
        Calculate the average degree of the network.
        Uses out_degree for directed networks (amount of outgoing edges) and degree for undirected networks.

        :return: The average degree of the network.
        :rtype: float
        """
        degree_iter = self.out_degree() if self.is_directed() else self.degree()
        return average(tuple(map(lambda x: x[1], tuple(degree_iter))))

    #### Node communication methods ####

    def transit_messages(self, u: "Node", v: "Node") -> dict["Message", int]:
        """
        Get messages in transit from node u to node v.

        :param u: The source node.
        :type u: Node
        :param v: The destination node.
        :type v: Node
        :return: A dictionary of messages in transit from node u to node v,
                 with the message as the key and the delay as the value.
        :rtype: Dict[Message, int]
        """
        if "in_transit_messages" not in self[u][v]:
            self[u][v]["in_transit_messages"] = {}
        return self[u][v]["in_transit_messages"]

    def add_transit_message(self, u: "Node", v: "Node", message: "Message", delay: int):
        """
        Add a message to the in-transit messages from node u to node v.

        :param u: The source node.
        :type u: Node
        :param v: The destination node.
        :type v: Node
        :param message: The message
        :type message: Message
        :param delay: The delay of the message
        :type delay: int
        """

        in_transit_messages = self.transit_messages(u, v)
        in_transit_messages[message] = delay

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
        logger.info("Communicating messages in the network.")

        if len(self) == 0:
            return

        transmission_complete: list["Message"] = []

        # Process messages in outboxes
        for node in self.nodes():
            node: "Node"
            for message in node.outbox.copy():
                next_dest = message.nexthop or message.destination
                node.outbox.remove(message)

                if self.communication_properties.message_loss_indicator(self):
                    logger.debug("Message lost: {}", message)
                    continue

                logger.debug("Message delayed: {}", message)
                self.add_transit_message(
                    node, next_dest, message, self.communication_properties.message_delay_indicator(self)
                )
                continue

        # Process messages in transit
        for u, v in self.edges():
            messages_delay = self.transit_messages(u, v)
            message_ordering = self.communication_properties.message_ordering

            # Decrease delay for all messages
            for message in messages_delay:
                messages_delay[message] -= 1

            if message_ordering:
                # Sort messages by id only if message_ordering is enabled
                messages = sorted(messages_delay.keys(), key=lambda x: x.id)
            else:
                # Sort only a little bit if message_ordering is disabled
                messages = sort_by_sortedness(messages_delay.keys(), 0.75, key=lambda x: x.id)

            for message in messages:
                if messages_delay[message] > 0 and message_ordering:
                    # When a delayed message is found, only process the rest if there is no message ordering.
                    # This is to ensure that the messages are processed in order, even if a previous message is delayed.
                    break
                if messages_delay[message] <= 0:
                    transmission_complete.append(message)
                    messages_delay.pop(message)

        for message in transmission_complete:
            logger.debug("Communicating message: {}", message)

            if message.nexthop is not None:
                # Node routing
                try:
                    self.deliver_to(message.nexthop, message)
                except MessageUndeliverableException as e:
                    logger.warning("Routing Message Undeliverable: {}", e.message)
            elif message.destination is not None:
                # Destination is neighbor
                if message.source in self.nodes() and message.destination in self.neighbors(
                    message.source
                ):  # for DiGraph, `self.neighbors` are the out-neighbors
                    self.deliver_to(message.destination, message)
                elif self.networkRouting:
                    # Network routing
                    # TODO: program network routing so it goes hop by hop only
                    #       in connected part of the network
                    self.deliver_to(message.destination, message)
                else:
                    raise MessageUndeliverableException("Can't deliver message.", message)

    def deliver_to(self, destination: "Node", message: "Message"):
        """
        Deliver a message to a destination node in the network.

        :param destination: The destination node to send the message to.
        :type destination: Node
        :param message: The message to be sent.
        :type message: Message
        :raises PyDistSimMessageUndeliverable: If the destination is not in the network.
        """
        logger.debug("Sending message from {} to {}.", message.source, destination)
        if destination in self.nodes():
            destination.push_to_inbox(message)
        else:
            raise MessageUndeliverableException("Destination not in network.", message)

    #### Algorithm relation methods ####

    def get_current_algorithm(self):
        """
        Try to return the current algorithm based on the algorithmState.

        :return: The current algorithm.
        :rtype: BaseAlgorithm or None

        :raises NetworkException: If there are no algorithms defined in the network.
        """
        if len(self.algorithms) == 0:
            logger.error("There is no algorithm defined in the network.")
            raise NetworkException(NetworkErrorMsg.ALGORITHM_NOT_FOUND)

        if self.algorithmState["finished"]:
            if len(self.algorithms) > self.algorithmState["index"] + 1:
                self.algorithmState["index"] += 1
                self.algorithmState["step"] = 1
                self.algorithmState["finished"] = False
            else:
                return None

        return self.algorithms[self.algorithmState["index"]]

    #### Visualization methods ####

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
        fig_size = tuple(array(self._environment.image.shape) / dpi)

        # figsize in inches
        # default matplotlibrc is dpi=80 for plt and dpi=100 for savefig
        fig = plt.figure(figsize=fig_size, dpi=dpi, frameon=False)
        plt.imshow(self._environment.image, cmap="binary_r", vmin=0, origin="lower")
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
        draw_networkx_edges(net, pos, alpha=0.6, edgelist=edgelist)
        draw_networkx_nodes(net, pos, node_size=node_size, node_color=nodeColor, cmap="YlOrRd")
        if show_labels:
            label_pos = {}
            from math import sqrt

            label_delta = sqrt(node_size * 0.6) * dpi / 100
            for n in net.nodes():
                label_pos[n] = pos[n].copy() + label_delta
            draw_networkx_labels(
                net,
                label_pos,
                labels=labels,
                horizontalalignment="left",
                verticalalignment="bottom",
            )
        # plt.axis('off')
        return fig

    def get_size(self):
        """Returns network width and height based on nodes positions."""
        return max(list(self.pos.values()), axis=0) - min(list(self.pos.values()), axis=0)

    def get_dic(self):
        """
        Return all network data in the form of a dictionary.

        :return: A dictionary containing the network data.
        :rtype: dict
        """
        algorithms = {
            "%d %s" % (ind, alg.name): ("active" if alg == self.algorithms[self.algorithmState["index"]] else "")
            for ind, alg in enumerate(self.algorithms)
        }
        pos = {
            n: f"x: {self.pos[n][0]:.2f} y: {self.pos[n][1]:.2f} theta: {self.ori[n] * 180.0 / pi:.2f} deg"
            for n in self.nodes_sorted()
        }
        edges = [(x.id, y.id) for x, y in self.edges()]
        return {
            "nodes": pos,  # A dictionary mapping nodes to their positions in the network.
            "edges": edges,  # A list of pairs (id1, id2) representing the edges by node id.
            "algorithms": algorithms,  # A dictionary mapping algorithm names to their status (active or not).
            "algorithmState": {
                "name": (  # The name of the current algorithm.
                    self.get_current_algorithm().name if self.get_current_algorithm() else ""
                ),
                "step": self.algorithmState["step"],  # The current step of the algorithm.
                "finished": self.algorithmState["finished"],  # Whether the algorithm has finished or not.
            },
        }

    #### Test helper methods ####

    def validate_params(self, params: dict):
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
                assert len(self) in count, f"{len(self)=} not in {count=}"
            else:
                assert len(self) == count, f"{len(self)=} != {count=}"
        n_min = params.get("n_min", 0)
        n_max = params.get("n_max", Inf)
        assert len(self) >= n_min and len(self) <= n_max
        for param, value in params.items():
            if param == "connected":
                assert not value or self.is_connected(), f"{value=}, {self.is_connected()=}"
            elif param == "degree":
                assert allclose(self.avg_degree(), value, atol=settings.DEG_ATOL)
            elif param == "environment":
                assert self.environment.__class__ == value.__class__
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


class Network(NetworkMixin, DiGraph):
    """
    A directed graph representing a network in a distributed simulation.
    """


class BidirectionalNetwork(NetworkMixin, Graph):
    """
    An undirected graph representing a bidirectional network in a distributed simulation.
    """


NetworkType = Network | BidirectionalNetwork
"A network in a distributed simulation."
