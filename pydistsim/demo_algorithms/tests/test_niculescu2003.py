import unittest

from pydistsim.demo_algorithms.niculescu2003.dvhop import DVHop
from pydistsim.demo_algorithms.niculescu2003.trilaterate import Trilaterate
from pydistsim.network import NetworkGenerator
from pydistsim.network.sensor import TruePosSensor
from pydistsim.simulation import Simulation


class TestNiculescu2003(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100, directed=False)
        self.net = net_gen.generate_random_network()
        self.algorithms = (
            (DVHop, {"truePositionKey": "tp", "hopsizeKey": "hs", "dataKey": "I"}),
            (
                Trilaterate,
                {
                    "truePositionKey": "tp",
                    "hopsizeKey": "hs",
                    "positionKey": "pos",
                    "dataKey": "I",
                },
            ),
        )
        for node in self.net.nodes_sorted()[:10]:
            node.compositeSensor = (TruePosSensor,)

    def test_niculescu2003_sim(self):
        """Test niculescu2003 default simulation."""
        sim = Simulation(self.net)
        sim.algorithms = self.algorithms
        sim.run(100_000)
        for node in self.net.nodes():
            self.assertTrue(len(node.memory.get("pos", [None, None])) == 2 or "tp" in node.memory)
