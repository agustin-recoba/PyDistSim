import unittest

from networkx import is_connected

from pymote.algorithm import NodeAlgorithm
from pymote.channeltype import ChannelType, Complete
from pymote.conf import settings
from pymote.environment import Environment2D
from pymote.network import Network, PymoteNetworkError
from pymote.node import Node
from pymote.utils import tree


class TestNetwork(unittest.TestCase):
    treeKey = "T_KEY"

    def setUp(self):
        env = Environment2D()
        self.net = Network(channelType=Complete(env))
        self.net.environment.im[22, 22] = 0
        self.node1 = self.net.add_node(pos=[22.8, 21.8])
        self.node2 = self.net.add_node(pos=[21.9, 22.9])
        self.node3 = self.net.add_node(pos=[21.7, 21.7])

        self.net.algorithms = (NodeAlgorithm,)

        self.node1.memory[self.treeKey] = {
            "parent": None,
            "children": [self.node2, self.node3],
        }
        self.node2.memory[self.treeKey] = {"parent": self.node1, "children": []}
        self.node3.memory[self.treeKey] = {"parent": self.node1, "children": []}

    def test_check_tree_key(self):
        """Test check_tree_key function."""
        tree.check_tree_key(self.net, self.treeKey)

    def test_get_root_node(self):
        """Test get_tree_root function."""
        root = tree.get_root_node(self.net, self.treeKey)
        assert root == self.node1, "Incorrect tree root"

    def test_get_path(self):
        """Test get_path function."""
        path = tree.get_path(self.node1, self.node3, self.treeKey)
        assert path == [self.node1, self.node3], "Incorrect path"

        path2 = tree.get_path(self.node2, self.node3, self.treeKey)
        assert path2 == [self.node2, self.node1, self.node3], "Incorrect path"

    def test_get_path_no_path(self):
        """Test get_path function when there is no path."""
        self.node4 = self.net.add_node(pos=[21.7, 21.7])
        self.node4.memory[self.treeKey] = {"parent": None, "children": []}

        path = tree.get_path(self.node1, self.node4, self.treeKey)
        assert path == [], "Incorrect path"

        self.net.remove_node(self.node4)

    def test_change_root_node(self):
        """Test change_root_node function."""
        tree.change_root_node(self.net, self.node2, self.treeKey)
        root = tree.get_root_node(self.net, self.treeKey)
        assert root == self.node2, "Incorrect tree root"
