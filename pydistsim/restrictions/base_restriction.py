from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


def abstractclassmethod(method):
    return classmethod(abstractmethod(method))


RestrictionType = Union["CheckableRestriction", "ApplicableRestriction"]
"""
A restriction over a message passing network.

All implemented restrictions are based on "Design and Analysis of Distributed Algorithms" by Nicola Santoro.
"""


class CheckableRestriction(ABC):
    """
    Model a checkable restriction over a message passing network.
    """

    @abstractclassmethod
    def check(cls, network: "NetworkType") -> bool: ...


class ApplicableRestriction(ABC):
    """
    A restriction that can be applied to a network.

    This is a separate class from :class:`Restriction` to allow for restrictions that are not checkable.
    """

    @abstractclassmethod
    def apply(self, network: "NetworkType") -> None: ...
