from contextlib import contextmanager

from pydistsim.demo_algorithms.broadcast import Flood
from pydistsim.network import NetworkGenerator
from pydistsim.observers import (
    AlgorithmObserver,
    NetworkObserver,
    NodeObserver,
    ObservableEvents,
    SimulationObserver,
)
from pydistsim.simulation import Simulation
from pydistsim.utils.testing import PyDistSimTestCase


class ObserverForTests(AlgorithmObserver, SimulationObserver, NetworkObserver, NodeObserver):
    """
    A test observer that raises an exception when notified.
    """

    events = list(ObservableEvents._all)

    class ObserverNotified(Exception):
        def __init__(self, event):
            self.event = event

    def __init__(self) -> None:
        self.raise_e = None

    @contextmanager
    def do_raise(self, event):
        try:
            self.raise_e = event
            yield self
        finally:
            self.raise_e = None

    def on_added(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.added:
            raise self.ObserverNotified(ObservableEvents.added)

    def on_step_done(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.step_done:
            raise self.ObserverNotified(ObservableEvents.step_done)

    def on_message_sent(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.message_sent:
            raise self.ObserverNotified(ObservableEvents.message_sent)

    def on_sim_state_changed(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.sim_state_changed:
            raise self.ObserverNotified(ObservableEvents.sim_state_changed)

    def on_algorithm_started(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.algorithm_started:
            raise self.ObserverNotified(ObservableEvents.algorithm_started)

    def on_algorithm_finished(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.algorithm_finished:
            raise self.ObserverNotified(ObservableEvents.algorithm_finished)

    def on_network_changed(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.network_changed:
            raise self.ObserverNotified(ObservableEvents.network_changed)

    def on_message_delivered(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.message_delivered:
            raise self.ObserverNotified(ObservableEvents.message_delivered)

    def on_node_status_changed(self, *args, **kwargs):
        if self.raise_e == ObservableEvents.node_status_changed:
            raise self.ObserverNotified(ObservableEvents.node_status_changed)


class TestObserver(PyDistSimTestCase):
    def setUp(self):
        super().setUpClass()
        self.observer = ObserverForTests()
        self.net = NetworkGenerator(10, directed=False).generate_random_network()

        self.sim = Simulation(self.net)
        self.sim.algorithms = ((Flood, {"informationKey": "greet"}),)

        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = "HELLO"

    def test_added(self):
        with self.observer.do_raise(ObservableEvents.added):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.add_observers(self.observer)

        self.assertEqual(context.exception.event, ObservableEvents.added)

    def test_step_done(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.step_done):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.run(1)

        self.assertEqual(context.exception.event, ObservableEvents.step_done)

    def test_algorithm_started(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.algorithm_started):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.run(1)

        self.assertEqual(context.exception.event, ObservableEvents.algorithm_started)

    def test_algorithm_finished(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.algorithm_finished):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.run(100_000)

        self.assertEqual(context.exception.event, ObservableEvents.algorithm_finished)

    def test_network_changed(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.network_changed):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.network = self.net

        self.assertEqual(context.exception.event, ObservableEvents.network_changed)

    def test_sim_state_changed(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.sim_state_changed):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.run(100_000)

        self.assertEqual(context.exception.event, ObservableEvents.sim_state_changed)

    def test_message_sent(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.message_sent):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.run(3)

        self.assertEqual(context.exception.event, ObservableEvents.message_sent)

    def test_message_delivered(self):
        self.sim.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.message_delivered):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                self.sim.run(1)

        self.assertEqual(context.exception.event, ObservableEvents.message_delivered)

    def test_node_status_changed(self):
        some_node = self.net.nodes_sorted()[0]
        some_node.add_observers(self.observer)
        with self.observer.do_raise(ObservableEvents.node_status_changed):
            with self.assertRaises(ObserverForTests.ObserverNotified) as context:
                some_node.status = "NEW"

        self.assertEqual(context.exception.event, ObservableEvents.node_status_changed)


class TestWrongEvent(PyDistSimTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.observer = ObserverForTests()
        cls.net = NetworkGenerator(10, directed=False).generate_random_network()

    def test_wrong_event(self):
        # Nothing should happen
        self.net.add_observers(self.observer)
        self.net.notify_observers("test", None)
