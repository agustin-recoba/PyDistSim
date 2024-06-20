import unittest
from inspect import isclass
from math import inf as Inf

from pydistsim.demo_algorithms.readsensors import ReadSensors
from pydistsim.network import NetworkGenerator, NetworkGeneratorException, UdgRangeType
from pydistsim.network.environment import Environment2D
from pydistsim.network.network import NetworkType
from pydistsim.utils.testing import PyDistSimTestCase


class TestNetworkGeneration(PyDistSimTestCase):

    def setUp(self):
        # Raises NetworkGeneratorException
        # returns None
        # else expected network/node properties dictionary
        env = Environment2D(shape=(600, 600))
        rangeType = UdgRangeType(env)
        algorithms = (ReadSensors,)
        self.in_out = [
            (
                "default N_COUNT and COMM_RANGE and ENVIRONMENT should be compatible",
                {
                    "n_count": None,
                    "n_min": 0,
                    "n_max": Inf,
                    "enforce_connected": True,
                    "environment": None,
                    "degree": None,
                    "comm_range": None,
                },
                {"count": list(range(100, 1001))},
            ),
            (
                "regular default params",
                {
                    "n_count": 100,
                    "n_min": 0,
                    "n_max": Inf,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": None,
                    "comm_range": 100,
                },
                {"count": list(range(100, 1001))},
            ),
            ############## connected True degree False
            (
                "increase node number",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": Inf,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": None,
                    "comm_range": 100,
                },
                {"count": list(range(11, 301))},
            ),
            (
                "increase commRange",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 10,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": None,
                    "comm_range": None,
                },
                {"count": 10},
            ),
            (
                "decrease commRange",
                {
                    "n_count": 10,
                    "n_min": 10,
                    "n_max": 10,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": 0,
                    "comm_range": None,
                },
                {"count": 10},
            ),
            ############## connected True degree True
            (
                "increase node number",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 200,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": 11,
                    "comm_range": 100,
                },
                {"count": list(range(10, 201))},
            ),
            (
                "increase commRange",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 10,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": 9,
                    "degree_tolerance": 0.01,
                    "comm_range": None,
                },
                {"count": 10},
            ),
            (
                "low degree with connected, alternating directions problem",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 10,
                    "enforce_connected": True,
                    "environment": env,
                    "degree": 3,
                    "comm_range": 30,
                },
                None,
            ),
            ############## connected False degree True
            (
                "increase node number",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 200,
                    "enforce_connected": False,
                    "environment": env,
                    "degree": 8,
                    "comm_range": 100,
                },
                {"count": list(range(10, 201))},
            ),
            (
                "increase commRange",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 200,
                    "enforce_connected": False,
                    "environment": env,
                    "degree": 11,
                    "comm_range": None,
                },
                {"count": list(range(10, 201))},
            ),
            (
                "low degree",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 100,
                    "enforce_connected": False,
                    "environment": env,
                    "degree": 3,
                    "comm_range": 100,
                },
                {"count": list(range(10, 101))},
            ),
            (
                "degree too high for node number",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 10,
                    "enforce_connected": False,
                    "environment": env,
                    "degree": 10,
                    "comm_range": None,
                },
                NetworkGeneratorException,
            ),
            (
                "",
                {
                    "n_count": 11,
                    "n_min": 0,
                    "n_max": 10,
                    "enforce_connected": False,
                    "environment": env,
                    "degree": None,
                    "comm_range": None,
                },
                NetworkGeneratorException,
            ),
            (
                "",
                {
                    "n_count": 9,
                    "n_min": 10,
                    "n_max": 10,
                    "enforce_connected": False,
                    "environment": env,
                    "degree": None,
                    "comm_range": None,
                },
                NetworkGeneratorException,
            ),
            ############## connected False degree False - no need for modifying initially created network
            # also remove environment from kwargs to test default and change comm_range to commRange
            (
                "",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 100,
                    "enforce_connected": False,
                    "degree": None,
                    "commRange": 100,
                },
                {"count": 10},
            ),
            (
                "",
                {
                    "n_count": 20,
                    "n_min": 0,
                    "n_max": 100,
                    "enforce_connected": False,
                    "degree": None,
                    "commRange": None,
                },
                {"count": 20},
            ),
            (
                "",
                {
                    "n_count": 30,
                    "n_min": 0,
                    "n_max": 100,
                    "enforce_connected": False,
                    "degree": None,
                    "commRange": 30,
                },
                {"count": 30},
            ),
            (
                "Check sensors and algorithms",
                {
                    "n_count": 10,
                    "n_min": 0,
                    "n_max": 100,
                    "enforce_connected": False,
                    "rangeType": rangeType,
                    "algorithms": algorithms,
                    "commRange": 100,
                },
                {
                    "count": 10,
                    "rangeType": rangeType,
                    "algorithms": algorithms,
                    "commRange": 100,
                },
            ),
        ]

    def test_random_generation(self):
        """Test different random generation parameters"""
        for comment, input, output in self.in_out:
            for directed in (True, False):
                with self.subTest(input=input, output=output, directed=directed):
                    print(f"{comment=}")
                    print(f"{input=}\n{output=}")
                    if isclass(output) and issubclass(output, Exception):
                        self.assertRaises(output, NetworkGenerator, **input)
                        continue
                    net_gen = NetworkGenerator(directed=directed, **input)
                    if output is None:
                        self.assertEqual(None, net_gen.generate_random_network(max_steps=500))
                    elif isinstance(output, dict):
                        net = net_gen.generate_random_network(max_steps=2000)
                        assert isinstance(net, NetworkType)
                        assert directed == net.is_directed()
                        net.validate_params(output)


class TestNotConnectedNetworkGeneration(unittest.TestCase):
    def setUp(self) -> None:
        self.gen = NetworkGenerator(
            n_count=10,
            n_min=10,
            n_max=10,
            degree=0.01,
            degree_tolerance=0.2,
            enforce_connected=False,
        )

    def test_generate_not_connected_net(self):
        for directed in (True, False):
            with self.subTest(directed=directed):
                self.gen.directed = directed
                net = self.gen.generate_random_network()
                assert not net.is_connected()
                assert len(net) == 10
                assert abs(net.avg_degree()) <= 0.2
                assert net.is_directed() == directed


class TestOtherGenerators(unittest.TestCase):
    def setUp(self) -> None:
        self.gen1 = NetworkGenerator(n_count=10, n_min=0, n_max=100, enforce_connected=True)
        self.gen2 = NetworkGenerator(n_count=10, n_min=10, n_max=10, enforce_connected=True)
        self.gen3 = NetworkGenerator(n_count=99, n_min=99, n_max=99, enforce_connected=True)
        self.gen4 = NetworkGenerator(
            n_count=10,
            n_min=10,
            n_max=10,
            degree=0,
            degree_tolerance=0.2,
            enforce_connected=False,
        )

    def test_generate_neighborhood(self):
        net1 = self.gen1.generate_neigborhood_network()

        assert len(net1) >= 10 and len(net1) <= 100
        assert net1.is_connected()

        net2 = self.gen2.generate_neigborhood_network()

        assert len(net2) == 10
        assert net2.is_connected()

        net3 = self.gen3.generate_neigborhood_network()

        assert len(net3) == 99
        assert net3.is_connected()

        # Dont test for the connectedness and degree for this network
        # as it is not enforced

    def test_homogeneous_network(self):
        net1 = self.gen1.generate_homogeneous_network()

        assert len(net1) >= 10 and len(net1) <= 100
        assert net1.is_connected()

        net2 = self.gen2.generate_homogeneous_network()

        assert len(net2) == 10
        assert net2.is_connected()

        net3 = self.gen3.generate_homogeneous_network()

        assert len(net3) == 99
        assert net3.is_connected()

        net4 = self.gen4.generate_homogeneous_network()

        assert len(net4) == 10
        assert not net4.is_connected()
        assert abs(net4.avg_degree()) <= 0.2
