from abc import ABC
from typing import TYPE_CHECKING

from pydistsim.message import Message, MetaHeader
from pydistsim.restrictions.base import Restriction
from pydistsim.utils.helpers import len_is_not_zero

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class TimeRestriction(Restriction, ABC):
    """
    Restrictions relating to time.

    In fact, the general model makes no assumption about delays (except that they are finite).
    """


class BoundedCommunicationDelays(TimeRestriction):
    """
    There exists a constant T such that, in the absence of failures, the communication delay of any message on any link
    is at most T.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        raise NotImplementedError


class UnitaryCommunicationDelays(TimeRestriction):
    """
    In the absence of failures, the communication delay of any message on any link is one unit of time.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        raise NotImplementedError


class SynchronizedClocks(TimeRestriction):
    """
    All local clocks are incremented by one unit simultaneously and the interval of time between successive increments
    is constant.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        raise NotImplementedError


class SimultaneousStart(TimeRestriction):
    """
    All nodes start the algorithm at the same time.
    """

    @classmethod
    def check(cls, network: "NetworkType"):
        def message_is_ini(message: "Message"):
            return message.meta_header == MetaHeader.INITIALIZATION_MESSAGE

        nodes_with_ini = (node for node in network if len_is_not_zero(filter(message_is_ini, node.inbox)))
        return len(nodes_with_ini) == len(network)
