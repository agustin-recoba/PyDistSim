"""
This module contains the classes for observers and the mixin class for objects that can have observers.
"""

from typing import TYPE_CHECKING

from pydistsim.logging import logger

if TYPE_CHECKING:
    from pydistsim.algorithm import BaseAlgorithm
    from pydistsim.message import Message
    from pydistsim.network import Node
    from pydistsim.simulation import Simulation


class ObservableEvents(str):
    """
    Enum-like class for the events that can be observed.
    :class:`StrEnum` from the :mod:`enum` module is not used because it does not support inheritance.
    """

    added = "added"
    step_done = "step_done"
    message_sent = "message_sent"
    sim_state_changed = "sim_state_changed"
    algorithm_started = "algorithm_started"
    algorithm_finished = "algorithm_finished"
    network_changed = "network_changed"
    message_delivered = "message_delivered"
    node_status_changed = "node_status_changed"

    _all = (
        added,
        step_done,
        message_sent,
        sim_state_changed,
        algorithm_started,
        algorithm_finished,
        network_changed,
        message_delivered,
        node_status_changed,
    )


class Observer:
    """
    Base class for observers.

    Subclasses must implement the `on_{event_name}` methods for the events they want to listen to.

    If an observer is notified of an event it does not listen to, the notification is discarded
    and a debug message is logged.

    To define the events an observer listens to, set the `events` attribute to a list of event names.
    The definitive list of allowed events is the union of the `events` attribute of every class in
    the inheritance chain.
    For more information, refer to the :meth:`__get_allowed_events__` method.

    Example of concrete implementations are:
    - :class:`MetricCollector` class in :mod:`pydistsim.metrics`
    - :class:`QThreadObserver` class in :mod:`pydistsim.gui.simulationgui`
    """

    events = [ObservableEvents.added]

    @classmethod
    def __get_allowed_events__(cls) -> set[ObservableEvents]:
        def get_bases(cls):
            for base_cls in cls.__bases__:
                yield from get_bases(base_cls)
                yield base_cls

        allowed_events = set(cls.events)
        for base_cls in get_bases(cls):
            if issubclass(base_cls, Observer) or base_cls == Observer:
                allowed_events.update(base_cls.events)
        return allowed_events

    def notify(self, event: ObservableEvents, *args, **kwargs):
        allowed_events = self.__get_allowed_events__()
        if event not in allowed_events:
            logger.trace(
                "Invalid event name '{}' for observer type {}. Valid events are: {}.",
                event,
                self.__class__.__name__,
                ", ".join(allowed_events),
            )
            return
        getattr(self, f"on_{event.lower()}")(*args, **kwargs)

    def on_added(self, observable: "ObserverManagerMixin") -> None:
        """
        Called when the observer is added to an observable object.

        :param observable: The observable object to which the observer is added.
        :type observable: ObserverManagerMixin

        :return: None
        """
        ...


class AlgorithmObserver(Observer):
    """
    Observer for algorithm events.
    """

    events = [
        ObservableEvents.step_done,
        ObservableEvents.algorithm_started,
    ]

    def on_step_done(self, algorithm: "BaseAlgorithm") -> None: ...

    def on_algorithm_started(self, algorithm: "BaseAlgorithm") -> None: ...


class SimulationObserver(Observer):
    """
    Observer for simulation events.
    """

    events = [
        ObservableEvents.sim_state_changed,
        ObservableEvents.algorithm_finished,
        ObservableEvents.network_changed,
    ]

    def on_sim_state_changed(self, simulation: "Simulation") -> None: ...

    def on_algorithm_finished(self, algorithm: "BaseAlgorithm") -> None: ...

    def on_network_changed(self, simulation: "Simulation") -> None: ...


class NetworkObserver(Observer):
    """
    Observer for network events.
    No such events are defined yet.
    """

    events = []


class NodeObserver(Observer):
    """
    Observer for node events.
    No such events are defined yet.
    """

    events = [
        ObservableEvents.node_status_changed,
        ObservableEvents.message_delivered,
        ObservableEvents.message_sent,
    ]

    def on_node_status_changed(self, node: "Node", previous_status: str, new_status: str) -> None: ...

    def on_message_delivered(self, message: "Message") -> None: ...

    def on_message_sent(self, message: "Message") -> None: ...


class NodeNetworkObserver(NodeObserver, NetworkObserver):
    """
    Observer for node AND network events.
    """


class ObserverManagerMixin:
    """
    Mixin class for objects that can have observers.

    Subclasses must call the `super().__init__()` method in their :meth:`__init__` method or
    add the :attr:`observers` attribute.
    """

    def __init__(self, *args, **kwargs):
        self.observers: set[Observer] = set()
        super().__init__(*args, **kwargs)

    def add_observers(self, *observers: "Observer"):
        for observer in observers:
            self.observers.add(observer)
            observer.notify(ObservableEvents.added, self)

    def clear_observers(self):
        self.observers = set()

    def notify_observers(self, event: ObservableEvents, *args, **kwargs):
        for observer in self.observers:
            observer.notify(event, *args, **kwargs)
