import logging

from PySide6.QtCore import SIGNAL, QThread

from pydistsim.algorithm import Algorithm, NetworkAlgorithm, NodeAlgorithm
from pydistsim.logger import LogLevels
from pydistsim.network import Network


class Simulation(QThread):
    """
    Controls single network algorithm and node algorithms simulation.
    It is responsible for visualization and logging, also.
    """

    def __init__(
        self, network: Network, logLevel: LogLevels = LogLevels.DEBUG, **kwargs
    ):
        """
        Initialize a Simulation object.

        :param network: The network object representing the simulation network.
        :type network: Network
        :param logLevel: The log level for the simulation logger (default: LogLevels.DEBUG).
        :type logLevel: LogLevels
        :param kwargs: Additional keyword arguments.
        """
        assert isinstance(network, Network)
        self._network = network
        self._network.simulation = self
        self.stepsLeft = 0
        self.logger = logging.getLogger("pydistsim.simulation")
        self.logger.setLevel(logLevel)
        self.logger.debug("Simulation %s created successfully." % (hex(id(self))))
        QThread.__init__(self)

    def __del__(self):
        self.exiting = True
        self.wait()

    def run_all(self, stepping=False):
        """
        Run simulation from the beginning.

        :param stepping: A boolean indicating whether to run the simulation in stepping mode.
                         If True, the simulation will pause after running one step.
                         If False, the simulation will run continuously without pausing.

        :return: None
        """
        self.reset()
        self.logger.info("Simulation %s starts running." % hex(id(self)))
        if stepping:
            self.run(1)
            self.logger.info(
                "Simulation pause. Use sim.run(n) to continue n "
                "steps or sim.run() to continue without "
                "stepping."
            )
        else:
            self.run()
            self.logger.info("Simulation end.")

    def run(self, steps=0):
        """
        Run simulation from the current state.

        :param steps: Number of steps to run the simulation. If steps = 0, it runs until all algorithms are finished.
                      If steps > 0, the simulation is in stepping mode.
                      If steps > number of steps to finish the current algorithm, it finishes it.
        :type steps: int

        :return: None
        """
        self.stepsLeft = steps
        while True:
            algorithm = self.network.get_current_algorithm()
            if not algorithm:
                self.logger.info(
                    "Simulation has finished. There are no "
                    "algorithms left to run. "
                    "To run it from the start use sim.reset()."
                )
                self.emit(SIGNAL("redraw()"))
                break
            self.run_algorithm(algorithm)
            self.emit(SIGNAL("redraw()"))
            if self.stepsLeft >= 0:
                break

    def run_algorithm(self, algorithm: Algorithm):
        """
        Run the given algorithm on the given network.

        Update stepsLeft and network.algorithmState['step'].
        If stepsLeft hit 0 it may return unfinished.

        :param algorithm: The algorithm to run on the network.
        """
        if isinstance(algorithm, NetworkAlgorithm):
            self.stepsLeft -= 1
            algorithm.run()
        elif isinstance(algorithm, NodeAlgorithm):
            if self.network.algorithmState["step"] == 1:
                algorithm.initializer()
                if not self.network.outbox:
                    self.logger.warning("Initializer didn't send INI message")
            while not self.is_halted():
                self.stepsLeft -= 1
                self.network.communicate()
                for node in self.network.nodes_sorted():
                    nodeTerminated = algorithm.step(node)
                self.emit(
                    SIGNAL("updateLog(QString)"),
                    "[%s] Step %d finished"
                    % (algorithm.name, self.network.algorithmState["step"]),
                )
                self.logger.debug(
                    "[%s] Step %d finished"
                    % (algorithm.name, self.network.algorithmState["step"])
                )
                self.network.algorithmState["step"] += 1
                if nodeTerminated:
                    break
                if self.stepsLeft == 0:
                    return  # not finished
        self.emit(
            SIGNAL("updateLog(QString)"), "[%s] Algorithm finished" % (algorithm.name)
        )
        self.logger.debug("[%s] Algorithm finished" % (algorithm.name))
        self.network.algorithmState["finished"] = True
        return

    def run_step(self):
        """
        Run a single step of the simulation.

        :return: None
        """
        self.run(1)

    def reset(self):
        """
        Reset the simulation.

        :return: None
        """
        self.logger.info("Resetting simulation.")
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
            len(self._network.outbox) > 0
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
        self._network.simulation = None
        self._network = network
        self._network.simulation = self
        self.emit(SIGNAL("updateLog(QString)"), "Network loaded")
        self.emit(SIGNAL("redraw()"))
