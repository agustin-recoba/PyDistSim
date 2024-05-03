import unittest

from pymote import Network, NetworkGenerator, Simulation
from pymote.algorithms.santoro2007.yoyo import YoYo


class TestSantoro2007(unittest.TestCase):

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
                net = Network()
                for node_pos in node_positions:
                    net.add_node(pos=node_pos, commRange=node_range)

                name = "Special %d" % i

                net.algorithms = (YoYo,)
                sim = Simulation(net, logLevel="WARNING")
                sim.run()

                min_id = min(sim.network.nodes(), key=lambda node: node.id).id
                for node in sim.network.nodes():
                    if node.id != min_id:
                        # Check if every other node is PRUNED
                        assert (
                            node.status == YoYo.Status.PRUNED
                        ), "%s: Node %d has status %s, not PRUNED" % (
                            name,
                            node.id,
                            node.status,
                        )
                    else:
                        # Check if the node with the smallest ID is the LEADER
                        assert (
                            node.status == YoYo.Status.LEADER
                        ), "%s: Node %d has status %s, not LEADER" % (
                            name,
                            node.id,
                            node.status,
                        )

    def test_santoro2007_random(self):
        N_ITERS = 5
        N_NETWORKS = 15
        N_NODES_STEP = 5

        for i in range(N_ITERS):
            for n_nodes in range(
                N_NODES_STEP, N_NETWORKS * N_NODES_STEP + N_NODES_STEP, N_NODES_STEP
            ):
                with self.subTest(i=i, n_nodes=n_nodes):
                    net_gen = NetworkGenerator(n_nodes)
                    net = net_gen.generate_random_network()

                    name = "Random %d, %d nodes" % (i, n_nodes)

                    net.algorithms = (YoYo,)
                    sim = Simulation(net, logLevel="WARNING")
                    sim.run()

                    min_id = min(sim.network.nodes(), key=lambda node: node.id).id
                    for node in sim.network.nodes():
                        if node.id == min_id:
                            # Check if the node with the smallest ID is the LEADER
                            assert (
                                node.status == YoYo.Status.LEADER
                            ), "%s: Node %d has status %s, not LEADER" % (
                                name,
                                node.id,
                                node.status,
                            )
                        else:
                            # Check if every other node is PRUNED
                            assert (
                                node.status == YoYo.Status.PRUNED
                            ), "%s: Node %d has status %s, not PRUNED" % (
                                name,
                                node.id,
                                node.status,
                            )