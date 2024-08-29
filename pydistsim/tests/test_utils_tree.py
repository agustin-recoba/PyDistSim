import unittest

from pydistsim.network import CompleteRangeType, Network
from pydistsim.network.environment import Environment2D
from pydistsim.utils import tree, visualization


class TestNetwork(unittest.TestCase):
    tree_key = "T_KEY"

    def setUp(self):
        env = Environment2D()
        self.net = Network(rangeType=CompleteRangeType(env))
        self.net.environment.image[22, 22] = 0
        self.node1 = self.net.add_node(pos=[22.8, 21.8])
        self.node2 = self.net.add_node(pos=[21.9, 22.9])
        self.node3 = self.net.add_node(pos=[21.7, 21.7])

        self.node1.memory[self.tree_key] = {
            "parent": None,
            "children": [self.node2, self.node3],
        }
        self.node2.memory[self.tree_key] = {"parent": self.node1, "children": []}
        self.node3.memory[self.tree_key] = {"parent": self.node1, "children": []}

    def test_check_tree_key(self):
        """Test check_tree_key function."""
        tree.check_tree_key(self.net, self.tree_key)

    def test_get_root_node(self):
        """Test get_tree_root function."""
        root = tree.get_root_node(self.net, self.tree_key)
        assert root == self.node1, "Incorrect tree root"

    def test_not_tree_network(self):
        env = Environment2D()
        net = Network(rangeType=CompleteRangeType(env))

        with self.assertRaises(tree.TreeNetworkException):
            tree.check_tree_key(net, self.tree_key)

        net.environment.image[22, 22] = 0
        node1 = net.add_node(pos=[22.8, 21.8])
        node2 = net.add_node(pos=[21.9, 22.9])
        node3 = net.add_node(pos=[21.7, 21.7])
        with self.assertRaises(tree.Missingtree_key):
            tree.check_tree_key(net, self.tree_key)

        node1.memory[self.tree_key] = {
            "parent": None,
            "children": [node2, node3],
        }

        with self.assertRaises(tree.Missingtree_key):
            tree.check_tree_key(net, self.tree_key)

        node2.memory[self.tree_key] = {"parent": node1, "children": []}
        node3.memory[self.tree_key] = {"parent": node1, "children": []}

        tree.check_tree_key(net, self.tree_key)

    def test_visualization(self):
        """Test visualization functions."""
        visualization.show_mst(self.net, self.tree_key)

        env = Environment2D()
        net = Network(rangeType=CompleteRangeType(env))
        node1 = net.add_node(pos=[22.8, 21.8])

        node1.memory[self.tree_key] = {
            "parent": None,
            "children": [],
        }

        visualization.show_mst(net, self.tree_key)
