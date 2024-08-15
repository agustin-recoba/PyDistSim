from enum import StrEnum
from typing import Literal, Tuple

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.collections import PatchCollection
from matplotlib.figure import Figure
from matplotlib.patches import Circle, RegularPolygon
from networkx import draw_networkx_edges, draw_networkx_labels

from pydistsim.algorithm.node_algorithm import NodeAlgorithm
from pydistsim.message import Message
from pydistsim.network.network import NetworkType
from pydistsim.simulation import Simulation


class MessageType(StrEnum):
    IN = "Inbox"
    OUT = "Outbox"
    TRANSIT = "Transit"
    LOST = "Lost"


MESSAGE_COLOR = {
    MessageType.IN: "k",
    MessageType.OUT: "w",
    MessageType.TRANSIT: "y",
    MessageType.LOST: "r",
}


EDGES_ALPHA = 0.6
NODE_COLORS = "bgrcmy" * 100


def get_message_positions(message: "Message", net: "NetworkType", direction: MessageType) -> tuple[float, float]:
    xd, yd = net.pos[message.destination]
    try:
        xs, ys = net.pos[message.source]
    except KeyError:
        return (xd, yd)
    x = (xs + xd) / 2.0  # middle point
    y = (ys + yd) / 2.0
    if direction == MessageType.OUT:
        x = (xs + x) / 2.0  # one quarter from source
        y = (ys + y) / 2.0
        x = (xs + x) / 2.0  # one eighth from source
        y = (ys + y) / 2.0
    elif direction == MessageType.IN:
        x = (xd + x) / 2.0  # one quarter from destination
        y = (yd + y) / 2.0
        x = (xd + x) / 2.0  # one eighth from destination
        y = (yd + y) / 2.0
    elif direction == MessageType.TRANSIT:
        ...
    elif direction == MessageType.LOST:
        ...
    return (x, y)


def draw_current_state(
    sim: "Simulation",
    axes: Axes,
    clear: bool = True,
    treeKey: str = None,
    dpi: int = 100,
    node_radius: int = 10,
):
    net = sim.network
    currentAlgorithm = sim.get_current_algorithm()
    if clear:
        axes.clear()

    axes.imshow(net.environment.image, vmin=0, cmap="binary_r", origin="lower")

    draw_tree(treeKey, net, axes)
    draw_edges(net, axes)
    node_colors = get_node_colors(net, algorithm=currentAlgorithm, figureAddLegends=axes.figure)

    draw_nodes(net, axes, node_colors, radius_default=node_radius)
    draw_messages(net, axes, message_radius=node_radius / 2)
    draw_labels(net, node_radius, dpi)
    step_text = " (step %d)" % sim.algorithmState["step"] if isinstance(currentAlgorithm, NodeAlgorithm) else ""
    axes.set_title((currentAlgorithm.name if currentAlgorithm else "") + step_text)
    axes.axis("off")


def draw_tree(treeKey: str, net: "NetworkType", axes: Axes):
    """
    Show tree representation of network.

    Attributes:
        treeKey (str):
            key in nodes memory (dictionary) where tree data is stored
            storage format can be a list off tree neighbors or a dict:
                {'parent': parent_node,
                    'children': [child_node1, child_node2 ...]}
    """
    treeNet = net.get_tree_net(treeKey)
    if treeNet:
        draw_networkx_edges(
            treeNet,
            treeNet.pos,
            treeNet.edges(),
            width=1.8,
            alpha=EDGES_ALPHA,
            ax=axes,
        )


def draw_nodes(net, axes, node_colors={}, node_radius={}, radius_default=8.0):
    if isinstance(node_colors, str):
        node_colors = {node: node_colors for node in net.nodes()}
    nodeCircles = []
    for n in net.nodes():
        c = Circle(
            tuple(net.pos[n]),
            node_radius.get(n, radius_default),
            color=node_colors.get(n, "r"),
            ec="k",
            lw=1.0,
            ls="solid",
            picker=3,
        )
        nodeCircles.append(c)
    node_collection = PatchCollection(nodeCircles, match_original=True)
    node_collection.set_picker(3)
    axes.add_collection(node_collection)
    return node_collection


def get_node_colors(net, algorithm=None, subclusters=None, figureAddLegends: Figure = None):
    proxy_kwargs = {
        "xy": (0, 0),
        "radius": 8.0,
        "ec": "k",
        "lw": 1.0,
        "ls": "solid",
    }

    node_colors = {}
    if algorithm:
        color_map = {}
        if isinstance(algorithm, NodeAlgorithm):
            for ind, status in enumerate(algorithm.Status.__members__):
                color_map.update({status: NODE_COLORS[ind]})
            if figureAddLegends:
                # Node status legend
                proxy = []
                labels = []
                for status, color in list(color_map.items()):
                    proxy.append(
                        Circle(
                            color=color,
                            **proxy_kwargs,
                        )
                    )
                    labels.append(status)
                figureAddLegends.legends = []
                figureAddLegends.legend(
                    proxy,
                    labels,
                    loc="center right",
                    ncol=1,
                    bbox_to_anchor=(1, 0.2),
                    title="Statuses for %s:" % algorithm.name,
                )
                # Message legend
                figureAddLegends.legend(
                    [
                        Circle(
                            color=MESSAGE_COLOR[msg],
                            **proxy_kwargs,
                        )
                        for msg in (MessageType.IN, MessageType.OUT, MessageType.TRANSIT, MessageType.LOST)
                    ],
                    ["Inbox", "Outbox", "Transit", "Lost"],
                    loc="center right",
                    ncol=1,
                    bbox_to_anchor=(1, 0.8),
                    title="Messages:",
                )
                plt.subplots_adjust(left=0.1, bottom=0.1, right=0.99)

        for n in net.nodes():
            if n.status == "" or n.status not in list(color_map.keys()):
                node_colors[n] = "r"
            else:
                node_colors[n] = color_map[n.status]
    elif subclusters:
        for i, sc in enumerate(subclusters):
            for n in sc:
                if n in node_colors:
                    node_colors[n] = "k"
                else:
                    node_colors[n] = NODE_COLORS[i]
    return node_colors


def draw_edges(net, axes):
    draw_networkx_edges(net, net.pos, alpha=EDGES_ALPHA, edgelist=None, ax=axes)


def draw_messages(net: "NetworkType", axes: Axes, message_radius: float):
    MESSAGE_LINE_WIDTH = 1.0
    kwargs = {
        "numVertices": 4,
        "radius": message_radius,
        "lw": MESSAGE_LINE_WIDTH,
        "ls": "solid",
        "picker": 3,
        "zorder": 3,
        "ec": "k",
    }

    messages = []
    msgCircles = []
    for node in net.nodes():
        for msg in node.outbox:
            # broadcast
            if msg.destination is None:
                for neighbor in list(net.adj[node].keys()):
                    nbr_msg = msg.copy()
                    nbr_msg.destination = neighbor
                    c = RegularPolygon(
                        get_message_positions(nbr_msg, net, MessageType.OUT),
                        color=MESSAGE_COLOR[MessageType.OUT],
                        **kwargs,
                    )
                    messages.append(nbr_msg)
                    msgCircles.append(c)
            else:
                c = RegularPolygon(
                    get_message_positions(msg, net, MessageType.OUT),
                    color=MESSAGE_COLOR[MessageType.OUT],
                    **kwargs,
                )
                messages.append(msg)
                msgCircles.append(c)
        for msg in node.inbox:
            c = RegularPolygon(
                get_message_positions(msg, net, MessageType.IN),
                color=MESSAGE_COLOR[MessageType.IN],
                **kwargs,
            )
            messages.append(msg)
            msgCircles.append(c)
        for other_node in net.out_neighbors(node):
            for msg in net.transit_messages(node, other_node):
                c = RegularPolygon(
                    get_message_positions(msg, net, MessageType.TRANSIT),
                    color=MESSAGE_COLOR[MessageType.TRANSIT],
                    **kwargs,
                )
                messages.append(msg)
                msgCircles.append(c)
            for msg in net.get_lost_messages(node, other_node):
                c = RegularPolygon(
                    get_message_positions(msg, net, MessageType.LOST),
                    color=MESSAGE_COLOR[MessageType.LOST],
                    **kwargs,
                )
                messages.append(msg)
                msgCircles.append(c)

    if messages:
        message_collection = PatchCollection(msgCircles, match_original=True)
        message_collection.set_picker(3)
        axes.add_collection(message_collection)


def draw_labels(net: "NetworkType", node_size, dpi):
    label_pos = {}
    from math import sqrt

    label_delta = 1.5 * sqrt(node_size) * dpi / 100
    for n in net.nodes():
        label_pos[n] = net.pos[n].copy() + label_delta
    draw_networkx_labels(
        net,
        label_pos,
        labels=net.labels,
        horizontalalignment="left",
        verticalalignment="bottom",
    )
