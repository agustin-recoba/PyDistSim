"""
Set of utils that operate on network nodes when they have defined tree
in their memory under tree_key key.
tree_key -- key in node memory (dictionary) where parent and
           children data is stored in format:
           {'parent': parent_node,
            'children': [child_node1, child_node2 ...]}
"""

from typing import TYPE_CHECKING, Union

from pydistsim.algorithm.node_wrapper import NeighborLabel, NodeAccess

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType
    from pydistsim.network.node import Node

NodeType = Union["Node", "NodeAccess", "NeighborLabel"]


def get_root_node(net: "NetworkType", tree_key: str = "mst") -> NodeType:
    """
    Return root node in network tree.
    """
    check_tree_key(net, tree_key)

    node = net.nodes_sorted()[0]
    while node.memory[tree_key]["parent"] and node.memory[tree_key]["parent"].unbox() in net.nodes():
        node = node.memory[tree_key]["parent"].unbox()
    return node


def check_tree_key(net: "NetworkType", tree_key: str):
    if len(net.nodes()) == 0:
        raise TreeNetworkException("Network has no nodes.")

    for node in net.nodes():
        if tree_key not in node.memory:
            raise Missingtree_key(tree_key)


class TreeNetworkException(Exception):
    pass


class Missingtree_key(TreeNetworkException):
    def __init__(self, tree_key):
        self.tree_key = tree_key

    def __str__(self):
        return "At least one node is missing '%s' key in memory." % self.tree_key
