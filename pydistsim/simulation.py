"""
Simulation module for the PyDistSim package.
"""

import inspect
from copy import copy, deepcopy
from typing import TYPE_CHECKING, Optional

from pydistsim._exceptions import SimulationException
from pydistsim.algorithm import BaseAlgorithm
from pydistsim.logging import logger
from pydistsim.observers import (
    NetworkObserver,
    ObservableEvents,
    ObserverManagerMixin,
    SimulationObserver,
)

if TYPE_CHECKING:
    from pydistsim.network import NetworkType


AlgorithmsParam = tuple[type["BaseAlgorithm"] | tuple[type["BaseAlgorithm"], dict]]


class Simulation(ObserverManagerMixin):
    """
    Controls single network algorithm and node algorithms simulation.
    It is responsible for visualization and logging, also.

    :param network: The network object representing the simulation network.
    :type network: NetworkType
    :param algorithms: The algorithms to be executed on the network.
    :type algorithms: AlgorithmsParam, optional
    :param check_restrictions: Whether to check restrictions during the simulation.
    :type check_restrictions: bool, optional
    :param kwargs: Additional keyword arguments.
    """

    def __init__(
        self,
        network: "NetworkType",
        algorithms: AlgorithmsParam | None = None,
        check_restrictions: bool = True,
        **kwargs,
    ):
        super().__init__()

        self._network = network
        self._network.simulation = self
        self._algorithms = ()
        if algorithms is not None:
            self.algorithms = algorithms

        self.algorithmState = {"index": 0, "step": 1, "finished": False}
        self.stepsLeft = 0
        self.check_restrictions = check_restrictions

        logger.info("Simulation {} created successfully.", hex(id(self)))

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]

        # Shallow copy of the object
        copy_s = type(self)(deepcopy(self._network, memo))
        memo[id(self)] = copy_s

        # Shallow copy of the immutable attributes
        copy_s.algorithms = self._algorithms_param
        copy_s.algorithmState = copy(self.algorithmState)
        copy_s.stepsLeft = self.stepsLeft
        copy_s.check_restrictions = self.check_restrictions

        # Deep copy of the mutable attributes
        copy_s.algorithmState = deepcopy(self.algorithmState, memo)
        copy_s.stepsLeft = self.stepsLeft

        copy_s.clear_observers()

        return copy_s

    def run(self, steps=0):
        """
        Run simulation from the current state.

        :param steps: Number of steps to run the simulation.
                      If steps = 0, it runs until all algorithms are finished.
                      If steps > 0, the simulation is in stepping mode.
                      If steps > number of steps to finish the current algorithm, it finishes it.
        :type steps: int
        """
        self.stepsLeft = steps
        for _ in range(len(self.algorithms) * len(self.network)):
            algorithm: Optional["BaseAlgorithm"] = self.get_current_algorithm()
            if not algorithm:
                logger.info(
                    "Simulation has finished. There are no algorithms left to run. "
                    "To run it from the start use sim.reset()."
                )
                self.notify_observers(ObservableEvents.sim_state_changed, self)
                break
            algorithm.add_observers(*self.observers)
            self._run_algorithm(algorithm)
            self.notify_observers(ObservableEvents.sim_state_changed, self)
            if self.stepsLeft <= 0:
                break

    def run_step(self):
        """
        Run a single step of the simulation.

        This is equivalent to calling sim.run(1).
        """
        self.run(1)

    def _run_algorithm(self, algorithm: BaseAlgorithm):
        """
        Run the given algorithm on the given network.

        Update stepsLeft and sim.algorithmState['step'].
        If stepsLeft hit 0 it may return unfinished.

        :param algorithm: The algorithm to run on the network.
        """
        for _ in range(1000 * len(self.network)):
            logger.debug(
                "[{}] Step {} started",
                algorithm.name,
                self.algorithmState["step"],
            )
            algorithm.step(self.check_restrictions, self.algorithmState["step"])
            self.stepsLeft -= 1
            self.algorithmState["step"] += 1
            self.network.increment_node_clocks()
            logger.debug(
                "[{}] Step {} finished",
                algorithm.name,
                self.algorithmState["step"],
            )

            if algorithm.is_halted():
                break  # algorithm finished
            if self.stepsLeft == 0:
                return  # stepped execution finished

        self.notify_observers(ObservableEvents.algorithm_finished, algorithm)
        logger.info("[{}] Algorithm finished", algorithm.name)
        self.algorithmState["finished"] = True

    def reset(self):
        """
        Reset the simulation.
        """
        logger.debug("Resetting simulation.")
        self.algorithmState = {"index": 0, "step": 1, "finished": False}
        self._network.reset()
        if self._algorithms:
            for algorithm in self._algorithms:
                algorithm.reset()

    def is_halted(self):
        """
        Check if simulation has come to an end or deadlock,
        i.e. there are no messages to pass and no alarms set.

        A not-started algorithm is considered halted. If there are
        no algorithms left to run, the simulation is also considered halted.

        :return: True if the algorithm is halted, False otherwise.
        :rtype: bool
        """
        algorithm: Optional["BaseAlgorithm"] = self.get_current_algorithm()
        return algorithm is None or algorithm.is_halted()

    @property
    def network(self):
        """
        Get the network associated with the simulation.
        """
        return self._network

    @network.setter
    def network(self, network: "NetworkType"):
        """
        Set the network for the simulation.

        :param network: The network object to set.
        :type network: NetworkType
        """
        self._network.simulation = None  # remove reference to this simulation in the old network
        self._network.clear_observers()

        self._network = network
        self._network.simulation = self
        self.notify_observers(ObservableEvents.network_changed, self)
        self._copy_observers_to_network()

    def add_observers(self, *observers: "SimulationObserver"):
        super().add_observers(*observers)
        self._copy_observers_to_network()

    def _copy_observers_to_network(self):
        self.network.add_observers(*(observer for observer in self.observers if isinstance(observer, NetworkObserver)))

    #### Algorithm relation methods ####

    def get_current_algorithm(self) -> BaseAlgorithm | None:
        """
        Try to return the current algorithm based on the algorithmState.

        :return: The current algorithm.
        :rtype: BaseAlgorithm or None

        :raises NetworkException: If there are no algorithms defined in the network.
        """
        if len(self.algorithms) == 0:
            logger.error("There is no algorithm defined in the network.")
            raise SimulationException(SimulationException.ERRORS.ALGORITHM_NOT_FOUND)

        if self.algorithmState["finished"]:
            if len(self.algorithms) > self.algorithmState["index"] + 1:
                self.algorithmState["index"] += 1
                self.algorithmState["step"] = 1
                self.algorithmState["finished"] = False
            else:
                return None

        return self.algorithms[self.algorithmState["index"]]

    @property
    def algorithms(self):
        """
        Set algorithms by passing tuple of Algorithm subclasses.

        >>> sim.algorithms = (Algorithm1, Algorithm2,)

        For params pass tuples in form (Algorithm, params) like this

        >>> sim.algorithms = ((Algorithm1, {'param1': value,}), Algorithm2)

        """
        return self._algorithms

    @algorithms.setter
    def algorithms(self, algorithms: AlgorithmsParam):
        self.reset()
        self._algorithms = ()
        if not isinstance(algorithms, tuple):
            raise SimulationException(SimulationException.ERRORS.ALGORITHM)
        for algorithm in algorithms:
            if inspect.isclass(algorithm) and issubclass(algorithm, BaseAlgorithm):
                self._algorithms += (algorithm(self),)
            elif (
                isinstance(algorithm, tuple)
                and len(algorithm) == 2
                and issubclass(algorithm[0], BaseAlgorithm)
                and isinstance(algorithm[1], dict)
            ):
                self._algorithms += (algorithm[0](self, **algorithm[1]),)
            else:
                raise SimulationException(SimulationException.ERRORS.ALGORITHM)

        # If everything went ok, set algorithms param for coping
        self._algorithms_param = algorithms

    def get_dic(self):
        """
        Return all simulation data in the form of a dictionary.

        :return: A dictionary containing the simulation data.
        :rtype: dict
        """

        algorithms = {
            "%d %s" % (ind, alg.name): ("active" if alg == self.algorithms[self.algorithmState["index"]] else "")
            for ind, alg in enumerate(self.algorithms)
        }

        return {
            "algorithms": algorithms,  # A dictionary mapping algorithm names to their status (active or not).
            "algorithmState": {
                "name": (  # The name of the current algorithm.
                    self.get_current_algorithm().name if self.get_current_algorithm() else "No algorithm"
                ),
                "step": self.algorithmState["step"],  # The current step of the algorithm.
                "finished": self.algorithmState["finished"],  # Whether the algorithm has finished or not.
            },
        }
