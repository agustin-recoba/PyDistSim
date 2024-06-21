from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


def abstractclassmethod(method):
    return classmethod(abstractmethod(method))


class Restriction(ABC):
    """
    Model a checkable restriction over a message passing network.

    All implemented restrictions are based on "Design and Analysis of Distributed Algorithms" by Nicola Santoro.
    """

    @abstractclassmethod
    def check(cls, network: "NetworkType") -> bool: ...
