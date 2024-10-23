from collections.abc import Iterable
from copy import deepcopy
from math import inf as Inf
from random import choices
from typing import TYPE_CHECKING

from networkx import (
    DiGraph,
    Graph,
    draw_networkx_edges,
    draw_networkx_labels,
    draw_networkx_nodes,
    is_connected,
    is_strongly_connected,
)
from numpy import allclose, array, average, max, min, pi
from numpy.random import rand

from pydistsim._exceptions import MessageUndeliverableException, NetworkException
from pydistsim.gui import drawing as draw
from pydistsim.logging import logger
from pydistsim.network.behavior import NetworkBehaviorModel
from pydistsim.network.environment import Environment, Environment2D
from pydistsim.network.node import Node
from pydistsim.network.sensor import CompositeSensor
from pydistsim.observers import NodeObserver, ObserverManagerMixin
from pydistsim.utils.helpers import pydistsim_equal_objects, with_typehint

if TYPE_CHECKING:
    from pydistsim.message import Message


class NetworkMixin(ObserverManagerMixin, with_typehint(Graph)):
    """
    Mixin to extend Graph and DiGraph. The result represents a network in a distributed simulation.

    The Network classes (:class:`Network` and :class:`BidirectionalNetwork`) extend the Graph class and provides additional functionality
    for managing nodes and network properties.

    :param environment: The environment in which the network operates. If not provided, a new Environment instance will be created.
    :type environment: Environment, optional
    :param graph: The graph representing the network topology. Defaults to None.
    :type graph: NetworkX graph, optional
    :param kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        incoming_graph_data=None,  # Correct subclassing of Graph
        environment: Environment | None = None,
        behavioral_properties: NetworkBehaviorModel | None = None,
        **kwargs,
    ):
        super().__init__(incoming_graph_data)
        self._environment = environment or Environment2D()
        self.pos = {}
        self.ori = {}
        self.labels = {}
        self.simulation = None
        self.behavioral_properties = behavioral_properties or NetworkBehaviorModel.UnorderedCommunication
        logger.trace("Instance of Network has been initialized.")

    #### Overriding methods from Graph and DiGraph ####

    @staticmethod
    def to_directed_class():
        return Network

    @staticmethod
    def to_undirected_class():
        return BidirectionalNetwork

    def copy(self, as_view=False):
        """
        Return a copy of the graph. Parameters as_view is not used and is only for compatibility with NetworkX.

        :param as_view: Unused parameter. Defaults to False.
        :type as_view: bool, optional
        :return: A deepcopy of the graph.
        :rtype: NetworkMixin
        """
        return deepcopy(self)

    def __deepcopy__(self, memo, nodes=None, edges=None, init_args=None, cls=None):
        """
        Deepcopy the network.

        :param memo: A dictionary that maps object ids to the copied objects.
        :type memo: dict
        :param nodes: A list of nodes to include in the deepcopy. Defaults to None.
        :type nodes: Iterable[Node], optional
        :param edges: A list of edges to include in the deepcopy. Defaults to None.
        :type edges: Iterable[tuple[Node, Node]], optional
        :param init_args: A dictionary of additional arguments to pass to the constructor of the copied network. Defaults to None.
        :type init_args: dict, optional
        :param cls: The class to use for the copied network. Defaults to None.
        :type cls: type, optional
        """
        if id(self) in memo:
            return memo[id(self)]

        new_network = (cls or type(self))(**(init_args or {}))
        memo[id(self)] = new_network

        # Immutable attributes
        new_network._environment = self._environment
        new_network.behavioral_properties = self.behavioral_properties

        nodes = nodes or self.nodes()
        edges = edges or self.edges()

        nodes_copy = {node: deepcopy(node, memo) for node in nodes}
        for node, copy_node in nodes_copy.items():
            copy_node.network = None
            new_network.add_node(
                copy_node,
                pos=deepcopy(self.pos[node], memo),
                ori=deepcopy(self.ori[node], memo),
            )

        for u, v in edges:
            if u not in nodes or v not in nodes:
                continue
            new_network.add_edge(nodes_copy[u], nodes_copy[v])
        new_network.simulation = deepcopy(self.simulation, memo)

        new_network.clear_observers()
        return new_network

    def remove_node(self, node: "Node", skip_check=False):
        """
        Remove a node from the network.

        :param node: The node to be removed.
        :type node: Node
        :raises NetworkException: If the node is not in the network.
        """
        if not skip_check and node not in self.nodes():
            logger.error("Node not in network")
            raise NetworkException(NetworkException.ERRORS.NODE_NOT_IN_NET)
        super().remove_node(node)
        del self.pos[node]
        del self.labels[node]
        node.network = None
        logger.debug("Node with id {} is removed.", node._internal_id)

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
            raise NetworkException(NetworkException.ERRORS.NODE)

        node.network = self

        pos = pos if pos is not None else self._environment.find_random_pos(n=100)
        ori = ori if ori is not None else rand() * 2 * pi
        while ori > 2 * pi:
            ori -= 2 * pi

        if not self._environment.is_space(pos):
            logger.error("Given position is not free space.")
            raise NetworkException(NetworkException.ERRORS.NODE_SPACE)

        super().add_node(node)
        self.pos[node] = array(pos)
        self.ori[node] = ori
        self.labels[node] = str(node._internal_id)
        logger.debug("Node {} is placed on position {}.", node._internal_id, pos)
        self._copy_observers_to_nodes(node)
        return node

    def nodes(self, *args, **kwargs) -> Iterable["Node"]:
        return super().nodes(*args, **kwargs)

    #### Network attribute management ####

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

    def reset(self, log=True):
        """
        Reset the network to its initial state.

        Does not reset the observers of the network nor the observers of the nodes.
        """
        logger.debug("Resetting network.")
        self.reset_all_nodes()

    def reset_all_nodes(self):
        """
        Reset all nodes in the network.

        :return: None
        """
        logger.debug("Resetting all nodes.")
        for node in self.nodes():
            node.reset()

            for other_node in self.out_neighbors(node):
                if node != other_node:
                    self.get_transit_messages(node, other_node).clear()
                    self.get_lost_messages(node, other_node).clear()

    #### Network methods ####

    def is_connected(self):
        if self.is_directed():
            return is_strongly_connected(self)
        return is_connected(self)

    def subnetwork(
        self,
        nodes: list[Node],
        edges: None | Iterable[tuple[Node, Node]] = None,
    ):
        """
        Returns a Network instance with the specified nodes and edges.

        :param nbunch: A list of nodes to include in the subnetwork.
        :type nbunch: list[Node]
        :param edges: A list of edges to include in the subnetwork. Defaults to None.
        :type edges: Iterable[tuple[Node, Node]], optional
        :return: A Network instance representing the subnetwork.
        :rtype: Network
        """

        return self.__deepcopy__({}, nodes, edges)

    def get_tree_net(self, tree_key, return_subnetwork=True):
        """
        Returns a new network with edges that are not in a tree removed.

        The tree is defined in the nodes' memory under the specified tree_key. The method iterates over all nodes in the network and checks if the tree_key is present in their memory. If it is, it retrieves the tree neighbors or children and adds the corresponding edges to the tree_edges_ids list. It also adds the tree nodes to the tree_nodes list.

        After iterating over all nodes, a subnetwork is created using the tree_nodes. Then, the method removes any edges from the subnetwork that are not present in the tree_edges_ids list.

        Finally, the resulting subnetwork, representing the tree, is returned.

        :param tree_key: The key in the nodes' memory that defines the tree. It can be a list of tree neighbors or a dictionary with 'parent' (node) and 'children' (list) keys.
        :type tree_key: str
        :return: A new network object with only the edges that are part of the tree.
        :param return_subnetwork: Whether to return a new network or the sets of nodes and edges. Defaults to True.
        :type return_subnetwork: bool, optional
        :rtype: NetworkMixin
        """
        tree_edges = []
        tree_nodes = []
        for node in self.nodes():
            neighbors_in_tree = []
            if tree_key not in node.memory:
                continue
            if isinstance(node.memory[tree_key], list):
                neighbors_in_tree = node.memory[tree_key]
            elif isinstance(node.memory[tree_key], dict):
                if "children" in node.memory[tree_key]:
                    neighbors_in_tree += [n.unbox() for n in node.memory[tree_key]["children"]]
                if "parent" in node.memory[tree_key] and node.memory[tree_key]["parent"] is not None:
                    neighbors_in_tree.append(node.memory[tree_key]["parent"].unbox())

            tree_edges.extend([(node, neighbor) for neighbor in neighbors_in_tree if neighbor in self.neighbors(node)])
            tree_nodes.extend(neighbor for neighbor in neighbors_in_tree if neighbor in self.neighbors(node))
            if neighbors_in_tree:
                tree_nodes.append(node)

        if not return_subnetwork:
            return tree_nodes, tree_edges

        treeNet = self.subnetwork(tree_nodes, tree_edges)

        return treeNet

    def nodes_sorted(self) -> list["Node"]:
        """
        Returned sorted nodes by id.

        :return: A sorted tuple of nodes.
        :rtype: list[Node]
        """
        return sorted(self.nodes(), key=lambda k: k._internal_id)

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
            if n._internal_id == id_:
                return n

        logger.error("Network has no node with id {}.", id_)
        raise NetworkException(NetworkException.ERRORS.NODE_NOT_IN_NET)

    def avg_degree(self):
        """
        Calculate the average degree of the network.
        Uses out_degree for directed networks (amount of outgoing edges) and degree for undirected networks.

        :return: The average degree of the network.
        :rtype: float
        """
        degree_iter = self.out_degree() if self.is_directed() else self.degree()
        return average(tuple(map(lambda x: x[1], tuple(degree_iter))))

    def out_neighbors(self, node: "Node") -> set["Node"]:
        if self.is_directed():
            return set(self.successors(node))
        return set(self.neighbors(node))

    def in_neighbors(self, node: "Node") -> set["Node"]:
        if self.is_directed():
            return set(self.predecessors(node))
        return set(self.neighbors(node))

    def increment_node_clocks(self):
        """
        Increment the clock of all nodes in the network.

        Follows the clock increment function defined in the behavioral properties.

        :return: None
        """
        for node in self.nodes():
            node.clock += self.behavioral_properties._get_clock_increment(node)

    #### Node communication methods ####

    def get_transit_messages(self, u: "Node", v: "Node") -> dict["Message", int]:
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

        in_transit_messages = self.get_transit_messages(u, v)
        in_transit_messages[message] = delay

    def get_lost_messages(self, u: "Node", v: "Node") -> list["Message"]:
        """
        Get lost messages from node u to node v.

        :param u: The source node.
        :type u: Node
        :param v: The destination node.
        :type v: Node
        :return: A list of lost messages from node u to node v.
        :rtype: list[Message]
        """
        if "lost_messages" not in self[u][v]:
            self[u][v]["lost_messages"] = []
        return self[u][v]["lost_messages"]

    def add_lost_message(self, u: "Node", v: "Node", message: "Message"):
        """
        Add a message to the lost messages from node u to node v.

        :param u: The source node.
        :type u: Node
        :param v: The destination node.
        :type v: Node
        :param message: The message
        :type message: Message
        """
        self.get_lost_messages(u, v).append(message)

    def communicate(self):
        """
        Pass all messages from node's outboxes to its neighbors inboxes.

        This method collects messages from each node's outbox and delivers them to the appropriate destination.
        If the message is a broadcast, it is sent to all neighbors.
        If the message has a specific next hop, it is sent directly to that node.
        If the message has a specific destination, it is sent to that neighbor if it is reachable.

        :return: None
        """
        logger.debug("Communicating messages in the network.")

        if len(self) == 0:
            return

        transmission_complete: list["Message"] = []

        # Process messages in outboxes
        for node in self.nodes():
            # reversed to process messages in the order they were added
            for message in reversed(node.outbox.copy()):
                next_dest: "Node" = message.destination
                node.outbox.remove(message)

                if self.behavioral_properties._should_lose(self, message):
                    logger.trace("Message lost: {}", message)
                    self.add_lost_message(node, next_dest, message)
                    continue

                self.add_transit_message(
                    node,
                    next_dest,
                    message,
                    self.behavioral_properties._get_delay(self, message),
                )

        # Process messages in transit
        for u, v in self.edges():
            messages_delay = self.get_transit_messages(u, v)
            if not messages_delay:
                continue

            message_ordering = self.behavioral_properties.message_ordering

            # Decrease delay for all messages
            for message in messages_delay:
                messages_delay[message] -= 1

            # Sort messages by id
            messages = sorted(messages_delay.keys(), key=lambda x: x._internal_id)
            if not message_ordering:
                # Artificially create inversions in the message order
                messages = sorted(messages_delay.keys(), key=lambda x: x._internal_id)
                cant_inversions = len(messages) // 4
                artificial_inversions = choices(
                    [(i, j) for i in range(len(messages)) for j in range(len(messages)) if i < j],
                    k=cant_inversions,
                )

                for i, j in artificial_inversions:
                    messages[i], messages[j] = messages[j], messages[i]

            for message in messages:
                if messages_delay[message] > 0 and message_ordering:
                    # When a delayed message is found, only process the rest if there is no message ordering.
                    # This is to ensure that the messages are processed in order, even if a previous message is delayed.
                    break
                if messages_delay[message] <= 0:
                    transmission_complete.append(message)
                    messages_delay.pop(message)

        for message in transmission_complete:
            logger.trace("Communicating message: {}", message)

            if message.destination is not None:
                # Destination is neighbor
                if message.source in self and message.destination in self.neighbors(
                    message.source
                ):  # for DiGraph, `self.neighbors` are the out-neighbors
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

    #### Visualization methods ####

    def show(self, *args, **kwargs):
        """
        Get and show the figure object representing the network visualization.

        :param args: Additional positional arguments to pass to the draw function.
        :param kwargs: Additional keyword arguments to pass to the draw function.
        :return: The figure object representing the network visualization.
        :rtype: matplotlib.figure.Figure
        """
        fig = self.get_fig(*args, **kwargs)
        fig.show()
        return fig

    def savefig(self, fname="network.png", figkwargs={}, *args, **kwargs):
        self.get_fig(*args, **kwargs).savefig(fname, **figkwargs)

    def get_fig(self, *args, **kwargs):
        """
        Get the figure object representing the network visualization.

        :param args: Additional positional arguments to pass to the draw function.
        :param kwargs: Additional keyword arguments to pass to the draw function.
        :return: The figure object representing the network visualization.
        :rtype: matplotlib.figure.Figure
        """
        return draw.draw_current_state(
            self,
            *args,
            **kwargs,
        )

    def get_size(self):
        """Returns network width and height based on nodes positions."""
        return max(list(self.pos.values()), axis=0) - min(list(self.pos.values()), axis=0)

    def get_dic(self):
        """
        Return all network data in the form of a dictionary.

        :return: A dictionary containing the network data.
        :rtype: dict
        """
        pos = {
            n: f"x: {self.pos[n][0]:.2f} y: {self.pos[n][1]:.2f} theta: {self.ori[n] * 180.0 / pi:.2f} deg"
            for n in self.nodes_sorted()
        }
        edges = [(x_node._internal_id, y_node._internal_id) for x_node, y_node in self.edges()]
        return {
            "nodes": pos,  # A dictionary mapping nodes to their positions in the network.
            "edges": edges,  # A list of pairs (id1, id2) representing the edges by node id.
        }

    #### Test helper methods ####

    def validate_params(self, params: dict):
        """
        Validate if given network params match its real params.

        :param params: A dictionary containing the network parameters to validate.
        :type params: dict

        :raises AssertionError: If any of the network parameters do not match the real parameters.
        """
        logger.info("Validating params...")
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
                assert allclose(self.avg_degree(), value, atol=1)
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
