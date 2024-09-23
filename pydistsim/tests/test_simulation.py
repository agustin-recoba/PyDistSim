import unittest
from copy import deepcopy

from pydistsim._exceptions import SimulationException
from pydistsim.algorithm import NetworkAlgorithm, NodeAlgorithm
from pydistsim.network import NetworkGenerator
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
        self.algorithms = (UnimplementedNodeAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net)
        sim.algorithms = self.algorithms

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node._internal_id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
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
                print(f"{node._internal_id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert len(node.outbox) == 0
                nodes_with_1_msg += 1 if len(node.inbox) else 0
        assert nodes_with_1_msg == 1

        assert not sim.is_halted()

        sim.run_step()
        # Second step should process the INI message (and do nothing)

        assert all([len(node.outbox) == 0 for node in self.net.nodes()])
        assert all([len(node.inbox) == 0 for node in self.net.nodes()])

        assert sim.is_halted()

    def test_get_current_algorithm(self):
        """Test getting current algorithm."""
        sim = Simulation(self.net)
        sim.algorithms = ()

        with self.assertRaises(SimulationException):
            sim.get_current_algorithm()

        sim.algorithms = (NodeAlgorithm,)


class TestRunNetworkAlgorithm(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.algorithms = (ImplementedNetworkAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net)
        sim.algorithms = self.algorithms

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node._internal_id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert "test" not in node.memory

        sim.run(1)

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node._internal_id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert node.memory["test"] == "test"

        assert sim.is_halted()


class TestRunNotImplementedNetworkAlgorithm(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.algorithms = (NetworkAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net)
        sim.algorithms = self.algorithms

        with self.assertRaises(NotImplementedError):
            sim.run(100_000)

        assert sim.is_halted()


class TestResetNetwork(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net1 = net_gen.generate_random_network()
        self.sim1 = Simulation(self.net1)
        self.sim1.algorithms = (UnimplementedNodeAlgorithm,)

        self.net2 = net_gen.generate_random_network()
        self.sim2 = Simulation(self.net2)
        self.sim2.algorithms = (ImplementedNetworkAlgorithm,)

    def test_set_network(self):
        assert isinstance(self.sim1.get_current_algorithm(), UnimplementedNodeAlgorithm)
        assert isinstance(self.sim2.get_current_algorithm(), ImplementedNetworkAlgorithm)

        assert self.sim1.network == self.net1
        assert self.net1.simulation == self.sim1

        self.sim1.network = self.net2

        assert self.sim1.network == self.net2
        assert self.net2.simulation == self.sim1
        assert self.net1.simulation is None

    def test_deepcopy(self):
        sim_copy = deepcopy(self.sim1)

        assert sim_copy is not self.sim1
        assert sim_copy.network is not self.sim1.network
        assert len(sim_copy.network) == len(self.net1)
        assert len(sim_copy.network.edges()) == len(self.net1.edges())
        assert isinstance(sim_copy.network, type(self.net1))
        assert len(sim_copy.algorithms) == len(self.sim1.algorithms)
        assert all(
            isinstance(copy_algo, type(og_algo))
            for copy_algo, og_algo in zip(sim_copy.algorithms, self.sim1.algorithms)
        )
