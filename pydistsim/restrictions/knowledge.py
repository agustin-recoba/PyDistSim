from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base_restriction import Restriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class KnowledgeRestriction(Restriction, ABC):
    """
    Restrictions relating to `a priori` knowledge of the network.
    """


class InitialDistinctValues(KnowledgeRestriction):
    """
    The initial node id values are distinct.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError


class NetworkSize(KnowledgeRestriction):
    """
    The size of the network is known.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError
