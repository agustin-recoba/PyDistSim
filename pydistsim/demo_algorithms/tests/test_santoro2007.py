import unittest
from typing import TYPE_CHECKING

from pydistsim import NetworkGenerator, Simulation
from pydistsim.demo_algorithms.santoro2007.traversal import DFT, DFStar
from pydistsim.demo_algorithms.santoro2007.yoyo import YoYo
from pydistsim.network.rangenetwork import BidirectionalRangeNetwork
from pydistsim.utils.testing import PyDistSimTestCase

if TYPE_CHECKING:
    from pydistsim.network.node import Node


class TestYoYo(PyDistSimTestCase):

    def test_santoro2007(self):
        node_range = 100
        nets = [
            [(100, 100)],
            [(100, 100), (175, 250), (250, 175), (100, 250), (175, 175), (100, 175)],
            [
                (100, 100),
                (150, 200),
                (175, 175),
                (175, 100),
                (250, 175),
                (250, 250),
                (325, 250),
                (325, 325),
                (325, 400),
            ],
        ]

        for i, node_positions in enumerate(nets, start=1):
            with self.subTest(i=i):
                net = BidirectionalRangeNetwork()
                for node_pos in node_positions:
                    net.add_node(pos=node_pos, commRange=node_range)

                name = "Special %d" % i

                sim = Simulation(net)
                sim.algorithms = (YoYo,)

                sim.run(1)

                sim.algorithms[0].check_algorithm_initialization()

                sim.run(100_000)

                sim.algorithms[0].check_algorithm_termination()

                min_id = min(sim.network.nodes(), key=lambda node: node._internal_id)._internal_id
                for node in sim.network.nodes():
                    if node._internal_id != min_id:
                        # Check if every other node is PRUNED
                        assert node.status == YoYo.Status.PRUNED, "%s: Node %d has status %s, not PRUNED" % (
                            name,
                            node._internal_id,
                            node.status,
                        )
                    else:
                        # Check if the node with the smallest ID is the LEADER
                        assert node.status == YoYo.Status.LEADER, "%s: Node %d has status %s, not LEADER" % (
                            name,
                            node._internal_id,
                            node.status,
                        )

    def test_santoro2007_random(self):
        N_ITERS = 1
        N_NETWORKS = 15
        N_NODES_STEP = 5

        for i in range(N_ITERS):
            for n_nodes in range(N_NODES_STEP, N_NETWORKS * N_NODES_STEP + N_NODES_STEP, N_NODES_STEP):
                with self.subTest(i=i, n_nodes=n_nodes):
                    net_gen = NetworkGenerator(n_nodes, directed=False)
                    net = net_gen.generate_random_network()

                    name = " %d, %d nodes" % (i, n_nodes)

                    sim = Simulation(net)
                    sim.algorithms = (YoYo,)

                    sim.run(1)

                    sim.algorithms[0].check_restrictions()
                    sim.algorithms[0].check_algorithm_initialization()

                    sim.run(100_000)

                    sim.algorithms[0].check_algorithm_termination()

                    min_id = min(sim.network.nodes(), key=lambda node: node._internal_id)._internal_id
                    for node in sim.network.nodes():
                        if node._internal_id == min_id:
                            # Check if the node with the smallest ID is the LEADER
                            assert node.status == YoYo.Status.LEADER, "%s: Node %d has status %s, not LEADER" % (
                                name,
                                node._internal_id,
                                node.status,
                            )
                        else:
                            # Check if every other node is PRUNED
                            assert node.status == YoYo.Status.PRUNED, "%s: Node %d has status %s, not PRUNED" % (
                                name,
                                node._internal_id,
                                node.status,
                            )


class TestTraversalDFT(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100, directed=False)
        self.net = net_gen.generate_random_network()

        self.visited = []

        # Asigna el algoritmo

        def visitedAction(node: "Node"):
            self.visited.append(node.unbox()._internal_id)

        self.algorithms = ((DFT, {"visitedAction": visitedAction}),)

    def test_traversal(self):
        sim = Simulation(self.net)
        sim.algorithms = self.algorithms

        sim.run(100_000)

        for node in self.net.nodes():
            assert node.status == DFT.Status.DONE, "Node %d is not DONE" % node._internal_id

        assert sorted(node._internal_id for node in self.net.nodes()) == sorted(self.visited)


class TestTraversalDFStar(PyDistSimTestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100, directed=False)
        self.net = net_gen.generate_random_network()

        self.visited = []

        # Asigna el algoritmo

        def visitedAction(node: "Node"):
            self.visited.append(node.unbox()._internal_id)

        self.algorithms = ((DFStar, {"visitedAction": visitedAction}),)

    def test_traversal(self):
        sim = Simulation(self.net)
        sim.algorithms = self.algorithms

        sim.run(100_000)

        for node in self.net.nodes():
            assert node.status == DFStar.Status.DONE, "Node %d is not DONE" % node._internal_id

        assert sorted(node._internal_id for node in self.net.nodes()) == sorted(self.visited)
