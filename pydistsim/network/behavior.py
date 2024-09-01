from collections.abc import Callable
from dataclasses import dataclass
from random import randint, uniform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydistsim.message import Message
    from pydistsim.network.network import NetworkType
    from pydistsim.network.node import Node


@dataclass(slots=True, frozen=True)
class NetworkBehaviorModel:
    """
    Behavioral properties for a network.

    :param message_ordering: Boolean indicating if messages should be ordered. Default is False.
    :param message_loss_indicator: Function that returns a boolean indicating if a given message should be lost.
    Default (None) means no message loss.
    :param clock_increment: Function that returns the increment for the clock of a given node. Default (None) means
    unitary clock increment (sync).
    :param message_delay_indicator: Function that returns the amount of steps to delay a given message. Default (None)
    means no message delay.
    :param bounded_communication_delays: Boolean indicating if there is a predefined constant T such that the
    communication delay of any message on any link is at most T. Default is False.
    """

    message_ordering: bool = False
    "Boolean indicating if messages should be ordered."

    message_loss_indicator: Callable[["NetworkType", "Message"], bool] | None = None
    "Function that returns a boolean indicating if a given message should be lost. None means no message loss."

    clock_increment: Callable[["Node"], int] | None = None
    "Function that returns the increment for the clock of a given node. None means unitary clock increment (sync)."

    message_delay_indicator: Callable[["NetworkType", "Message"], int] | None = None
    "Function that returns the amount of steps to delay a given message. None means no message delay."

    bounded_communication_delays: bool = False
    "If there is a predefined constant T such that the communication delay of any message on any link is at most T."

    def get_delay(self, network: "NetworkType", message: "Message") -> int:
        "Get the delay for a given message."
        return self.message_delay_indicator(network, message) if self.message_delay_indicator else 0

    def should_lose(self, network: "NetworkType", message: "Message") -> bool:
        "Check if a given message should be lost."
        return self.message_loss_indicator(network, message) if self.message_loss_indicator else False

    def get_clock_increment(self, node: "Node") -> int:
        "Get the increment for the clock of a given node."
        return self.clock_increment(node) if self.clock_increment else 1


#### Delay functions ####


def delay_size_network(network: "NetworkType", message: "Message") -> int:
    "Delay every message by the number of nodes in the network."
    return len(network)


def random_delay_max_size_network(network: "NetworkType", message: "Message") -> int:
    "Delay a message by a random number between 0 and the number of nodes in the network."
    return randint(0, len(network))


def delay_based_on_network_usage(network: "NetworkType", message: "Message") -> int:
    "Delay a message by the number of pending messages in the network."
    # 30 messages in a 10 node network == 3 steps delay
    return round(sum(len(node.outbox) for node in network) / len(network))


#### Loss functions ####


def random_loss(probability_of_loss) -> Callable[["NetworkType", "Message"], bool]:
    "Randomly lose a message with a given probability."

    def _random_loss(network: "NetworkType", message: "Message") -> bool:
        return uniform(0, 1) < probability_of_loss

    return _random_loss


#### Clock increments ####


def big_random_increment(node: "Node") -> int:
    "Random increment between 1 and 10."
    return randint(1, 10)


def small_random_increment(node: "Node") -> int:
    "Random increment between 1 and 3."
    return randint(1, 2)


#### Communication properties instances ####
class ExampleProperties:
    "Example communication properties for networks."

    IdealCommunication = NetworkBehaviorModel(
        message_ordering=True,
        message_delay_indicator=None,
        bounded_communication_delays=True,
        message_loss_indicator=None,
        clock_increment=None,
    )
    "Properties for a network with message ordering, no message loss, no message delay and synchronized clocks."

    UnorderedCommunication = NetworkBehaviorModel(
        message_ordering=False,
        message_delay_indicator=None,
        bounded_communication_delays=True,
        message_loss_indicator=None,
        clock_increment=small_random_increment,
    )
    "Properties for a network with no message ordering, no message loss, no message delay and unsynchronized clocks."

    ThrottledCommunication = NetworkBehaviorModel(
        message_ordering=True,
        message_delay_indicator=delay_based_on_network_usage,
        bounded_communication_delays=False,
        message_loss_indicator=None,
        clock_increment=small_random_increment,
    )
    "Properties for a network with message ordering, no message loss, a delay based on network usage and unsynchronized clocks."

    UnorderedThrottledCommunication = NetworkBehaviorModel(
        message_ordering=False,
        message_delay_indicator=delay_based_on_network_usage,
        bounded_communication_delays=False,
        message_loss_indicator=None,
        clock_increment=small_random_increment,
    )
    "Properties for a network with no message ordering, no message loss, a delay based on network usage and unsynchronized clocks."

    RandomDelayCommunication = NetworkBehaviorModel(
        message_ordering=True,
        message_delay_indicator=random_delay_max_size_network,
        bounded_communication_delays=True,
        message_loss_indicator=None,
        clock_increment=small_random_increment,
    )
    "Properties for a network with message ordering, no message loss, random delay based on the network size and unsynchronized clocks."

    UnorderedRandomDelayCommunication = NetworkBehaviorModel(
        message_ordering=False,
        message_delay_indicator=random_delay_max_size_network,
        bounded_communication_delays=True,
        message_loss_indicator=None,
        clock_increment=small_random_increment,
    )
    "Properties for a network with no message ordering, no message loss, random delay based on the network size and unsynchronized clocks."

    UnlikelyRandomLossCommunication = NetworkBehaviorModel(
        message_ordering=True,
        message_delay_indicator=None,
        bounded_communication_delays=True,
        message_loss_indicator=random_loss(0.1),
        clock_increment=small_random_increment,
    )
    "Properties for a network with message ordering, a random (but unlikely) message loss, no message delay and unsynchronized clocks."

    LikelyRandomLossCommunication = NetworkBehaviorModel(
        message_ordering=True,
        message_delay_indicator=None,
        bounded_communication_delays=True,
        message_loss_indicator=random_loss(0.9),
        clock_increment=small_random_increment,
    )
    "Properties for a network with message ordering, a random (but likely) message loss, no message delay and unsynchronized clocks."
