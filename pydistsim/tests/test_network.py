import unittest

import pytest
from networkx import is_directed_acyclic_graph, is_weakly_connected

from pydistsim.algorithm import NodeAlgorithm
from pydistsim.network import (
    BidirectionalNetwork,
    BidirectionalRangeNetwork,
    CompleteRangeType,
    Network,
    NetworkException,
    NetworkType,
    Node,
    RangeNetwork,
    RangeType,
)
from pydistsim.network.environment import Environment2D
from pydistsim.utils.testing import PyDistSimTestCase
from pydistsim.utils.tree import check_tree_key


class TestDirectedNetwork(PyDistSimTestCase):
    nw_class = RangeNetwork

    def setUp(self):
        env = Environment2D()
        self.net = self.nw_class(rangeType=CompleteRangeType(env))
        self.net.environment.image[22, 22] = 0
        self.node1 = self.net.add_node(pos=[22.8, 21.8])
        self.node1.memory["test"] = 1
        self.node2 = self.net.add_node(pos=[21.9, 22.9])
        self.node2.memory["test"] = 2
        self.node3 = self.net.add_node(pos=[21.7, 21.7])
        self.node3.memory["test"] = 3
        self.node4 = self.net.add_node(pos=[23.7, 23.7])
        self.node4.memory["test"] = 4

        self.other_net = self.nw_class(rangeType=CompleteRangeType(env))
        self.node_in_other_net = self.other_net.add_node()

    def test_nodes(self):
        """Make sure the nodes are added."""
        assert isinstance(self.node1, Node)
        assert len(self.net.nodes()) == 4
        if isinstance(self.net.environment, Environment2D):
            assert self.net.environment._image.shape == (600, 600), "incorrect default size"

        assert isinstance(self.net.rangeType, RangeType)

        assert all(node.network == self.net for node in self.net.nodes())

    def test_visibility(self):
        """
        Pixel 22,22 is not space so node1 and node2 should not be visible
        but node3 is visible.
        """
        assert not self.net.environment.are_visible(self.net.pos[self.node1], self.net.pos[self.node2])

        assert self.net.environment.are_visible(self.net.pos[self.node2], self.net.pos[self.node3])

    def test_subnetwork(self):
        """Test subnetwork creation."""
        subnetwork: "NetworkType" = self.net.subnetwork([self.node1, self.node2])

        assert len(subnetwork.nodes()) == 2
        assert isinstance(subnetwork, type(self.net))

        for og_node in [self.node1, self.node2]:
            sn_node = [n for n in subnetwork if n.memory["test"] == og_node.memory["test"]][0]
            assert sn_node.network == subnetwork
            assert isinstance(sn_node, type(og_node))
            assert subnetwork.labels[sn_node] == str(sn_node._internal_id)
            assert subnetwork.ori[sn_node] == self.net.ori[og_node]
            assert all(subnetwork.pos[sn_node] == self.net.pos[og_node])

    def test_nodes_sorted(self):
        """Test sorting of nodes."""
        assert self.net.nodes_sorted() == [
            self.node1,
            self.node2,
            self.node3,
            self.node4,
        ]

    def test_remove_node(self):
        """Test node removal."""
        pos = self.net.pos[self.node1]
        original_len = len(self.net.nodes())

        print(f"Nodes ids pre-remove: {[node._internal_id for node in self.net.nodes()]}")
        self.net.remove_node(self.node1)
        print(f"Nodes ids post-remove: {[node._internal_id for node in self.net.nodes()]}")
        assert len(self.net.nodes()) == original_len - 1
        assert self.node1 not in self.net.nodes()

        with self.assertRaises(NetworkException):
            self.net.remove_node(self.node1)

        self.net.add_node(self.node1, pos=pos)

    def test_add_node_error_in_other_net(self):
        """Test adding node to network."""
        with self.assertRaises(NetworkException):
            self.net.add_node(self.node_in_other_net)

    def test_get_dic(self):
        """Test getting dictionary representation of the network."""
        dic = self.net.get_dic()
        assert "nodes" in dic
        assert "edges" in dic

    def test_get_tree_net(self):
        """Test getting tree representation of the network."""
        tree_key = "T_KEY"
        keepMemKey = "TEST_KEEP_MEM"

        self.node1.memory[tree_key] = {
            "parent": None,
            "children": [self.node2, self.node3],
        }
        self.node2.memory[tree_key] = {"parent": self.node1, "children": []}
        self.node2.memory[keepMemKey] = {"test": 1}
        self.node3.memory[tree_key] = {"parent": self.node1, "children": []}
        self.node4.memory[tree_key] = {"parent": None, "children": []}

        tree = self.net.get_tree_net(tree_key)

        assert isinstance(tree, self.nw_class)
        assert len(tree.nodes()) == 3
        assert len(self.net.nodes()) == 4
        assert tree.is_connected()
        assert (node.network == tree for node in tree.nodes())

        assert keepMemKey in self.node2.memory, "Memory should be kept"
        check_tree_key(self.net, tree_key)

    @pytest.mark.filterwarnings("ignore:No data for colormapping.*")
    def test_get_fig_runs(self):
        """Test getting figure of the network."""
        assert self.net.get_fig() is not None

        assert self.other_net.get_fig() is not None


class TestUnDirectedNetwork(TestDirectedNetwork):
    nw_class = BidirectionalRangeNetwork
