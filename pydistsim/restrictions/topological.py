from abc import ABC
from typing import TYPE_CHECKING

from networkx import connected_components, is_tree

from pydistsim.message import Message, MetaHeader
from pydistsim.restrictions.base_restriction import Restriction
from pydistsim.utils.helpers import len_is_not_zero, len_is_one

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class TopologicalRestriction(Restriction, ABC):
    """
    Restrictions related to the communication topology of the underlying graph of the network.
    """


class Connectivity(TopologicalRestriction):
    """
    The communication topology if strongly connected.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.is_connected()


StrongConnectivity = Connectivity
"Type alias to emphasize that strong connectivity is what's checked."


class UniqueInitiator(TopologicalRestriction):
    """
    Only one entity will be able to initiate the algorithm through a spontaneous event.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        def message_is_ini(message: "Message"):
            return message.meta_header == MetaHeader.INITIALIZATION_MESSAGE

        nodes_with_ini = (1 for node in network if len_is_not_zero(filter(message_is_ini, node.inbox)))
        return len_is_one(nodes_with_ini)


class ShapeRestriction(TopologicalRestriction, ABC):
    """
    The communication topology has a specific shape.

    Only the given shape is checked, not the connectivity, even if connectivity is often used with the shape.
    For connectivity, use :class:`Connectivity`.
    """


class CompleteGraph(ShapeRestriction):
    """
    The communication topology is a complete graph.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        N = len(network) - 1
        return not any(
            node in neighbors_of_node or len(neighbors_of_node) != N for node, neighbors_of_node in network.adj.items()
        )


class CycleGraph(ShapeRestriction):
    """
    The communication topology is a cycle.

    Connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return all(len(neighbors_of_node) == 2 for node, neighbors_of_node in network.adj.items()) and len_is_one(
            connected_components(network.to_undirected())
        )


RingGraph = CycleGraph
"Type alias for CycleGraph."


class OrientedCycleGraph(CycleGraph):
    """
    The communication topology is an oriented cycle.

    This means that every node shares the meaning of "left" and "right" with its neighbors.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError


OrientedRingGraph = OrientedCycleGraph
"Type alias for OrientedCycleGraph."


class TreeGraph(ShapeRestriction):
    """
    The communication topology is a tree.

    Connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return is_tree(network)


class StarGraph(ShapeRestriction):
    """
    The communication topology is a star.

    A network is a star if there is a node that is connected to all other nodes and the rest of the nodes are only
    connected to the center node.

    If the network has only one or two nodes, it is considered a star.

    Connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        if len(network) <= 2:
            return True

        N = len(network) - 1
        center_count = 0
        others_count = 0
        for node in network:
            if len(network[node]) == N:
                center_count += 1
                if center_count > 1:
                    return False
            elif len(network[node]) == 1:
                others_count += 1
            else:
                return False

        return center_count == 1 and others_count == N


class HyperCubeGraph(ShapeRestriction):
    """
    The communication topology is a hypercube of any dimension.

    Connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError


class OrientedHyperCubeGraph(HyperCubeGraph):
    """
    The communication topology is an oriented hypercube.

    Details of the definition can be found in section "3.5 ELECTION IN CUBE NETWORKS" of "Design and Analysis of
    Distributed Algorithms" by Nicola Santoro
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError
