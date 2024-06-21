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

        # Asigna el algoritmo
        self.net.algorithms = ((Flood, {"informationKey": "greet"}),)

        # Asigna el mensaje a enviar, la información inicial
        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = HELLO

    def test_broadcast(self):
        sim = Simulation(self.net)
        first_algo = sim.network._algorithms[0]
        last_algo = sim.network._algorithms[-1]

        first_algo.check_restrictions()

        for node in self.net.nodes():
            if node == self.initiator:
                assert node.memory["greet"] == HELLO
            else:
                assert "greet" not in node.memory

        sim.run(1)

        first_algo.check_algorithm_initialization()

        sim.run(100_000)

        last_algo.check_algorithm_termination()

        for node in self.net.nodes():
            self.assertEqual(node.memory["greet"], HELLO)


class TestBroadcastConcatenated(PyDistSimTestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100, directed=False)
        self.net = net_gen.generate_random_network()

        # Asigna el algoritmo
        self.net.algorithms = (
            (Flood, {"informationKey": "greet"}),
            (Flood, {"informationKey": "bye"}),
        )

        # Asigna el mensaje a enviar, la información inicial
        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = HELLO

        self.initiator2 = self.net.nodes_sorted()[-1]
        self.initiator2.memory["bye"] = BYE

    def test_broadcast(self):
        sim = Simulation(self.net)
        first_algo = sim.network._algorithms[0]
        last_algo = sim.network._algorithms[-1]

        first_algo.check_restrictions()

        for node in self.net.nodes():
            with self.subTest(node=node):
                if node == self.initiator:
                    assert node.memory["greet"] == HELLO
                    assert "bye" not in node.memory
                elif node == self.initiator2:
                    assert "greet" not in node.memory
                    assert node.memory["bye"] == BYE
                else:
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
