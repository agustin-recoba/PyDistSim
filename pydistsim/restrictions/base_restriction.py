"""
Base classes for restrictions over message passing networks.

All restrictions are based on "Design and Analysis of Distributed Algorithms" by Nicola Santoro.

There are two types of restrictions: checkable and applicable. Checkable restrictions can be checked for a network,
while applicable restrictions can be applied to a network. Sometimes, an applicable restriction may check itself.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


def abstractclassmethod(method):
    return classmethod(abstractmethod(method))


class Restriction(ABC):
    """
    Base class for all restrictions over a message passing network.
    """


class CheckableRestriction(Restriction, ABC):
    """
    Base class for checkable restrictions over a message passing network.
    """

    @abstractclassmethod
    def check(cls, network: "NetworkType") -> bool: ...

    @classmethod
    def get_help_message(cls, network: "NetworkType") -> str:
        return cls.help_message


class ApplicableRestriction(Restriction, ABC):
    """
    Base class for restrictions that can be applied to a network.

    This is a separate class from :class:`Restriction` to allow for restrictions that are not checkable.
    """

    help_message: str = (
        "The easiest fix would be adding the line `self.apply_restrictions()` to the initializer method of the "
        "algorithm."
    )

    @abstractclassmethod
    def apply(self, network: "NetworkType") -> None: ...
