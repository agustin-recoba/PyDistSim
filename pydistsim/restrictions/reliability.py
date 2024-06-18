from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base import Restriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class ReliabilityRestriction(Restriction, ABC):
    """
    Restrictions related to reliability, faults, ant their detection.
    """


class EdgeFailureDetection(ReliabilityRestriction):
    """
    Wheather or not all entities in the network are able to detect a fail in one of its edges and, following the
    failure, detect if it was reactivated.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        # TODO: implement dynamic edge failure and optional detection
        raise NotImplementedError


class EntityFailureDetection(ReliabilityRestriction):
    """
    For all nodes x in the network,  all in- and out-neighbors of x can detect whether x has failed and, following its
    failure, whether it has recovered.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        # TODO: implement dynamic entity failure and optional detection
        raise NotImplementedError


class TotalReliability(ReliabilityRestriction):
    """
    A totally fault-free system.

    Neither have any failures occurred nor will they occur.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        raise NotImplementedError


class PartialReliability(ReliabilityRestriction):
    """
    No failures will occur.

    Under this restriction, protocols do not need to take failures into account. Note
    that under PartialReliability, failures might have occurred before the execution of a
    computation.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        raise NotImplementedError


class GuaranteedDelivery(ReliabilityRestriction):
    """
    Any message that is sent will be received with its content uncorrupted.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        # TODO: implement optional dynamic message corruption
        raise NotImplementedError
