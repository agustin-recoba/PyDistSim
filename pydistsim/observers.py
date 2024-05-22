import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydistsim.algorithm import Algorithm
    from pydistsim.simulation import Simulation


class Observer(abc.ABC):
    events = []


class AlgorithmObserver(Observer, abc.ABC):
    events = ["step_done"]

    @abc.abstractmethod
    def on_step_done(self, algorithm: "Algorithm") -> None: ...


class SimulationObserver(Observer, abc.ABC):
    events = ["state_changed", "algorithm_finished", "network_changed"]

    @abc.abstractmethod
    def on_state_changed(self, simulation: "Simulation") -> None: ...

    @abc.abstractmethod
    def on_algorithm_finished(self, algorithm: "Algorithm") -> None: ...

    @abc.abstractmethod
    def on_network_changed(self, simulation: "Simulation") -> None: ...


class NetworkObserver(Observer, abc.ABC): ...


class ObserverManagerMixin:
    OBSERVER_TYPE = Observer

    def __init__(self, *args, **kwargs):
        self.observers: set[self.OBSERVER_TYPE] = set()
        super().__init__(*args, **kwargs)

    def add_observers(self, *observers: "Observer"):
        for observer in observers:
            self.observers.add(observer)

    def notify_observers(self, event: str, *args, **kwargs):
        if event not in self.OBSERVER_TYPE.events:
            raise ValueError(f"Invalid event: {event}")

        for observer in self.observers:
            getattr(observer, f"on_{event.lower()}")(*args, **kwargs)
