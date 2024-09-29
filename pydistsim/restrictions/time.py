"""
This module contains restrictions related to time and how it is handled in the simulation.
"""

from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.message import Message, MetaHeader
from pydistsim.restrictions.base_restriction import (
    ApplicableRestriction,
    CheckableRestriction,
)
from pydistsim.utils.helpers import len_is_not_zero

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class TimeRestriction(CheckableRestriction, ABC):
    """
    Base class for restrictions relating to time.

    In fact, the general model makes no assumption about delays (except that they are finite).
    """


class BoundedCommunicationDelays(TimeRestriction):
    """
    There exists a constant T such that, in the absence of failures, the communication delay of any message on any link
    is at most T.
    """

    help_message = (
        "Delays are not upper bounded. Choose a value for `network.behavioral_properties` such that "
        "`bounded_communication_delays` is True.\n"
        "The property NetworkBehaviorModel.RandomDelayCommunication should be a good example."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.behavioral_properties.bounded_communication_delays


class UnitaryCommunicationDelays(TimeRestriction):
    """
    In the absence of failures, the communication delay of any message on any link is one unit of time.
    """

    help_message = (
        "Delays are not unitary. Choose a value for `network.behavioral_properties` such that "
        "`message_delay_indicator` is `None`.\n"
        "The property NetworkBehaviorModel.UnorderedCommunication should be a good example."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.behavioral_properties.message_delay_indicator is None


class SynchronizedClocks(TimeRestriction):
    """
    All local clocks are incremented by one unit simultaneously and the interval of time between successive increments
    is constant.
    """

    help_message = (
        "Clocks are not synchronized. Choose a value for `network.behavioral_properties` such that "
        "`clock_increment` is `None`.\n"
        "The property NetworkBehaviorModel.IdealCommunication should be a good example."
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        return network.behavioral_properties.clock_increment is None


class SimultaneousStart(TimeRestriction, ApplicableRestriction):
    """
    All nodes start the algorithm at the same time.

    Note that "at the same time" is a given under this simulation model but that does not mean that the nodes are
    synchronized, nor that their messages arrive with the same delay.
    """

    help_message = (
        "Not every node starts at the beginning. Try inserting a`INITIALIZATION_MESSAGE` in the inbox of every node.\n"
        + ApplicableRestriction.help_message
    )

    @classmethod
    def check(cls, network: "NetworkType") -> bool:
        def message_is_ini(message: "Message"):
            return message.meta_header == MetaHeader.INITIALIZATION_MESSAGE

        nodes_with_ini = (node for node in network if len_is_not_zero(filter(message_is_ini, node.inbox)))
        return len(list(nodes_with_ini)) == len(network)

    @classmethod
    def apply(self, network: "NetworkType") -> None:
        for node in network.nodes():
            node.push_to_inbox(Message(meta_header=MetaHeader.INITIALIZATION_MESSAGE, destination=node))
