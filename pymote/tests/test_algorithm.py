import unittest

from pymote import Node
from pymote.algorithm import (
    ActionEnum,
    NetworkAlgorithm,
    NodeAlgorithm,
    PymoteAlgorithmException,
    StatusValues,
)
from pymote.network import PymoteNetworkError
from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation


def set_algorithms(net, algorithms):
    net.algorithms = algorithms


class SomeNodeAlgorithm(NodeAlgorithm):
    required_params = ("rp1", "rp2", "rp3")
    default_params = {"dp1": "dp1_value", "dp2": "dp2_value", "dp3": "dp3_value"}


class SomeNetworkAlgorithm(NetworkAlgorithm):
    default_params = {"dp1": "dp1_value", "dp2": "dp2_value", "dp3": "dp3_value"}


class SomeAlgorithmWithInheritance(SomeNodeAlgorithm):
    required_params = ("rp4",)
    default_params = {
        "dp4": "dp4_value",
    }


class SomeAlgorithmWithInheritanceChild(SomeAlgorithmWithInheritance):
    required_params = ("rp5", "rp6")
    default_params = {
        "dp2": "overriden_dp2_value",
    }


def rp_multiple():
    class SomeAlgorithmWhereRpIsRedefined(SomeAlgorithmWithInheritance):
        required_params = ("rp2",)


def dp_is_rp():
    class SomeAlgorithmWhereDpIsInheritedRp(SomeAlgorithmWithInheritance):
        default_params = {
            "rp2": "dp2_value",
        }


def rp_is_dp():
    class SomeAlgorithmWhereRpIsInheritedDp(SomeAlgorithmWithInheritance):
        required_params = ("dp2",)


class TestAlgorithmsSetter(unittest.TestCase):

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.algorithms_ok = (
            (
                SomeNodeAlgorithm,
                {
                    "rp1": 1,
                    "rp2": 2,
                    "rp3": 3,
                },
            ),
            (SomeNetworkAlgorithm, {}),
            SomeNetworkAlgorithm,
            (SomeAlgorithmWithInheritance, {"rp1": 1, "rp2": 2, "rp3": 3, "rp4": 4}),
            (
                SomeAlgorithmWithInheritanceChild,
                {"rp1": 1, "rp2": 2, "rp3": 3, "rp4": 4, "rp5": 5, "rp6": 6},
            ),
        )
        self.check = [
            # wrong_format
            (
                PymoteNetworkError,
                [
                    (SomeNodeAlgorithm, {"rp1": 1, "rp2": 2, "rp3": 3}),
                ],
            ),
            # wrong_base_class
            (PymoteNetworkError, ((Node, {}),)),
            # missing_req_params
            (
                PymoteAlgorithmException,
                (
                    (
                        SomeNodeAlgorithm,
                        {
                            "rp1": 1,
                        },
                    ),
                ),
            ),
            (
                PymoteAlgorithmException,
                (
                    (
                        SomeAlgorithmWithInheritance,
                        {
                            "rp1": 1,
                        },
                    ),
                ),
            ),
        ]

    def test_setter(self):
        """Test different algorithm initialization formats and params."""
        set_algorithms(self.net, self.algorithms_ok)
        for exc, alg in self.check:
            self.assertRaises(exc, set_algorithms, self.net, alg)

    def test_params_inheritance(self):
        """Test default params inheritance algorithm classes."""
        self.net.algorithms = (
            (
                SomeAlgorithmWithInheritanceChild,
                {"rp1": 1, "rp2": 2, "rp3": 3, "rp4": 4, "rp5": 5, "rp6": 6},
            ),
        )
        self.assertTrue(self.net.algorithms[0].dp1 == "dp1_value")
        self.assertTrue(self.net.algorithms[0].dp2 == "overriden_dp2_value")
        self.assertTrue(self.net.algorithms[0].dp3 == "dp3_value")
        self.assertRaises(AssertionError, rp_multiple)
        self.assertRaises(AssertionError, dp_is_rp)
        self.assertRaises(AssertionError, rp_is_dp)

    def test_default_params(self):
        """Test default params."""
        self.net.algorithms = (
            (
                SomeNetworkAlgorithm,
                {
                    "dp2": "overriden_dp2_value",
                },
            ),
        )
        self.assertTrue(self.net.algorithms[0].dp1 == "dp1_value")
        self.assertTrue(self.net.algorithms[0].dp2 == "overriden_dp2_value")
        self.assertTrue(self.net.algorithms[0].dp3 == "dp3_value")


class TestRunBaseAlgorithm(unittest.TestCase):
    class UnimplementedAlgorithm(NodeAlgorithm): ...

    def setUp(self):
        net_gen = NetworkGenerator(100)
        self.net = net_gen.generate_random_network()
        self.net.algorithms = (self.UnimplementedAlgorithm,)

    def test_run_base_algorithm(self):
        sim = Simulation(self.net, "DEBUG")

        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert len(node.outbox) == 0
                assert len(node.inbox) == 0

        sim.run(1)
        # First step should transfer the INI from the outbox to the inbox of the initiator node
        assert len(self.net.outbox) == 0

        nodes_with_1_msg = 0
        for node in self.net.nodes():
            with self.subTest(node=node):
                print(f"{node.id=}, {node.status=}, {node.outbox=}, {node.inbox=}")
                assert len(node.outbox) == 0
                nodes_with_1_msg += 1 if len(node.inbox) else 0
        assert nodes_with_1_msg == 1

        sim.run(1)
        # Second step should process the INI message (and do nothing)

        assert sim.is_halted()


class TestStatusValues(unittest.TestCase):
    def setUp(self):
        class Status(StatusValues):
            IDLE = "IDLE"
            DONE = "DONE"

        self.Status = Status

    def test_state_action_names(self):
        """Test if state action names raise exception and correct ones are allowed."""

        @self.Status.IDLE
        def spontaneously(): ...

        @self.Status.IDLE
        def receiving(): ...

        @self.Status.IDLE
        def alarm(): ...

        # Test if wrong name raises exception
        def wrong_name(): ...

        self.assertRaises(AssertionError, self.Status.IDLE, wrong_name)

        # Test if good name with capital letters raises exception
        def ALARM(): ...

        self.assertRaises(AssertionError, self.Status.IDLE, ALARM)

    def test_implements_method(self):
        """Test Status.implements method."""

        @self.Status.DONE
        def alarm(): ...

        # Using correct ActionEnum
        assert self.Status.DONE.implements(ActionEnum.alarm)

        # Using wrong ActionEnum
        assert not self.Status.DONE.implements(ActionEnum.spontaneously)

        # Using string
        assert self.Status.DONE.implements("alarm")

        # Using wrong string
        assert not self.Status.DONE.implements("spontaneously")

        # Using string with capital letters
        assert not self.Status.DONE.implements("ALARM")
