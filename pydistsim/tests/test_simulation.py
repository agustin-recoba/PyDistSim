import unittest

from pydistsim.algorithm import NetworkAlgorithm, NodeAlgorithm
from pydistsim.networkgenerator import NetworkGenerator
from pydistsim.simulation import Simulation
from pydistsim.utils.testing import PyDistSimTestCase


class UnimplementedNodeAlgorithm(NodeAlgorithm): ...


class ImplementedNetworkAlgorithm(NetworkAlgorithm):

    def run(self):
        for node in self.network.nodes():
            node.memory["test"] = "test"


class TestRunBaseNodeAlgorithm(PyDistSimTestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = (UnimplementedNodeAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net)

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert len(node.outbox) == 0
                assert len(node.inbox) == 0

        assert sim.is_halted()

        sim.run_step()
        # First step should put the INI in the outbox
        assert all(len(node.outbox) == 0 for node in self.net.nodes())
        assert sum(len(node.inbox) for node in self.net.nodes()) == 1

        # Put the INI message in the inbox of a node
        sim.run_step()

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

        assert all([len(node.outbox) == 0 for node in self.net.nodes()])
        assert all([len(node.inbox) == 0 for node in self.net.nodes()])

        assert sim.is_halted()


class TestRunNetworkAlgorithm(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = (ImplementedNetworkAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net)

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert "test" not in node.memory

        sim.run(1)

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
        sim = Simulation(self.net)

        with self.assertRaises(NotImplementedError):
            sim.run()

        assert sim.is_halted()


class TestResetNetwork(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net1 = net_gen.generate_random_network()
        self.net1.algorithms = (UnimplementedNodeAlgorithm,)

        self.net2 = net_gen.generate_random_network()
        self.net2.algorithms = (ImplementedNetworkAlgorithm,)

        self.sim = Simulation(self.net1)

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
