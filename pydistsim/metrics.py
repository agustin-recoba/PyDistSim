"""
:class:`MetricCollector` is an observer that collects metrics from the simulation.
"""

from time import time
from typing import TYPE_CHECKING

from pydistsim.observers import (
    AlgorithmObserver,
    NodeNetworkObserver,
    ObservableEvents,
    SimulationObserver,
)

if TYPE_CHECKING:
    from pydistsim.algorithm import BaseAlgorithm
    from pydistsim.message import Message
    from pydistsim.network import Node
    from pydistsim.simulation import Simulation


class MetricCollector(NodeNetworkObserver, AlgorithmObserver, SimulationObserver):
    """
    MetricCollector is an observer that collects metrics from the simulation.

    ### Custom metrics
    Extend this class and implement the desired event methods to collect custom metrics.
    For registering events, call the `_add_metric` method.
    Add an instance of your custom collector to the simulation observers for it to work.

    Even so, you can use the `events` attribute to register the events you want to listen to.
    This includes new custom events that you would trigger from an algorithm.

    Example of implementing a custom metric collector:

    .. code-block:: python

        class ExampleCustomMetricCollector(MetricCollector):
            events = ["example_custom_event"]

            class CustomMetricEventType(StrEnum):
                "Definition if this enum is optional. It helps to avoid typos in the event names."
                EXAMPLE_CUSTOM_EVENT_ZERO = "EXAMPLE_CUSTOM_EVENT_ZERO"
                ...

            def on_example_custom_event(self, a, b, c):
                self._add_metric(
                    self.CustomMetricEventType.EXAMPLE_CUSTOM_EVENT_ZERO,
                    {"a": a, "b": b, "c": c}
                )

    """

    def __init__(self):
        self.metrics: list[tuple[float, ObservableEvents, dict]] = []

    def _add_metric(self, event_type: "ObservableEvents", event_data: dict):
        self.metrics.append((time(), event_type, event_data))

    # AlgorithmObserver methods
    def on_step_done(self, algorithm: "BaseAlgorithm") -> None:
        self._add_metric(
            ObservableEvents.step_done,
            None,
        )

    def on_message_sent(self, message: "Message") -> None:
        self._add_metric(
            ObservableEvents.message_sent,
            {"message": message},
        )

    def on_algorithm_started(self, algorithm: "BaseAlgorithm") -> None:
        self._add_metric(
            ObservableEvents.algorithm_started,
            {"algorithm": algorithm},
        )

    # SimulationObserver methods
    def on_state_changed(self, simulation: "Simulation") -> None: ...

    def on_algorithm_finished(self, algorithm: "BaseAlgorithm") -> None:
        self._add_metric(
            ObservableEvents.algorithm_finished,
            {"algorithm": algorithm},
        )

    def on_network_changed(self, simulation: "Simulation") -> None: ...

    # NetworkObserver methods (none yet)
    def on_message_delivered(self, message: "Message") -> None:
        self._add_metric(
            ObservableEvents.message_delivered,
            {"message": message},
        )

    # NodeNetworkObserver methods
    def on_node_status_changed(self, node: "Node", previous_status: str, new_status: str) -> None:
        self._add_metric(
            ObservableEvents.node_status_changed,
            {
                "node": node,
                "previous_status": previous_status,
                "new_status": new_status,
            },
        )

    def create_report(self):
        """
        Returns a dictionary with the collected metrics.

        Currently, it returns the number of messages sent, messages delivered, and quantity of status changes.
        Future versions may include more metrics, with better reporting capabilities.
        """
        msg_sent = 0
        msg_delivered = 0
        qty_nodes_status_changed = 0
        qty_steps_done = 0

        for timestamp, event_type, event_data in self.metrics:
            match event_type:
                case ObservableEvents.message_sent:
                    msg_sent += 1
                case ObservableEvents.message_delivered:
                    msg_delivered += 1
                case ObservableEvents.node_status_changed:
                    qty_nodes_status_changed += 1
                case ObservableEvents.step_done:
                    qty_steps_done += 1

        return {
            "Qty. of messages sent": msg_sent,
            "Qty. of messages delivered": msg_delivered,
            "Qty. of status changes": qty_nodes_status_changed,
            "Qty. of steps": qty_steps_done,
        }
