from pydistsim.benchmark import MetricCollector
from pydistsim.demo_algorithms.broadcast import Flood
from pydistsim.message import Message
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

    def create_report(self):
        report = super().create_report()
        report["example_custom_event_msgs_sources"] = self.example_custom_event_msgs
        return report


class CustomAlgorithm(Flood):

    @Flood.Status.IDLE
    def receiving(self, node, message):
        super().receiving_IDLE(node, message)
        self.notify_observers("example_custom_event", message)


class TestMetricCollector(PyDistSimTestCase):
    def setUp(self):
        self.observer = MetricCollector()
        self.net = NetworkGenerator(10, directed=False).generate_random_network()
        self.sim = Simulation(self.net)
        self.sim.algorithms = ((Flood, {"informationKey": "greet"}),)

        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = "HELLO"

    def test_all(self):
        self.sim.add_observers(self.observer)
        self.sim.run(100_000)
        report = self.observer.create_report()

        assert "Qty. of messages sent" in report and report["Qty. of messages sent"] > 0
        assert "Qty. of messages delivered" in report and report["Qty. of messages delivered"] > 0
        assert "Qty. of status changes" in report and report["Qty. of status changes"] > 0
        assert "Qty. of steps" in report and report["Qty. of steps"] > 0


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
        self.sim = Simulation(self.net)
        self.sim.algorithms = ((CustomAlgorithm, {"informationKey": "greet"}),)

        self.initiator = self.net.nodes_sorted()[0]
        self.initiator.memory["greet"] = "HELLO"

    def test_all(self):
        self.sim.add_observers(self.observer)
        self.sim.run(100_000)
        report = self.observer.create_report()

        assert "Qty. of messages sent" in report and report["Qty. of messages sent"] > 0
        assert "Qty. of messages delivered" in report and report["Qty. of messages delivered"] > 0
        assert "Qty. of status changes" in report and report["Qty. of status changes"] > 0
        assert "Qty. of steps" in report and report["Qty. of steps"] > 0
        assert "example_custom_event_msgs_sources" in report and len(report["example_custom_event_msgs_sources"]) > 0
