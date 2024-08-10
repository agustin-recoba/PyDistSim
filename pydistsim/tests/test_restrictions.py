# flake8: noqa: E731

from pydistsim.message import Message
from pydistsim.network import NetworkGenerator
from pydistsim.network.behavior import NetworkBehaviorModel
from pydistsim.network.network import Network
from pydistsim.restrictions.communication import (
    BidirectionalLinks,
    MessageOrdering,
    ReciprocalCommunication,
)
from pydistsim.restrictions.knowledge import InitialDistinctValues, NetworkSize
from pydistsim.restrictions.reliability import TotalReliability
from pydistsim.restrictions.time import (
    BoundedCommunicationDelays,
    SimultaneousStart,
    SynchronizedClocks,
    UnitaryCommunicationDelays,
)
from pydistsim.restrictions.topological import (
    CompleteGraph,
    Connectivity,
    CycleGraph,
    StarGraph,
    TreeGraph,
    UniqueInitiator,
)
from pydistsim.utils.testing import PyDistSimTestCase


class TestRestrictions(PyDistSimTestCase):

    def test_TotalReliability(self):
        net = NetworkGenerator(10).generate_random_network()

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=None,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=True,
        )

        net.behavioral_properties = behavior
        assert TotalReliability.check(net)

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=False,
        )

        net.behavioral_properties = behavior
        assert not TotalReliability.check(net)

    def test_MessageOrdering(self):
        net = NetworkGenerator(10).generate_random_network()

        behavior = NetworkBehaviorModel(
            message_ordering=True,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=False,
        )

        net.behavioral_properties = behavior
        assert MessageOrdering.check(net)

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=False,
        )

        net.behavioral_properties = behavior
        assert not MessageOrdering.check(net)

    def test_ReciprocalCommunication(self):
        net = Network()  # directed graph
        n1, n2, n3 = net.add_node(), net.add_node(), net.add_node()

        net.add_edge(n1, n2)
        assert not ReciprocalCommunication.check(net)
        net.add_edge(n2, n1)
        assert ReciprocalCommunication.check(net)

        net.add_edge(n3, n2)
        assert not ReciprocalCommunication.check(net)
        net.add_edge(n3, n1)
        assert not ReciprocalCommunication.check(net)
        net.add_edge(n1, n3)
        assert not ReciprocalCommunication.check(net)
        net.add_edge(n2, n3)

        print(net.nodes_sorted())
        print([e for e in net.edges()])
        assert ReciprocalCommunication.check(net)

        und_net = NetworkGenerator(10, directed=False).generate_random_network()
        assert ReciprocalCommunication.check(und_net)

    def test_BidirectionalLinks(self):
        net = NetworkGenerator(10, directed=False).generate_random_network()
        assert BidirectionalLinks.check(net)

        net = NetworkGenerator(10, directed=True).generate_random_network()
        assert not BidirectionalLinks.check(net)

    def test_InitialDistinctValues(self):
        net = NetworkGenerator(10).generate_random_network()
        InitialDistinctValues.apply(net)
        InitialDistinctValues.check(net)

        for node in net.nodes():
            node.memory[InitialDistinctValues.KEY] = 1
        assert not InitialDistinctValues.check(net)

    def test_NetworkSize(self):
        net = NetworkGenerator(10).generate_random_network()
        NetworkSize.apply(net)
        assert NetworkSize.check(net)

        for node in net.nodes():
            node.memory[NetworkSize.KEY] = 9
        assert not NetworkSize.check(net)

    def test_SynchronizedClocks(self):
        net = NetworkGenerator(10).generate_random_network()

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=None,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=False,
        )

        net.behavioral_properties = behavior
        assert SynchronizedClocks.check(net)

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=False,
        )

        net.behavioral_properties = behavior
        assert not SynchronizedClocks.check(net)

    def test_BoundedCommunicationDelays(self):
        net = NetworkGenerator(10).generate_random_network()

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: 1000,
            bounded_communication_delays=True,
        )

        net.behavioral_properties = behavior
        assert BoundedCommunicationDelays.check(net)

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: float("inf"),
            bounded_communication_delays=False,
        )

        net.behavioral_properties = behavior
        assert not BoundedCommunicationDelays.check(net)

    def test_UnitaryCommunicationDelays(self):
        net = NetworkGenerator(10).generate_random_network()

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=None,
            bounded_communication_delays=True,
        )

        net.behavioral_properties = behavior
        assert UnitaryCommunicationDelays.check(net)

        behavior = NetworkBehaviorModel(
            message_ordering=False,
            message_loss_indicator=lambda network, message: True,
            clock_increment=lambda node: 100,
            message_delay_indicator=lambda network, message: float("inf"),
            bounded_communication_delays=True,
        )

        net.behavioral_properties = behavior
        assert not UnitaryCommunicationDelays.check(net)

    def test_SimultaneousStart(self):
        net = NetworkGenerator(10).generate_random_network()
        assert not SimultaneousStart.check(net)

        for node in net.nodes():
            node.push_to_inbox(Message(meta_header=Message.META_HEADERS.INITIALIZATION_MESSAGE))

        assert SimultaneousStart.check(net)

    def test_Connectivity(self):
        net = NetworkGenerator(10, enforce_connected=True).generate_random_network()
        assert Connectivity.check(net)

        net = Network()
        net.add_node()
        net.add_node()
        assert not Connectivity.check(net)

    def test_UniqueInitiator(self):
        net = NetworkGenerator(10).generate_random_network()

        for node in net.nodes_sorted()[0:2]:
            node.push_to_inbox(Message(meta_header=Message.META_HEADERS.INITIALIZATION_MESSAGE))

        assert not UniqueInitiator.check(net)

        net = NetworkGenerator(10).generate_random_network()

        node = net.nodes_sorted()[0]
        node.push_to_inbox(Message(meta_header=Message.META_HEADERS.INITIALIZATION_MESSAGE))

        assert UniqueInitiator.check(net)

    def test_CompleteGraph(self):
        net = Network()

        nodes = [net.add_node() for _ in range(10)]
        for i, n1 in enumerate(nodes):
            for j, n2 in enumerate(nodes):
                if i != j:
                    net.add_edge(n1, n2)

        assert CompleteGraph.check(net)

        net = NetworkGenerator(10).generate_random_network()
        assert not CompleteGraph.check(net)

    def test_CycleGraph(self):
        net = Network()
        LEN = 10
        nodes = [net.add_node() for _ in range(LEN)]
        for i, n1 in enumerate(nodes):
            n2 = nodes[(i + 1) % LEN]
            net.add_edge(n1, n2)

        assert CycleGraph.check(net)

        net = Network()
        nodes = [net.add_node() for _ in range(LEN)]
        for i, n1 in enumerate(nodes[:-2]):
            n2 = nodes[(i + 1) % LEN]
            net.add_edge(n1, n2)

        assert not CycleGraph.check(net)

    def test_TreeGraph(self):
        net = Network()
        n1, n2, n3, n4, n5 = net.add_node(), net.add_node(), net.add_node(), net.add_node(), net.add_node()

        net.add_edge(n1, n2), net.add_edge(n1, n3), net.add_edge(n2, n4), net.add_edge(n2, n5)
        assert TreeGraph.check(net)

        net.add_edge(n3, n4)  # cycle
        assert not TreeGraph.check(net)

    def test_StarGraph(self):
        net = Network()
        n1, n2, n3, n4, n5 = net.add_node(), net.add_node(), net.add_node(), net.add_node(), net.add_node()

        net.add_edge(n1, n2), net.add_edge(n1, n3), net.add_edge(n1, n4)
        assert not StarGraph.check(net)

        net.add_edge(n1, n5)  # missing edge
        assert StarGraph.check(net)

        net.add_edge(n2, n3)  # cycle
        assert not StarGraph.check(net)
