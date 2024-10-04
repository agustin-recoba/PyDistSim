"""
Sensors provide a way for node to interact with its environment.

Sensors can also be used to satisfy algorithm prerequisites.

Generally sensors should incorporate some model of measurement insecurity that
is inherent in real world sensors. This is implemented as a
:class:`ProbabilityFunction`.

Basic usage:

>>> node.compositeSensor = ('DistSensor','AoASensor')
>>> node.compositeSensor.sensors
(<pydistsim.network.sensor.DistSensor at 0x6d3fbb0>,
 <pydistsim.network.sensor.AoASensor at 0x6d3f950>)

To manually set sensor parameters first make an sensor instance:

>>> import scipy.stats
>>> aoa_sensor = AoASensor({'pf': scipy.stats.norm, 'scale': 10*pi/180 })
>>> node.compositeSensor = (aoa_sensor,)

"""

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING

from numpy import arctan2, pi, sqrt
from scipy.stats import rv_continuous, rv_discrete

if TYPE_CHECKING:
    from pydistsim.network import Node


class Sensor(ABC):
    """
    Abstract base class for all Sensors.

    Sensor provides a certain capability for a node, providing information about
    the outside world. It could be a capability to detect neighbors, measure
    distance to them, or retrieve the environment temperature.

    :param dict_args: A dictionary containing the scale and probability function.
    :type dict_args: dict
    :param scale: The scale parameter for the probability function.
    :type scale: float
    :param pf: The probability function (e.g. :py:data:`scipy.stats.norm`).
    :type pf: rv_continuous or rv_discrete
    """

    def __init__(self, dict_args=None, /, scale=None, pf: rv_continuous | rv_discrete = None):
        if dict_args:
            scale = dict_args.get("scale")
            pf = dict_args.get("pf")

        if pf and scale:
            self.probabilityFunction = ProbabilityFunction(scale, pf)
        else:
            self.probabilityFunction = None

    @classmethod
    def name(cls):
        """
        Get the name of the Sensor class.

        :return: The name of the Sensor class.
        :rtype: str
        """
        return cls.__name__

    @abstractmethod
    def read(self) -> dict:
        """
        Read the sensor data.

        This method should be overridden in a subclass.

        :return: The sensor data.
        :rtype: dict
        """
        pass


def node_in_network(fun: Callable):
    """Decorator function that checks if node is in network.

    :param fun: The function to be decorated.
    :type fun: Callable
    :return: The decorated function.
    :rtype: Callable
    """

    @wraps(fun)
    def f(sensor: Sensor, node: "Node"):
        if not node.network:
            raise SensorError("Cannot take a sensor reading if node is outside of a network.")
        return fun(sensor, node)

    return f


class AoASensor(Sensor):
    """
    Provides azimuth between node and its neighbors.

    This sensor calculates the azimuth angle between a node and its neighbors in a network.
    It uses the position and orientation information of the nodes to calculate the azimuth angle.
    """

    @node_in_network
    def read(self, node: "Node"):
        """
        Reads the azimuth angle between a node and its neighbors.

        :param node: The node for which to calculate the azimuth angle.
        :type node: Node
        :return: A dictionary containing the azimuth angle measurements between the node and its neighbors.
        :rtype: dict
        """
        network = node.network
        measurements = {}
        p = network.pos[node]
        o = network.ori[node]
        for neighbor in network.neighbors(node):
            v = network.pos[neighbor] - p
            measurement = (arctan2(v[1], v[0]) - o) % (2 * pi)
            measurement = self.probabilityFunction.getNoisyReading(measurement)
            measurements.update({neighbor: measurement})
        return {"AoA": measurements}


class DistSensor(Sensor):
    """Provides distance between node and its neighbors."""

    @node_in_network
    def read(self, node: "Node"):
        """
        Read the distances from the current node to its neighbors.

        :param node: The current node.
        :type node: Node
        :return: A dictionary containing the distances to the neighbors.
        :rtype: dict
        """
        network = node.network
        measurements = {}
        p = network.pos[node]
        for neighbor in network.neighbors(node):
            pn = network.pos[neighbor]
            measurement = sqrt(sum(pow(p - pn, 2)))
            measurement = self.probabilityFunction.getNoisyReading(measurement)
            measurements.update({neighbor: measurement})
        return {"Dist": measurements}


class TruePosSensor(Sensor):
    """Provides node's true position."""

    @node_in_network
    def read(self, node: "Node"):
        """
        Read the sensor data from the given node.

        :param node: The node from which to read the sensor data.
        :type node: Node

        :return: A dictionary containing the sensor data.
        :rtype: dict
        """
        return {"TruePos": node.network.pos[node]}


class CompositeSensor:
    """
    Wrap multiple sensors, coalesce results and return composite readout.

    This class is not a sensor itself, i.e. subclass of :class:`Sensor`,
    instead it serves as a placeholder for multiple sensors that can be
    attached to a :class:`Node`.


    :param node: The Node that has this composite sensor attached to.
    :type node: Node
    :param componentSensors: Tuple of Sensor subclasses or their class names.
    :type componentSensors: tuple[type[Sensor] | str]
    """

    def __init__(self, node: "Node", componentSensors: tuple[type[Sensor] | str] | None = None):
        self.node = node
        self._sensors = ()
        self.sensors = componentSensors or ()

    @property
    def sensors(self) -> tuple[Sensor]:
        """
        Get the sensors associated with the object.

        :return: A tuple of Sensor objects.
        """
        return self._sensors

    @sensors.setter
    def sensors(self, sensors: tuple[type[Sensor] | str]):
        self._sensors: tuple[Sensor] = ()
        # instantiate sensors passed by class name
        for cls in Sensor.__subclasses__():
            if cls.__name__ in sensors:
                self._sensors += (cls(),)
        # instantiate sensors passed by class
        for cls in sensors:
            if inspect.isclass(cls) and issubclass(cls, Sensor):
                self._sensors += (cls(),)
        # add sensors that are already instantiated
        for sensor in sensors:
            if isinstance(sensor, Sensor):
                self._sensors += (sensor,)

    def get_sensor(self, name: str) -> Sensor:
        """
        Get a sensor by its name.

        :param name: The name of the sensor.
        :type name: str
        :return: The sensor object.
        :rtype: Sensor
        :raises SensorError: If multiple or no sensors are found with the given name.
        """
        sensor = [s for s in self._sensors if s.name() == name]
        if len(sensor) != 1:
            raise SensorError("Multiple or no sensors found with name %s" % name)
        return sensor[0]

    def read(self):
        """
        Read measurements from all sensors.

        :return: A dictionary containing the measurements from all sensors.
        :rtype: dict
        """
        measurements = {}
        for sensor in self._sensors:
            measurements.update(sensor.read(self.node))
        return measurements


class ProbabilityFunction:
    """
    Provides a way to get noisy reading.

    :param scale: The scale parameter for the probability function.
    :type scale: float

    :param pf: The probability function (e.g. :py:data:`scipy.stats.norm`).
    :type pf: rv_continuous or rv_discrete
    """

    def __init__(self, scale, pf: rv_continuous | rv_discrete):
        self.pf = pf  # class or gen object
        self.name = self.pf.__class__.__name__
        self.scale = scale

    def getNoisyReading(self, value):
        return self.pf.rvs(scale=self.scale, loc=value)


class SensorError(Exception):
    pass
