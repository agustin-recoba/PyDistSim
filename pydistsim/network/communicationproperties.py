from collections.abc import Callable
from dataclasses import dataclass
from random import randint, uniform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydistsim.message import Message
    from pydistsim.network.network import NetworkType


@dataclass(slots=True, frozen=True)
class CommunicationPropertiesModel:
    "Communication properties for a network."

    message_ordering: bool
    "Boolean indicating if messages should be ordered."

    message_delay_indicator: Callable[["NetworkType", "Message"], int] | None
    "Function that returns the amount of steps to delay a given message. None means no message delay."

    message_loss_indicator: Callable[["NetworkType", "Message"], bool] | None
    "Function that returns a boolean indicating if a given message should be lost. None means no message loss."

    def get_delay(self, network: "NetworkType", message: "Message") -> int:
        "Get the delay for a given message."
        return self.message_delay_indicator(network, message) if self.message_delay_indicator else 0

    def should_lose(self, network: "NetworkType", message: "Message") -> bool:
        "Check if a given message should be lost."
        return self.message_loss_indicator(network, message) if self.message_loss_indicator else False


#### Delay functions ####


def delay_size_network(network: "NetworkType", message: "Message") -> int:
    "Delay every message by the number of nodes in the network."
    return len(network.nodes)


def random_delay_max_size_network(network: "NetworkType", message: "Message") -> int:
    "Delay a message by a random number between 0 and the number of nodes in the network."
    return randint(0, len(network.nodes))


def delay_based_on_network_usage(network: "NetworkType", message: "Message") -> int:
    "Delay a message by the number of pending messages in the network."
    # 30 messages in a 10 node network == 3 steps delay
    return round(sum(len(node.outbox) for node in network.nodes) / len(network.nodes))


#### Loss functions ####


def random_loss(probability_of_loss) -> Callable[["NetworkType", "Message"], bool]:
    "Randomly lose a message with a given probability."

    def _random_loss(network: "NetworkType", message: "Message") -> bool:
        return uniform(0, 1) < probability_of_loss

    return _random_loss


#### Communication properties instances ####
class ExampleProperties:
    "Example communication properties for networks."

    IdealCommunication = CommunicationPropertiesModel(
        message_ordering=True,
        message_delay_indicator=None,
        message_loss_indicator=None,
    )
    "Properties for a network with message ordering, no message loss, and no message delay."

    UnorderedCommunication = CommunicationPropertiesModel(
        message_ordering=False,
        message_delay_indicator=None,
        message_loss_indicator=None,
    )
    "Properties for a network with no message ordering, no message loss, and no message delay."

    ThrottledCommunication = CommunicationPropertiesModel(
        message_ordering=True,
        message_delay_indicator=delay_based_on_network_usage,
        message_loss_indicator=None,
    )
    "Properties for a network with message ordering, no message loss, and a delay based on network usage."

    UnorderedThrottledCommunication = CommunicationPropertiesModel(
        message_ordering=False,
        message_delay_indicator=delay_based_on_network_usage,
        message_loss_indicator=None,
    )
    "Properties for a network with no message ordering, no message loss, and a delay based on network usage."

    RandomDelayCommunication = CommunicationPropertiesModel(
        message_ordering=True,
        message_delay_indicator=random_delay_max_size_network,
        message_loss_indicator=None,
    )
    "Properties for a network with message ordering, no message loss, and a random delay based on the network size."

    UnorderedRandomDelayCommunication = CommunicationPropertiesModel(
        message_ordering=False,
        message_delay_indicator=random_delay_max_size_network,
        message_loss_indicator=None,
    )
    "Properties for a network with no message ordering, no message loss, and a random delay based on the network size."

    UnlikelyRandomLossCommunication = CommunicationPropertiesModel(
        message_ordering=True,
        message_delay_indicator=None,
        message_loss_indicator=random_loss(0.1),
    )
    "Properties for a network with message ordering, a random (but unlikely) message loss, and no message delay."

    LikelyRandomLossCommunication = CommunicationPropertiesModel(
        message_ordering=True,
        message_delay_indicator=None,
        message_loss_indicator=random_loss(0.9),
    )
    "Properties for a network with message ordering, a random (but likely) message loss, and no message delay."
