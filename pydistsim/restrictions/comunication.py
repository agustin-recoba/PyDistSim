from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base import Restriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class ComunicationRestriction(Restriction, ABC):
    """
    Restriciton related to communication among entities.
    """


class MessageOrdering(ComunicationRestriction):
    """
    In the absence of failure, the messages transmited by an entity
    to the same out-neighbor will arrive in the same order they are sent.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        return network.communication_properties.message_ordering


class ReciprocalCommunication(ComunicationRestriction):
    """
    For all nodes, the set of out-neighbors is the same as the set of in-neighbors.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        "True if the network is undirected or the set of out-neighbors is the same as the set of in-neighbors."
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
    def check(cls, network: "NetworkType"):
        # TODO: create edge labeling system to ofuscate neighbor knowledge
        raise NotImplementedError
