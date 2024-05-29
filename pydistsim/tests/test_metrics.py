from pydistsim.algorithms.broadcast import Flood
from pydistsim.message import Message
from pydistsim.metrics import MetricCollector
from pydistsim.network import NetworkGenerator
from pydistsim.simulation import Simulation
from pydistsim.utils.testing import PyDistSimTestCase


class CustomMetricCollector(MetricCollector):
    """
    A test observer that raises an exception when notified.
    """

    events = ["example_custom_event"]

    def __init__(self) -> None:
        super().__init__()
        self.example_custom_event_msgs = []

    def on_example_custom_event(self, message: "Message"):
        self.example_custom_event_msgs.append(message.source)

    def make_report(self):
        report = super().make_report()
        report["example_custom_event_msgs_sources"] = self.example_custom_event_msgs
        return report


class CustomAlgorithm(Flood):

    @Flood.Status.IDLE
    def receiving(self, node, message):
        Flood.receiving(self, node, message)
        self.notify_observers("example_custom_event", message)


class TestMetricCollector(PyDistSimTestCase):
    def setUp(self):
        self.observer = MetricCollector()
        self.net = NetworkGenerator(10, directed=False).generate_random_network()
        self.net.algorithms = ((Flood, {"informationKey": "greet"}),)

        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = "HELLO"

        self.sim = Simulation(self.net)

    def test_all(self):
        self.sim.add_observers(self.observer)
        self.sim.run()
        report = self.observer.make_report()

        assert "messages_sent" in report and report["messages_sent"] > 0
        assert "messages_delivered" in report and report["messages_delivered"] > 0
        assert "qty_nodes_status_changed" in report and report["qty_nodes_status_changed"] > 0


class TestWrongEvent(PyDistSimTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.observer = MetricCollector()
        cls.net = NetworkGenerator(10, directed=False).generate_random_network()

    def test_wrong_event(self):
        # Nothing should happen
        self.net.add_observers(self.observer)
        self.net.notify_observers("test", None)


class TestCustomMetricCollector(PyDistSimTestCase):
    def setUp(self):
        self.observer = CustomMetricCollector()
        self.net = NetworkGenerator(10, directed=False).generate_random_network()
        self.net.algorithms = ((CustomAlgorithm, {"informationKey": "greet"}),)

        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = "HELLO"

        self.sim = Simulation(self.net)

    def test_all(self):
        self.sim.add_observers(self.observer)
        self.sim.run()
        report = self.observer.make_report()

        assert "messages_sent" in report and report["messages_sent"] > 0
        assert "messages_delivered" in report and report["messages_delivered"] > 0
        assert "qty_nodes_status_changed" in report and report["qty_nodes_status_changed"] > 0
        assert "example_custom_event_msgs_sources" in report and len(report["example_custom_event_msgs_sources"]) > 0
