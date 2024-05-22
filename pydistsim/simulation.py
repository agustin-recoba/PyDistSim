from PySide6.QtCore import SIGNAL, QThread

from pydistsim.algorithm import Algorithm
from pydistsim.logger import logger
from pydistsim.network import Network
from pydistsim.observers import (
    AlgorithmObserver,
    ObserverManagerMixin,
    SimulationObserver,
)


class Simulation(ObserverManagerMixin, QThread):
    """
    Controls single network algorithm and node algorithms simulation.
    It is responsible for visualization and logging, also.
    """

    OBSERVER_TYPE = SimulationObserver

    def __init__(self, network: Network, **kwargs):
        """
        Initialize a Simulation object.

        :param network: The network object representing the simulation network.
        :type network: Network
        :param logLevel: The log level for the simulation logger (default: LogLevels.DEBUG).
        :type logLevel: LogLevels
        :param kwargs: Additional keyword arguments.
        """
        super().__init__()

        self._network = network
        self._network.simulation = self
        self.stepsLeft = 0
        self.add_observers(QThreadObserver(self))

        logger.debug("Simulation {} created successfully.", hex(id(self)))

    def __del__(self):
        self.exiting = True
        self.wait()

    def run(self, steps=0):
        """
        Run simulation from the current state.

        :param steps: Number of steps to run the simulation.
                      If steps = 0, it runs until all algorithms are finished.
                      If steps > 0, the simulation is in stepping mode.
                      If steps > number of steps to finish the current algorithm, it finishes it.
        :type steps: int

        :return: None
        """
        self.stepsLeft = steps
        while True:
            algorithm: "Algorithm" = self.network.get_current_algorithm()
            if not algorithm:
                logger.info(
                    "Simulation has finished. There are no "
                    "algorithms left to run. "
                    "To run it from the start use sim.reset()."
                )
                self.notify_observers("state_changed", self)
                break
            algorithm.add_observers(*self.observers)
            self._run_algorithm(algorithm)
            self.notify_observers("state_changed", self)
            if self.stepsLeft >= 0:
                break

    def run_step(self):
        """
        Run a single step of the simulation.

        This is equivalent to calling sim.run(1).

        :return: None
        """
        self.run(1)

    def _run_algorithm(self, algorithm: Algorithm):
        """
        Run the given algorithm on the given network.

        Update stepsLeft and network.algorithmState['step'].
        If stepsLeft hit 0 it may return unfinished.

        :param algorithm: The algorithm to run on the network.
        """
        while True:
            algorithm.step()
            self.stepsLeft -= 1
            if self.stepsLeft == 0:
                return  # not finished

            if self.is_halted():  # end of the loop so at least one step is done
                break

        self.notify_observers("algorithm_finished", algorithm)
        logger.debug("[{}] Algorithm finished", algorithm.name)
        self.network.algorithmState["finished"] = True

    def reset(self):
        """
        Reset the simulation.

        :return: None
        """
        logger.info("Resetting simulation.")
        self._network.reset()

    def is_halted(self):
        """
        Check if the distributed algorithm has come to an end or deadlock,
        i.e. there are no messages to pass.

        A not-started algorithm is considered halted.

        :return: True if the algorithm is halted, False otherwise.
        :rtype: bool
        """
        if (
            len(self._network.network_outbox) > 0
            or any([len(node.outbox) for node in self.network.nodes()])
            or any([len(node.inbox) for node in self.network.nodes()])
        ):
            return False
        else:
            return True

    @property
    def network(self):
        """
        Get the network associated with the simulation.
        """
        return self._network

    @network.setter
    def network(self, network: Network):
        """
        Set the network for the simulation.

        :param network: The network object to set.
        :type network: Network

        :return: None
        :rtype: None

        """
        self._network.simulation = (
            None  # remove reference to this simulation in the old network
        )
        self._network = network
        self._network.simulation = self
        self.notify_observers("network_changed", self)


class QThreadObserver(AlgorithmObserver, SimulationObserver):
    def __init__(self, q_thread: QThread, *args, **kwargs) -> None:
        self.q_thread = q_thread
        super().__init__(*args, **kwargs)

    def on_step_done(self, algorithm: Algorithm) -> None:
        self.q_thread.emit(
            SIGNAL("updateLog(QString)"),
            "[{}] Step {} finished",
            algorithm.name,
            algorithm.network.algorithmState["step"],
        )

    def on_state_changed(self, simulation: Simulation) -> None:
        self.q_thread.emit(SIGNAL("redraw()"))

    def on_algorithm_finished(self, algorithm: Algorithm) -> None:
        self.q_thread.emit(
            SIGNAL("updateLog(QString)"), "[%s] Algorithm finished" % (algorithm.name)
        )

    def on_network_changed(self, simulation: Simulation) -> None:
        self.q_thread.emit(SIGNAL("updateLog(QString)"), "Network loaded")
        self.q_thread.emit(SIGNAL("redraw()"))
