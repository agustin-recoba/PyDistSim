from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base_restriction import Restriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class ReliabilityRestriction(Restriction, ABC):
    """
    Restrictions related to reliability, faults, ant their detection.
    """


class EdgeFailureDetection(ReliabilityRestriction):
    """
    Whether or not all entities in the network are able to detect a fail in one of its edges and, following the
    failure, detect if it was reactivated.

    In this context, a failure is a temporary loss of the ability to send messages over an edge. Not to be confused with
    delay or a message loss, even though a failure might cause these effects.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        # TODO: implement dynamic edge failure and optional detection
        raise NotImplementedError


class EntityFailureDetection(ReliabilityRestriction):
    """
    For all nodes x in the network,  all in- and out-neighbors of x can detect whether x has failed and, following its
    failure, whether it has recovered.

    In this context, a failure is a temporary loss of the ability of a node to react to events.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        # TODO: implement dynamic entity failure and optional detection
        raise NotImplementedError


class TotalReliability(ReliabilityRestriction):
    """
    A totally fault-free system.

    Neither have any failures occurred nor will they occur.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return (
            network.communication_properties.message_loss_indicator is None
        )  # No message loss. Entity failures are not implemented.


class PartialReliability(ReliabilityRestriction):
    """
    No failures will occur.

    Under this restriction, protocols do not need to take failures into account. Note
    that under PartialReliability, failures might have occurred before the execution of a
    computation.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise TotalReliability.check(network)  # The simulation does not support partial reliability (yet)


class GuaranteedDelivery(ReliabilityRestriction):
    """
    Any message that is sent will be received with its content uncorrupted.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        # TODO: implement optional message corruption
        raise network.communication_properties.message_loss_indicator is None  # Check only no message loss (for now)
