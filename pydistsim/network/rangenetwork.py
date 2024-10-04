from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional

from numpy import allclose, sign, sqrt
from numpy.random import random

from pydistsim.logging import logger
from pydistsim.network.environment import Environment
from pydistsim.network.network import BidirectionalNetwork, Network
from pydistsim.utils.helpers import with_typehint

if TYPE_CHECKING:
    from pydistsim.network.behavior import NetworkBehaviorModel
    from pydistsim.network.node import Node


class RangeType(ABC):
    """RangeType abstract base class.

    This class represents an abstract base class for different types of channels.
    Subclasses of RangeType should implement the `in_comm_range` method.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def __init__(self, environment: "Environment"):
        self.environment = environment

    @abstractmethod
    def in_comm_range(self, network: "RangeNetworkType", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        This method should be implemented by subclasses to determine if two nodes
        are within communication range.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        ...


class UdgRangeType(RangeType):
    """Unit disc graph range type.

    This class represents the Unit Disc Graph (UDG) channel type. It determines if
    two nodes are within communication range based on their positions and communication
    range.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def in_comm_range(self, network: "RangeNetworkType", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        Two nodes are in communication range if they can see each other and are
        positioned so that their distance is smaller than the communication range.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        p1 = network.pos[node1]
        p2 = network.pos[node2]
        d = sqrt(sum(pow(p1 - p2, 2)))
        if d < node1.commRange and d < node2.commRange:
            if self.environment.are_visible(p1, p2):
                return True
        return False


class CompleteRangeType(RangeType):
    """Complete range type.

    This class represents the Complete channel type. It always returns True,
    indicating that any two nodes are within communication range.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def in_comm_range(self, network: "RangeNetworkType", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        This method always returns True, indicating that any two nodes are within
        communication range.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        return True


class SquareDiscRangeType(RangeType):
    """Square Disc channel type.

    This class represents the Square Disc channel type. It determines if two nodes
    are within communication range based on their positions, communication range,
    and a probability of connection.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def in_comm_range(self, network: "RangeNetworkType", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        Two nodes are in communication range if they can see each other, are positioned
        so that their distance is smaller than the communication range, and satisfy a
        probability of connection.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        p1 = network.pos[node1]
        p2 = network.pos[node2]
        d = sqrt(sum(pow(p1 - p2, 2)))
        if random() > d**2 / node1.commRange**2:
            if self.environment.are_visible(p1, p2):
                assert node1.commRange == node2.commRange
                return True
        return False


class RangeNetworkMixin(with_typehint(Network)):
    """
    Mixin to define a type of network that decides which nodes are connected based on their
    communication range.


    :param environment: The environment in which the network operates. If not provided, a new Environment instance will be created.
    :type environment: Environment, optional
    :param rangeType: The type of channel to be used for communication. If not provided, a new RangeType instance will be created using the environment.
    :type rangeType: RangeType, optional
    :param graph: The graph representing the network topology. Defaults to None.
    :type graph: NetworkX graph, optional
    :param kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        incoming_graph_data=None,
        environment: Optional["Environment"] = None,
        rangeType: RangeType | None = None,
        behavioral_properties: Optional["NetworkBehaviorModel"] = None,
        **kwargs,
    ):
        super().__init__(incoming_graph_data, environment, behavioral_properties, **kwargs)
        self.rangeType = rangeType or UdgRangeType(self._environment)
        self.rangeType.environment = self._environment

    @staticmethod
    def to_directed_class():
        return RangeNetwork

    @staticmethod
    def to_undirected_class():
        return BidirectionalRangeNetwork

    def __deepcopy__(self, memo, nodes=None, edges=None, init_args=None, cls=None):
        init_args = init_args or {}
        init_args["rangeType"] = self.rangeType

        return super().__deepcopy__(memo, nodes, edges, init_args, cls)

    def add_node(self, node=None, pos=None, ori=None, commRange=None):
        node = super().add_node(node, pos, ori, commRange)
        self.recalculate_edges([node])
        return node

    def remove_node(self, node, skip_check=False):
        super().remove_node(node, skip_check)
        self.recalculate_edges()

    def recalculate_edges(self, nodes: Iterable | None = None):
        """
        Recalculate edges for given nodes or for all self.nodes().

        :param nodes: A list of nodes to recalculate edges for. If not provided, edges will be recalculated for all nodes in the network.
        :type nodes: list, optional

        Edge between nodes n1 and n2 are added if both are RangeType.in_comm_range of each other.
        """
        if not nodes:
            nodes = self.nodes()
        for n1 in nodes:
            for n2 in self.nodes():
                if n1 != n2:
                    for x, y in ((n1, n2), (n2, n1)):
                        if self.rangeType.in_comm_range(self, x, y):
                            super().add_edge(x, y)
                        elif self.has_edge(x, y):
                            self.remove_edge(x, y)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """
        Add an edge to the network.

        :param u_of_edge: The source node of the edge.
        :param v_of_edge: The target node of the edge.
        :param attr: Additional attributes to be assigned to the edge.
        """
        logger.warning("Edges are auto-calculated from rangeType and commRange")
        super().add_edge(u_of_edge, v_of_edge, **attr)

    def _set_environment(self, environment: Environment):
        super()._set_environment(environment)
        self.rangeType.environment = environment
        for node in self.nodes_sorted():
            self.remove_node(node, skip_check=True)
            self.add_node(node)
        logger.debug("All nodes are moved into new environment.")

    def validate_params(self, params: dict):
        super().validate_params(params)
        for param, value in params.items():
            if param == "rangeType":
                assert self.rangeType.__class__ == value.__class__
            elif param == "comm_range":
                for node in self:
                    assert node.commRange == value

    def modify_avg_degree(self, value):
        """
        DEPRECATED AND UNTESTED

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
        assert value + 1 > self.avg_degree()  # only increment
        step_factor = 7.0
        steps = [0]
        # TODO: while condition should call validate
        while not allclose(self.avg_degree(), value, atol=1):
            steps.append((value - self.avg_degree()) * step_factor)
            for node in self:
                node.commRange += steps[-1]
            # variable step_factor for step size for over/undershoot cases
            if len(steps) > 2 and sign(steps[-2]) != sign(steps[-1]):
                step_factor /= 2
        logger.trace("Modified degree to {}", self.avg_degree())


class RangeNetwork(RangeNetworkMixin, Network):
    """
    Type of network that decides which nodes are connected based on their communication range.

    Aims to represent a wireless network where nodes can only communicate with each other if they
    are within a certain range.

    Manual edge modification is not recommended. Edges are automatically calculated and any edge
    can be removed by moving the nodes out of communication range or by addition/removal of nodes.
    """


class BidirectionalRangeNetwork(RangeNetworkMixin, BidirectionalNetwork):
    """
    Same as RangeNetwork but with bidirectional edges (undirected graph).
    """


RangeNetworkType = RangeNetwork | BidirectionalRangeNetwork
"Type of network that decides which nodes are connected based on their communication range."
