import unittest

from pymote.algorithm import NetworkAlgorithm, NodeAlgorithm
from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation


class UnimplementedNodeAlgorithm(NodeAlgorithm): ...


class ImplementedNetworkAlgorithm(NetworkAlgorithm):

    def run(self):
        for node in self.network.nodes():
            node.memory["test"] = "test"


class TestRunBaseNodeAlgorithm(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = (UnimplementedNodeAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net, "DEBUG")

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert len(node.outbox) == 0
                assert len(node.inbox) == 0

        assert sim.is_halted()

        sim.run_step()
        # First step should transfer the INI from the outbox to the inbox of the initiator node
        assert len(self.net.outbox) == 0

        nodes_with_1_msg = 0
        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert len(node.outbox) == 0
                nodes_with_1_msg += 1 if len(node.inbox) else 0
        assert nodes_with_1_msg == 1

        assert not sim.is_halted()

        sim.run_step()
        # Second step should process the INI message (and do nothing)

        assert sim.is_halted()


class TestRunNetworkAlgorithm(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = (ImplementedNetworkAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net, "DEBUG")

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert "test" not in node.memory

        sim.run_all(True)

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert node.memory["test"] == "test"

        assert sim.is_halted()


class TestRunNotImplementedNetworkAlgorithm(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = (NetworkAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net, "DEBUG")

        with self.assertRaises(NotImplementedError):
            sim.run_all(False)

        assert sim.is_halted()


class TestResetNetwork(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net1 = net_gen.generate_random_network()
        self.net1.algorithms = (UnimplementedNodeAlgorithm,)

        self.net2 = net_gen.generate_random_network()
        self.net2.algorithms = (ImplementedNetworkAlgorithm,)

        self.sim = Simulation(self.net1, "DEBUG")

    def test_set_network(self):
        assert isinstance(self.net1.get_current_algorithm(), UnimplementedNodeAlgorithm)
        assert isinstance(
            self.net2.get_current_algorithm(), ImplementedNetworkAlgorithm
        )

        assert self.sim.network == self.net1
        assert self.net1.simulation == self.sim

        self.sim.network = self.net2

        assert self.sim.network == self.net2
        assert self.net2.simulation == self.sim
        assert self.net1.simulation is None
