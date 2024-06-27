from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base_restriction import (
    ApplicableRestriction,
    CheckableRestriction,
)

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class KnowledgeRestriction(CheckableRestriction, ABC):
    """
    Restrictions relating to `a priori` knowledge of the network.
    """


class InitialDistinctValues(KnowledgeRestriction, ApplicableRestriction):
    """
    The initial node id values are distinct.
    """

    KEY = "unique_value"

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return {node.memory.get(cls.KEY, None) for node in network} == {node.id for node in network}

    @classmethod
    def apply(cls, network: "NetworkType") -> None:
        for node in network.nodes():
            node.memory[cls.KEY] = node.id


class NetworkSize(KnowledgeRestriction, ApplicableRestriction):
    """
    The size of the network is known.
    """

    KEY = "network_node_count"

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        network_size = len(network)
        return all(node.memory.get(cls.KEY, -1) == network_size for node in network)

    @classmethod
    def apply(cls, network: "NetworkType") -> None:
        for node in network.nodes():
            node.memory[cls.KEY] = len(network)
