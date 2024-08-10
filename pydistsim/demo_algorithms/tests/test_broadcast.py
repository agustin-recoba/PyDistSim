from pydistsim.demo_algorithms.broadcast import Flood
from pydistsim.network import NetworkGenerator
from pydistsim.simulation import Simulation
from pydistsim.utils.testing import PyDistSimTestCase

HELLO = "Hello distributed world"
BYE = "Bye bye distributed world"


class TestBroadcastSimple(PyDistSimTestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100, directed=False)
        self.net = net_gen.generate_random_network()
        self.sim = Simulation(self.net)
        self.sim.algorithms = ((Flood, {"informationKey": "greet", "initial_information": HELLO}),)

    def test_broadcast(self):
        sim = self.sim
        algo = sim.algorithms[0]

        for node in self.net.nodes():
            assert "greet" not in node.memory

        sim.run(1)

        algo.check_algorithm_initialization()

        sim.run(100_000)

        algo.check_algorithm_termination()

        for node in self.net.nodes():
            self.assertEqual(node.memory["greet"], HELLO)


class TestBroadcastConcatenated(PyDistSimTestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100, directed=False)
        self.net = net_gen.generate_random_network()
        self.sim = Simulation(self.net)
        self.sim.algorithms = (
            (Flood, {"informationKey": "greet", "initial_information": HELLO}),
            (Flood, {"informationKey": "bye", "initial_information": BYE}),
        )
        # Asigna el mensaje a enviar, la información inicial
        self.initiator = self.net.nodes_sorted()[0]

    def test_broadcast(self):
        sim = self.sim
        first_algo = sim.algorithms[0]
        last_algo = sim.algorithms[-1]

        for node in self.net.nodes():
            with self.subTest(node=node):
                assert "greet" not in node.memory
                assert "bye" not in node.memory

        sim.run(1)

        first_algo.check_algorithm_initialization()

        sim.run(100_000)

        last_algo.check_algorithm_termination()

        for node in self.net.nodes():
            with self.subTest(node=node):
                self.assertEqual(node.memory["greet"], HELLO)
                self.assertEqual(node.memory["bye"], BYE)
