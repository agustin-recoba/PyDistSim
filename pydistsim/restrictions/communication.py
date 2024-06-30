"""
Restrictions related to communication among entities/nodes.

These restrictions are related to the communication topology of the underlying graph of the network.
"""

from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base_restriction import CheckableRestriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class CommunicationRestriction(CheckableRestriction, ABC):
    """
    Base class for restrictions related to communication among entities.
    """


class MessageOrdering(CommunicationRestriction):
    """
    In the absence of failure, the messages transmitted by an entity
    to the same out-neighbor will arrive in the same order they are sent.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.behavioral_properties.message_ordering


class ReciprocalCommunication(CommunicationRestriction):
    """
    For all nodes, the set of out-neighbors is the same as the set of in-neighbors.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        """
        True if the network is undirected or the set of out-neighbors is the same as the set of in-neighbors.
        """
        return not network.is_directed() or all(
            set(network.in_neighbors(node)) == set(network.out_neighbors(node)) for node in network.nodes()
        )


class BidirectionalLinks(ReciprocalCommunication):
    """
    Even if ReciprocalCommunication holds, one node may not know which out-edges correspond
    to which in-edges. ReciprocalCommunication combined with such knowledge is modeled by
    this restriction.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return not network.is_directed()
