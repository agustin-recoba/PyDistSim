"""
Restrictions relating to `a priori` knowledge of the network.
"""

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
    Base class for restrictions relating to `a priori` knowledge of the network.
    """


class InitialDistinctValues(KnowledgeRestriction, ApplicableRestriction):
    """
    The initial node id values are distinct.
    """

    KEY = "unique_value"

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return len({node.memory.get(cls.KEY, None) for node in network}) == len(network)

    @classmethod
    def apply(cls, network: "NetworkType") -> None:
        for node in network.nodes():
            node.memory[cls.KEY] = node._internal_id

    @classmethod
    def get_help_message(cls, network: "NetworkType") -> str:
        if all(cls.KEY in node.memory for node in network):
            return (
                f"The initial values at `node.memory['{cls.KEY}']` are not distinct for every node.\n"
                + cls.help_message
            )
        else:
            return f"The key '{cls.KEY}' is not present in the memory of every node.\n" + cls.help_message


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

    @classmethod
    def get_help_message(cls, network: "NetworkType") -> str:
        if all(cls.KEY in node.memory for node in network):
            return (
                f"The initial values at `node.memory['{cls.KEY}']` are not equal to {len(network)} for every node.\n"
                + cls.help_message
            )
        else:
            return f"The key '{cls.KEY}' is not present in the memory of every node.\n" + cls.help_message
