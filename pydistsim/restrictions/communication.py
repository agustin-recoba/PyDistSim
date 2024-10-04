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

    help_message = (
        "Message ordering is disabled. Choose a value for `network.behavioral_properties` such that `message_ordering` "
        "is True.\nThe property NetworkBehaviorModel.RandomDelayCommunication should be a good example."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.behavioral_properties.message_ordering


class ReciprocalCommunication(CommunicationRestriction):
    """
    For all nodes, the set of out-neighbors is the same as the set of in-neighbors.
    """

    help_message = "The network is not reciprocal. All nodes should have the same set of out-neighbors and "
    "in-neighbors. You may want to use an undirected network or transform the network to be reciprocal (add the "
    "missing edges)."

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

    help_message = (
        "The network can't be directed. Please check the documentation of the network generation method and its "
        "parameters to ensure that the network is undirected."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return not network.is_directed()
