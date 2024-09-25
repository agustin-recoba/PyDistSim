"""
Restrictions related to the communication topology of the underlying graph of the network.

These restrict some communication properties of the network, such as connectivity, shape, and the number of initiators.
"""

from abc import ABC
from typing import TYPE_CHECKING

from networkx import connected_components, is_tree

from pydistsim.message import Message, MetaHeader
from pydistsim.restrictions.base_restriction import CheckableRestriction
from pydistsim.utils.helpers import len_is_not_zero, len_is_one

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class TopologicalRestriction(CheckableRestriction, ABC):
    """
    Restrictions related to the communication topology of the underlying graph of the network.
    """


class Connectivity(TopologicalRestriction):
    """
    The communication topology if strongly connected.
    """

    help_message = "The network is not strongly connected. Consider adding more edges/links to the network."

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.is_connected()


StrongConnectivity = Connectivity
"Type alias to emphasize that strong connectivity is what's checked."


class UniqueInitiator(TopologicalRestriction):
    """
    Only one entity will be able to initiate the algorithm through a spontaneous event.
    """

    help_message = (
        "There is more than one initiator. Consider checking the algorithm initializer method and how many "
        "times it uses an initialization message (`Message(meta_header=NodeAlgorithm.INI)`)."
    )

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
    For strong connectivity, use :class:`Connectivity`.
    """


class CompleteGraph(ShapeRestriction):
    """
    The communication topology is a complete graph.

    No self-loops are allowed.
    """

    help_message = (
        "The network topology is not 'complete'. Consider adding more edges/links or using "
        "`NetworkGenerator.generate_complete_network(n)` to generate a new network."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        N = len(network) - 1
        return not any(
            node in neighbors_of_node or len(neighbors_of_node) != N for node, neighbors_of_node in network.adj.items()
        )


class CycleGraph(ShapeRestriction):
    """
    The communication topology is a cycle.

    Strong connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    help_message = (
        "The network topology is not a 'cycle'. Consider adding/removing edges or using "
        "`NetworkGenerator.generate_ring_network(n)` to generate a new network."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        network = network.to_undirected()
        return all(len(neighbors_of_node) == 2 for node, neighbors_of_node in network.adj.items()) and len_is_one(
            connected_components(network)
        )


RingGraph = CycleGraph
"Type alias for CycleGraph."


class OrientedCycleGraph(CycleGraph):
    """
    The communication topology is an oriented cycle.

    This means that every node shares the meaning of "left" and "right" with its neighbors.

    *TODO*: This check is not implemented.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError("ToDo: Implement OrientedCycleGraph restriction.")


OrientedRingGraph = OrientedCycleGraph
"Type alias for OrientedCycleGraph."


class TreeGraph(ShapeRestriction):
    """
    The communication topology is a tree.

    Strong connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    help_message = (
        "The network topology is not a 'tree'. Consider adding/removing edges to avoid cycles while also maintaining "
        "connectivity."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return is_tree(network)


class StarGraph(ShapeRestriction):
    """
    The communication topology is a star.

    A network is a star if there is a node that is connected to all other nodes and the rest of the nodes are only
    connected to the center node.

    If the network has only one or two nodes, it is considered a star.

    Strong connectivity is not required as this restriction can be used with :class:`Connectivity`.
    """

    help_message = (
        "The network topology is not a 'star'. Consider adding/removing edges or using "
        "`NetworkGenerator.generate_star_network(n)` to generate a new network."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        def neig(node):
            return len(set(network.in_neighbors(node)) | set(network.out_neighbors(node)))

        if len(network) <= 2:
            return True

        N = len(network) - 1
        center_count = 0
        others_count = 0
        for node in network.nodes():
            if neig(node) == N:
                center_count += 1
                if center_count > 1:
                    return False
            elif neig(node) == 1:
                others_count += 1
            else:
                return False

        return center_count == 1 and others_count == N


class HyperCubeGraph(ShapeRestriction):
    """
    The communication topology is a hypercube of any dimension.

    Strong connectivity is not required as this restriction can be used with :class:`Connectivity`.

    *TODO*: This check is not implemented.
    """

    help_message = (
        "This restriction is not implemented. Remove it from the list of restrictions and make sure the network is "
        "generated with `NetworkGenerator.generate_hypercube_network(n)`."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError("ToDo: Implement HyperCubeGraph restriction.\n" + cls.get_help_message(network))


class OrientedHyperCubeGraph(HyperCubeGraph):
    """
    The communication topology is an oriented hypercube.

    Details of the definition can be found in section "3.5 ELECTION IN CUBE NETWORKS" of "Design and Analysis of
    Distributed Algorithms" by Nicola Santoro

    *TODO*: This check is not implemented.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError("ToDo: Implement OrientedHyperCubeGraph restriction.")
