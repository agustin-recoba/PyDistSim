from typing import TYPE_CHECKING

from pydistsim.gui.drawing import NODE_COLORS
from pydistsim.utils.tree import get_root_node

if TYPE_CHECKING:
    from pydistsim.network import NetworkType


def show_mst(net: "NetworkType", tree_key="mst"):
    """
    Show tree representation of network.

    :param net: network to show
    :param tree_key: key in nodes memory (dictionary) where parent and
               children data is stored in format:
                {'parent': parent_node,
                 'children': [child_node1, child_node2 ...]}
    """
    nodesToCheck = [(get_root_node(net, tree_key), 0)]
    edgelist = []
    levels = {}  # level of node in tree, root is 0
    while nodesToCheck:
        (node, level) = nodesToCheck.pop()
        edgelist += [(node, child.unbox()) for child in node.memory[tree_key]["children"]]
        levels[node] = NODE_COLORS[level]
        nodesToCheck += [(child.unbox(), level + 1) for child in node.memory[tree_key]["children"]]
    net.show(edge_filter=edgelist, node_colors=levels)
    from matplotlib.pyplot import gca

    gca().set_title("Minimum spanning tree in memory['%s']" % tree_key)
