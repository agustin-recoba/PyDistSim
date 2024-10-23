import unittest
from random import uniform

from pydistsim.demo_algorithms.santoro2007.mega_merger.algorithm import (
    ExampleParameters,
    MegaMergerAlgorithm,
)
from pydistsim.network import NetworkGenerator
from pydistsim.network.behavior import NetworkBehaviorModel
from pydistsim.simulation import Simulation


def t_net(net):
    # Numerical parameters: city names and weights are integers
    par = ExampleParameters.numerical_parameters.copy()

    # Randomize the parameters
    par.update({"percentage_of_initiators": uniform(0.1, 1)})

    # Create the simulation object
    sim = Simulation(net, ((MegaMergerAlgorithm, par),))

    # Run the simulation
    sim.run()

    assert all(node.status in MegaMergerAlgorithm.S_term for node in net)
    assert len({node.memory["city"].name for node in sim.network.nodes()}) == 1
    assert len({node for node in sim.network.nodes() if node.status == MegaMergerAlgorithm.Status.ELECTED}) == 1


class TestMegaMerger(unittest.TestCase):

    def test_run(self):
        ### Ring network
        for n in [1, 10, 30]:
            net = NetworkGenerator.generate_ring_network(n)
            net.behavioral_properties = NetworkBehaviorModel.RandomDelayCommunication
            t_net(net)
            print(f"Test passed for ring network with {n} nodes.")

        print("\nAll tests passed for ring networks with 1, 10, 40 and 100 nodes.\n")

        ### Complete network
        for n in [1, 10, 40, 60]:
            net = NetworkGenerator.generate_complete_network(n)
            net.behavioral_properties = NetworkBehaviorModel.RandomDelayCommunication
            t_net(net)

        print("All tests passed for complete networks with 2 up to 35 nodes.\n")

        ### Square mesh/grid network
        for n in range(2, 6):
            n = n * n

            net = NetworkGenerator.generate_mesh_network(n)
            net.behavioral_properties = NetworkBehaviorModel.RandomDelayCommunication
            t_net(net)
            print(f"Test passed for square mesh network with {n} nodes.")

        print("\nAll tests passed for square mesh networks with 4 up to 121 nodes.\n")

        ### Path network (`1 x n` grid)
        for n in range(2, 30):
            net = NetworkGenerator.generate_mesh_network(a=1, b=n)
            net.behavioral_properties = NetworkBehaviorModel.RandomDelayCommunication
            t_net(net)
            if n % 10 == 0:
                print(f"Test passed for path network with {n} nodes.")

        print("\nAll tests passed for path networks with 1 up to 50 nodes.\n")

        ### Star network
        for n in range(2, 20):
            net = NetworkGenerator.generate_star_network(n)
            net.behavioral_properties = NetworkBehaviorModel.RandomDelayCommunication
            t_net(net)
            if n % 10 == 0:
                print(f"Test passed for star network with {n} nodes.")

        print("\nAll tests passed for star networks with 2 up to 44 nodes.\n")
