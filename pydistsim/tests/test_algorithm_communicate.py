# flake8: noqa: E731

import unittest
from typing import TYPE_CHECKING

from pydistsim.message import Message
from pydistsim.network import NetworkGenerator
from pydistsim.network.behavior import NetworkBehaviorModel

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType
    from pydistsim.network.node import Node

CANT_MESSAGES = 100


# all messages are sent
def all_sent(source: "Node", dest: "Node", network: "NetworkType"):
    return len(source.outbox) == 0


# some but not all messages are received
def only_some_received(source: "Node", dest: "Node", network: "NetworkType"):
    return len(dest.inbox) > 0 and len(dest.inbox) < CANT_MESSAGES


# all messages are received
def all_received(source: "Node", dest: "Node", network: "NetworkType"):
    return len(dest.inbox) == CANT_MESSAGES


def none_received(source: "Node", dest: "Node", network: "NetworkType"):
    return len(dest.inbox) == 0


# inbox is ordered by data in message
def assert_order(source: "Node", dest: "Node", network: "NetworkType"):
    return dest.inbox == sorted(dest.inbox, key=(lambda x: x.data), reverse=True)


# inbox is unordered
def assert_unordered(source: "Node", dest: "Node", network: "NetworkType"):
    return dest.inbox != sorted(dest.inbox, key=(lambda x: x.data), reverse=True)


# none in transit
def none_in_transit(source: "Node", dest: "Node", network: "NetworkType"):
    return len(network.get_transit_messages(source, dest)) + len(network.get_transit_messages(dest, source)) == 0


def all_in_transit(source: "Node", dest: "Node", network: "NetworkType"):
    return len(network.get_transit_messages(source, dest)) == CANT_MESSAGES


# some in transit
def some_in_transit(source: "Node", dest: "Node", network: "NetworkType"):
    return len(network.get_transit_messages(source, dest)) > 0


def delay_only_first_message(network: "NetworkType", message: "Message"):
    if hasattr(network, "first_message_sent") and network.first_message_sent:
        return 0
    network.first_message_sent = True
    return 100


DelayOnlyFirstMessage = NetworkBehaviorModel(
    message_ordering=True,
    message_delay_indicator=delay_only_first_message,
    bounded_communication_delays=True,
    message_loss_indicator=None,
    clock_increment=None,
)


class TestBehaviorModel(unittest.TestCase):
    TESTS = {
        NetworkBehaviorModel.LikelyRandomLossCommunication: (
            "LikelyRandomLossCommunication",
            [all_sent, only_some_received, assert_order, none_in_transit],
        ),
        NetworkBehaviorModel.IdealCommunication: (
            "IdealCommunication",
            [all_sent, all_received, assert_order, none_in_transit],
        ),
        NetworkBehaviorModel.UnorderedCommunication: (
            "UnorderedCommunication",
            [all_sent, all_received, assert_unordered, none_in_transit],
        ),
        NetworkBehaviorModel.RandomDelayCommunication: (
            "RandomDelayCommunication",
            [all_sent, assert_order, some_in_transit],
        ),
        NetworkBehaviorModel.UnorderedRandomDelayCommunication: (
            "UnorderedRandomDelayCommunication",
            [all_sent, only_some_received, assert_unordered, some_in_transit],
        ),
        DelayOnlyFirstMessage: (
            "DelayOnlyFirstMessage",
            [all_sent, none_received, assert_order, all_in_transit],
        ),
    }

    def test(self):
        for comm_props, (name, tests) in self.TESTS.items():
            with self.subTest(comm_props=comm_props):
                net = NetworkGenerator(2, enforce_connected=True).generate_random_network()

                node_source = net.nodes_sorted()[0]
                node_dest = net.nodes_sorted()[1]
                for i in range(1, CANT_MESSAGES + 1):
                    message = Message(
                        source=node_source,
                        destination=node_dest,
                        data=i,
                    )
                    node_source.push_to_outbox(message, destination=node_dest)

                print(f"Running tests for {name}")
                net.behavioral_properties = comm_props
                net.communicate()

                def data_messages(messages):
                    return tuple(map(lambda x: x.data, messages))

                # Prints for debugging

                print(f"node_dest.outbox={data_messages(node_dest.outbox)}")
                print(f"node_dest.inbox={data_messages(node_dest.inbox)}")
                print(f"transit_messages={data_messages(net.get_transit_messages(node_source, node_dest))}")
                print(f"lost_messages={data_messages(net.get_lost_messages(node_source, node_dest))}")

                print(f"{len(node_dest.outbox)=}")
                print(f"{len(node_dest.inbox)=}")
                print(f"{len(net.get_transit_messages(node_source, node_dest))=}")
                print(f"{len(net.get_lost_messages(node_source, node_dest))=}")

                for test in tests:
                    assert test(node_source, node_dest, net)
