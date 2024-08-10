import unittest

import scipy.stats

from pydistsim.network import Network, Node
from pydistsim.network.sensor import DistSensor, SensorError


class TestSensor(unittest.TestCase):

    def test_read(self):
        """Test read compositeSensor"""
        net = Network()
        node = net.add_node()
        node.compositeSensor.read()

    def test_set_compositeSensor(self):
        """Test setting compositeSensors on a node"""
        node = Node()
        dist_sensor = DistSensor({"pf": scipy.stats.norm, "scale": 10})
        node.compositeSensor = ("AoASensor", dist_sensor)
        self.assertRaises(SensorError, node.compositeSensor.read)

        net = Network()
        node = net.add_node()
        dist_sensor = DistSensor({"pf": scipy.stats.norm, "scale": 10})
        node.compositeSensor = ("AoASensor", dist_sensor)
        self.assertTrue(len(node.compositeSensor.sensors) == 2)
        readings = node.compositeSensor.read()
        self.assertTrue("AoA" in list(readings.keys()) and "Dist" in list(readings.keys()))

        # TODO: check normal distribution
