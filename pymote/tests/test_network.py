import unittest

import pytest
from networkx import is_connected
from pydistsim.algorithm import NodeAlgorithm
from pydistsim.channeltype import ChannelType, Complete
from pydistsim.conf import settings
from pydistsim.environment import Environment2D
from pydistsim.network import Network, PyDistSimNetworkError
from pydistsim.node import Node
from pydistsim.utils.tree import check_tree_key


class TestNetwork(unittest.TestCase):

    def setUp(self):
        env = Environment2D()
        self.net = Network(channelType=Complete(env))
        self.net.environment.im[22, 22] = 0
        self.node1 = self.net.add_node(pos=[22.8, 21.8])
        self.node2 = self.net.add_node(pos=[21.9, 22.9])
        self.node3 = self.net.add_node(pos=[21.7, 21.7])

        self.net.algorithms = (NodeAlgorithm,)

        self.other_net = Network(channelType=Complete(env))
        self.node_in_other_net = self.other_net.add_node()

    def test_nodes(self):
        """Make sure the nodes are added."""
        assert isinstance(self.node1, Node)
        assert len(self.net.nodes()) == 3
        if isinstance(self.net.environment, Environment2D):
            assert (
                self.net.environment.im.shape == settings.ENVIRONMENT2D_SHAPE
            ), "incorrect default size"

        assert isinstance(self.net.channelType, ChannelType)

        assert all(node.network == self.net for node in self.net.nodes())

    def test_visibility(self):
        """
        Pixel 22,22 is not space so node1 and node2 should not be visible
        but node3 is visible.
        """
        assert not self.net.environment.are_visible(
            self.net.pos[self.node1], self.net.pos[self.node2]
        )

        assert self.net.environment.are_visible(
            self.net.pos[self.node2], self.net.pos[self.node3]
        )

    def test_subnetwork(self):
        """Test subnetwork creation."""
        subnetwork: Network = self.net.subnetwork([self.node1, self.node2])

        assert len(subnetwork.nodes()) == 2
        assert (
            subnetwork._algorithms_param == self.net._algorithms_param
        )  # compare the algorithms classes and their parameters

        assert (
            subnetwork.algorithms != self.net.algorithms
        )  # compare algorithm instances

        assert all(
            algo1.network == subnetwork and algo2.network == self.net
            for (algo1, algo2) in zip(subnetwork.algorithms, self.net.algorithms)
        )  # compare algorithm network

        assert len(subnetwork.outbox) == 0
        assert subnetwork.networkRouting == self.net.networkRouting

        for node in [self.node1, self.node2]:
            node_in_subnetwork = subnetwork.node_by_id(node.id)
            assert all(subnetwork.pos[node_in_subnetwork] == self.net.pos[node])
            assert subnetwork.ori[node_in_subnetwork] == self.net.ori[node]
            assert subnetwork.labels[node_in_subnetwork] == self.net.labels[node]
            assert node_in_subnetwork.network == subnetwork

    def test_nodes_sorted(self):
        """Test sorting of nodes."""
        assert self.net.nodes_sorted() == [self.node1, self.node2, self.node3]

    def test_remove_node(self):
        """Test node removal."""
        pos = self.net.pos[self.node1]

        print(f"Nodes ids pre-remove: {[node.id for node in self.net.nodes()]}")
        self.net.remove_node(self.node1)
        print(f"Nodes ids post-remove: {[node.id for node in self.net.nodes()]}")
        assert len(self.net.nodes()) == 2
        assert self.node1 not in self.net.nodes()

        with self.assertLogs(level="ERROR"):
            with self.assertRaises(PyDistSimNetworkError):
                self.net.remove_node(self.node1)

        self.net.add_node(self.node1, pos=pos)

    def test_add_node_error_in_other_net(self):
        """Test adding node to network."""
        with self.assertRaises(PyDistSimNetworkError):
            self.net.add_node(self.node_in_other_net)

    def test_get_current_algorithm(self):
        """Test getting current algorithm."""
        assert isinstance(self.net.get_current_algorithm(), NodeAlgorithm)

        self.net.algorithms = ()

        with self.assertLogs(level="ERROR"):
            with self.assertRaises(PyDistSimNetworkError):
                self.net.get_current_algorithm()

        self.net.algorithms = (NodeAlgorithm,)

    def test_get_dic(self):
        """Test getting dictionary representation of the network."""
        dic = self.net.get_dic()
        assert "nodes" in dic
        assert "algorithms" in dic
        assert "algorithmState" in dic

    def test_get_tree_net(self):
        """Test getting tree representation of the network."""
        treeKey = "T_KEY"

        self.node1.memory[treeKey] = {
            "parent": None,
            "children": [self.node2, self.node3],
        }
        self.node2.memory[treeKey] = {"parent": self.node1, "children": []}
        self.node3.memory[treeKey] = {"parent": self.node1, "children": []}

        check_tree_key(self.net, treeKey)

        tree = self.net.get_tree_net(treeKey)

        assert isinstance(tree, Network)
        assert len(tree.nodes()) == 3
        assert is_connected(tree)
        assert (node.network == tree for node in tree.nodes())

    @pytest.mark.filterwarnings("ignore:No data for colormapping.*")
    def test_get_fig_runs(self):
        """Test getting figure of the network."""
        assert self.net.get_fig() is not None

        assert self.other_net.get_fig() is not None
