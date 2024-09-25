import unittest

from pydistsim import Node
from pydistsim._exceptions import SimulationException
from pydistsim.algorithm import (
    Actions,
    AlgorithmException,
    NetworkAlgorithm,
    NodeAlgorithm,
    StatusValues,
)
from pydistsim.message import Message
from pydistsim.network import NetworkException, NetworkGenerator
from pydistsim.simulation import Simulation
from pydistsim.utils.helpers import first
from pydistsim.utils.testing import PyDistSimTestCase


def set_algorithms(sim, algorithms):
    sim.algorithms = algorithms


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
                SimulationException,
                [
                    (SomeNodeAlgorithm, {"rp1": 1, "rp2": 2, "rp3": 3}),
                ],
            ),
            # wrong_base_class
            (SimulationException, ((Node, {}),)),
            # missing_req_params
            (
                AlgorithmException,
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
                AlgorithmException,
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
        sim = Simulation(self.net)

        set_algorithms(sim, self.algorithms_ok)
        for exc, alg in self.check:
            self.assertRaises(exc, set_algorithms, sim, alg)

    def test_params_inheritance(self):
        """Test default params inheritance algorithm classes."""
        sim = Simulation(self.net)
        sim.algorithms = (
            (
                SomeAlgorithmWithInheritanceChild,
                {"rp1": 1, "rp2": 2, "rp3": 3, "rp4": 4, "rp5": 5, "rp6": 6},
            ),
        )
        self.assertTrue(sim.algorithms[0].dp1 == "dp1_value")
        self.assertTrue(sim.algorithms[0].dp2 == "overriden_dp2_value")
        self.assertTrue(sim.algorithms[0].dp3 == "dp3_value")
        self.assertRaises(AssertionError, rp_multiple)
        self.assertRaises(AssertionError, dp_is_rp)
        self.assertRaises(AssertionError, rp_is_dp)

    def test_default_params(self):
        """Test default params."""
        sim = Simulation(self.net)
        sim.algorithms = (
            (
                SomeNetworkAlgorithm,
                {
                    "dp2": "overriden_dp2_value",
                },
            ),
        )
        self.assertTrue(sim.algorithms[0].dp1 == "dp1_value")
        self.assertTrue(sim.algorithms[0].dp2 == "overriden_dp2_value")
        self.assertTrue(sim.algorithms[0].dp3 == "dp3_value")


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
        assert self.Status.DONE.implements(Actions.alarm)

        # Using wrong ActionEnum
        assert not self.Status.DONE.implements(Actions.spontaneously)

        # Using string
        assert self.Status.DONE.implements("alarm")

        # Using wrong string
        assert not self.Status.DONE.implements("spontaneously")

        # Using string with capital letters
        assert not self.Status.DONE.implements("ALARM")


class TimerAlgorithm(NodeAlgorithm):
    class Status(StatusValues):
        IDLE = "IDLE"
        DONE = "DONE"

    def initializer(self):
        for node in self.network.nodes():
            node.status = self.Status.IDLE
            self.set_alarm(node, 3, Message(data=f"ALARM{node._internal_id}"))
            self.set_alarm(node, 6, Message(data=f"ALARM{node._internal_id}"))
            node.memory["LAST_ALARM"] = self.set_alarm(node, 9, Message(data=f"ALARM{node._internal_id}"))

    @Status.IDLE
    def alarm(self, node, message):
        node.memory["alarm"] = message.data

        self.disable_alarm(node.memory["LAST_ALARM"])
        self.disable_all_node_alarms(node)
        node.status = self.Status.DONE


class TimerDefaultMessage(TimerAlgorithm):
    def initializer(self):
        for node in self.network.nodes():
            node.status = self.Status.IDLE
            self.set_alarm(node, 3)
            self.set_alarm(node, 6)
            node.memory["LAST_ALARM"] = self.set_alarm(node, 9)


class TimerDefaultMessageDecreasedTime(TimerAlgorithm):

    @TimerAlgorithm.Status.IDLE
    def alarm(self, node, message):
        node.memory["alarm"] = message.data

        self.disable_alarm(node.memory["LAST_ALARM"])
        self.disable_all_node_alarms(node)
        node.status = self.Status.DONE

    @TimerAlgorithm.Status.IDLE
    def spontaneously(self, node, message):
        self.update_alarm_time(node.memory["FIRST_ALARM"], -100)
        self.disable_alarm(node.memory["LAST_ALARM"])

    def initializer(self):
        for node in self.network.nodes():
            node.status = self.Status.IDLE
            node.memory["FIRST_ALARM"] = self.set_alarm(node, 4)
            node.memory["SECOND_ALARM"] = self.set_alarm(node, 6)
            node.memory["LAST_ALARM"] = self.set_alarm(node, 9)
            node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI))


class TestAlarms(unittest.TestCase):

    def test_run_base_algorithm(self):
        def node_data_test(node: "Node"):
            return (node.status == TimerAlgorithm.Status.DONE and node.memory["alarm"] == f"ALARM{node._internal_id}",)

        self.aux_test(TimerAlgorithm, node_data_test)

    def test_run_base_algorithm_default_message(self):
        self.aux_test(
            TimerDefaultMessage,
            lambda node: node.status == TimerAlgorithm.Status.DONE and node.memory["alarm"] is None,
        )

    def aux_test(self, algo_class, data_test):
        self.net = NetworkGenerator(10).generate_random_network()
        sim = Simulation(self.net)
        sim.algorithms = (algo_class,)

        algorithm: NodeAlgorithm = sim.get_current_algorithm()
        some_n = first(self.net.nodes())

        assert sim.is_halted()

        # 1 step for initialization, 3 steps for alarms, 1 step for processing alarm messages
        sim.run(1)

        assert len(algorithm._alarms) == 3 * len(self.net.nodes())
        assert len(some_n.inbox) == 0

        sim.run(1)  # alarm tic

        assert len(algorithm._alarms) == 3 * len(self.net.nodes())
        assert len(some_n.inbox) == 0

        sim.run(1)  # alarm tic

        assert len(algorithm._alarms) == 3 * len(self.net.nodes())
        assert len(some_n.inbox) == 0

        sim.run(1)  # alarm tic

        assert len(algorithm._alarms) == 2 * len(self.net.nodes())
        assert all(len(node.inbox) == 1 for node in self.net.nodes())

        sim.run(1)  # 1 step for processing alarm messages

        assert all([data_test(node) for node in self.net.nodes()])
        assert len(algorithm._alarms) == 0
        assert sim.is_halted()

    def test_update_alarm(self):
        self.net = NetworkGenerator(10).generate_random_network()
        sim = Simulation(self.net)
        sim.algorithms = (TimerDefaultMessageDecreasedTime,)

        algorithm: NodeAlgorithm = sim.get_current_algorithm()
        some_n = first(self.net.nodes())

        assert sim.is_halted()

        # 1 step for initialization, 3 steps for alarms, 1 step for processing alarm messages
        sim.run(1)

        assert len(algorithm._alarms) == 3 * len(self.net.nodes())
        assert len(some_n.inbox) == 1  # INI message
        assert some_n.memory["FIRST_ALARM"].time_left == 4

        sim.run(1)  # alarm tic

        assert len(algorithm._alarms) == 3 * len(self.net.nodes())
        assert len(some_n.inbox) == 1  # INI message
        assert some_n.memory["FIRST_ALARM"].time_left == 3

        sim.run(1)  # alarm tic -> processes INI and disables LAST_ALARM

        assert len(algorithm._alarms) == 2 * len(self.net.nodes())
        assert len(some_n.inbox) == 0
        assert some_n.memory["FIRST_ALARM"].time_left == -98  # -100 + 2

        sim.run(1)  # alarm tic -> FIRST_ALARM triggered

        assert len(algorithm._alarms) == len(self.net.nodes())  # Only SECOND_ALARM left
        assert all(len(node.inbox) == 1 for node in self.net.nodes())  # 1 alarm message (generated by FIRST_ALARM)

        sim.run(1)  # 1 step for processing alarm messages, disables SECOND_ALARM

        assert len(algorithm._alarms) == 0
        assert sim.is_halted()
