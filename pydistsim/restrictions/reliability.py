"""
Restrictions related to reliability, faults, and their detection.
"""

from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.restrictions.base_restriction import CheckableRestriction

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class ReliabilityRestriction(CheckableRestriction, ABC):
    """
    Base class for restrictions related to reliability.
    """


class EdgeFailureDetection(ReliabilityRestriction):
    """
    Whether or not all entities in the network are able to detect a fail in one of its edges and, following the
    failure, detect if it was reactivated.

    In this context, a failure is a temporary loss of the ability to send messages over an edge. Not to be confused with
    delay or a message loss, even though a failure might cause these effects.

    *TODO*: Edge failures are not implemented by the simulation.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError("ToDo: implement dynamic edge failure and optional detection")


class EntityFailureDetection(ReliabilityRestriction):
    """
    For all nodes x in the network,  all in- and out-neighbors of x can detect whether x has failed and, following its
    failure, whether it has recovered.

    In this context, a failure is a temporary loss of the ability of a node to react to events.

    *TODO*: Entity failures are not implemented by the simulation.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        raise NotImplementedError("ToDo: implement dynamic entity failure and optional detection")


class TotalReliability(ReliabilityRestriction):
    """
    A totally fault-free system.

    Neither have any failures occurred nor will they occur.

    *TODO*: Entity failures are not implemented by the simulation.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return (
            network.behavioral_properties.message_loss_indicator is None
        )  # No message loss. Entity failures are not implemented.


class PartialReliability(ReliabilityRestriction):
    """
    No failures will occur.

    Under this restriction, protocols do not need to take failures into account. Note
    that under PartialReliability, failures might have occurred before the execution of a
    computation.

    *TODO*: The simulation does not support partial reliability so this is the same as TotalReliability.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return TotalReliability.check(network)  # The simulation does not support partial reliability (yet)


class GuaranteedDelivery(ReliabilityRestriction):
    """
    Any message that is sent will be received with its content uncorrupted.

    *TODO*: Implement optional message corruption. this only checks for message loss.
    """

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.behavioral_properties.message_loss_indicator is None  # Check only no message loss (for now)
