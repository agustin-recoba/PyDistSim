import unittest

from pymote.algorithms.broadcast import Flood
from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation

HELLO = "Hello distributed world"
BYE = "Bye bye distributed world"


class TestBroadcastSimple(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()

        # Asigna el algoritmo
        self.net.algorithms = ((Flood, {"informationKey": "greet"}),)

        # Asigna el mensaje a enviar, la información inicial
        self.initiator = self.net.nodes()[0]
        self.initiator.memory["greet"] = HELLO

    def test_broadcast(self):
        sim = Simulation(self.net)

        for node in self.net.nodes():
            if node == self.initiator:
                assert node.memory["greet"] == HELLO
            else:
                assert "greet" not in node.memory

        sim.run()

        for node in self.net.nodes():
            self.assertEqual(node.memory["greet"], HELLO)


class TestBroadcastConcatenated(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()

        # Asigna el algoritmo
        self.net.algorithms = (
            (Flood, {"informationKey": "greet"}),
            (Flood, {"informationKey": "bye"}),
        )

        # Asigna el mensaje a enviar, la información inicial
        self.initiator = self.net.nodes()[0]
        self.initiator.memory["greet"] = HELLO

        self.initiator2 = self.net.nodes()[-1]
        self.initiator2.memory["bye"] = BYE

    def test_broadcast(self):
        sim = Simulation(self.net)

        for node in self.net.nodes():
            with self.subTest(node=node):
                if node == self.initiator:
                    assert node.memory["greet"] == HELLO
                elif node == self.initiator2:
                    assert node.memory["bye"] == BYE
                else:
                    assert "greet" not in node.memory
                    assert "bye" not in node.memory

        sim.run()

        for node in self.net.nodes():
            with self.subTest(node=node):
                self.assertEqual(node.memory["greet"], HELLO)
                self.assertEqual(node.memory["bye"], BYE)
