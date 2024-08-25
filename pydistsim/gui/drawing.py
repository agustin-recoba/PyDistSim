"""Drawing functions for visualizing the simulation."""

import math
from enum import StrEnum
from functools import reduce
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.axes import Axes
from matplotlib.collections import PatchCollection
from matplotlib.figure import Figure
from matplotlib.patches import Circle, RegularPolygon
from networkx import draw_networkx_edges, draw_networkx_labels

from pydistsim.algorithm.node_algorithm import NodeAlgorithm
from pydistsim.simulation import Simulation

if TYPE_CHECKING:
    from pydistsim.network.network import NetworkType


class MessageType(StrEnum):
    IN = "Inbox"
    OUT = "Outbox"
    TRANSIT = "Transit"
    LOST = "Lost"


MESSAGE_COLOR = {
    MessageType.IN: "tab:cyan",
    MessageType.OUT: "w",
    MessageType.TRANSIT: "y",
    MessageType.LOST: "r",
}


EDGES_ALPHA = 0.6
NODE_COLORS = [
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
    "tab:cyan",
] * 100

MESSAGE_SHAPE_ZORDER = 3
MESSAGE_ANNOTATION_ZORDER = 4


def __get_message_positions_and_orientation(
    source, destination, net: "NetworkType", direction: MessageType
) -> tuple[float, float, float]:
    xd, yd = net.pos[destination]
    xs, ys = net.pos[source]

    angle_in_rads = -math.pi / 2 + math.atan2(yd - ys, xd - xs)

    x = y = None
    if direction == MessageType.OUT:
        offset = 1 / 6
    elif direction == MessageType.IN:
        offset = 7 / 8
    elif direction == MessageType.TRANSIT:
        offset = 1 / 3
    elif direction == MessageType.LOST:
        offset_distance = 10

        xm = (xs + xd) / 2.0
        ym = (ys + yd) / 2.0

        if xs == xd:  # vertical line
            x = xm + offset_distance
            y = ym
        elif yd == ys:  # horizontal line
            x = xm
            y = ym + offset_distance
        else:  # diagonal line
            slope = (yd - ys) / (xd - xs)
            slope_perpendicular = -1 / slope
            x = xm + offset_distance / (slope_perpendicular**2 + 1) ** 0.5
            y = ym + offset_distance / (slope_perpendicular**2 + 1) ** 0.5 * slope_perpendicular

    if x is None:
        x = xs + (xd - xs) * offset
        y = ys + (yd - ys) * offset

    return x, y, angle_in_rads


def __draw_tree(treeKey: str, net: "NetworkType", axes: Axes):
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


def __draw_nodes(net, axes, node_colors={}, node_radius={}, radius_default=8.0):
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


def __create_and_get_color_labels(net, algorithm=None, subclusters=None, figure: Figure = None, show_messages=True):
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
            if figure:
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
                figure.legends = []
                figure.legend(
                    proxy,
                    labels,
                    loc="center right",
                    ncol=1,
                    bbox_to_anchor=(1, 0.8),
                    title="Statuses for %s:" % algorithm.name,
                )
                if show_messages:
                    # Message legend
                    figure.legend(
                        [
                            Circle(
                                color=MESSAGE_COLOR[msg],
                                **proxy_kwargs,
                            )
                            for msg in (
                                MessageType.IN,
                                MessageType.OUT,
                                MessageType.TRANSIT,
                                MessageType.LOST,
                            )
                        ],
                        ["Inbox", "Outbox", "Transit", "Lost"],
                        loc="center right",
                        ncol=1,
                        bbox_to_anchor=(1, 0.2),
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


def __draw_edges(net, axes):
    draw_networkx_edges(net, net.pos, alpha=EDGES_ALPHA, edgelist=None, ax=axes)


def __draw_messages(net: "NetworkType", axes: Axes, message_radius: float):
    MESSAGE_LINE_WIDTH = 1.0
    patch_kwargs = {
        "numVertices": 3,
        "radius": message_radius,
        "lw": MESSAGE_LINE_WIDTH,
        "ls": "solid",
        "picker": 3,
        "zorder": MESSAGE_SHAPE_ZORDER,
        "ec": "k",
    }

    msgCircles = []

    message_collection = {
        node: {
            MessageType.OUT: [
                ([msg.destination] if msg.destination is not None else list(net.adj[node].keys()))
                for msg in node.outbox
            ],
            MessageType.IN: [[msg.source] for msg in node.inbox],
            MessageType.TRANSIT: [
                [other_node for msg in net.get_transit_messages(node, other_node)]
                for other_node in net.out_neighbors(node)
                if net.get_transit_messages(node, other_node)
            ],
            MessageType.LOST: [
                [other_node for msg in net.get_lost_messages(node, other_node)]
                for other_node in net.out_neighbors(node)
                if net.get_lost_messages(node, other_node)
            ],
        }
        for node in net.nodes()
    }

    for node in message_collection:
        messages_type_dict = message_collection[node]

        msg_dict = {}
        for msg_type in messages_type_dict:
            dest_lists = messages_type_dict[msg_type]

            msg_dict[msg_type] = {}
            for dest in reduce(lambda x, y: x + y, dest_lists, []):
                if dest is None:
                    continue

                src = node if msg_type != MessageType.IN else dest
                dst = dest if msg_type != MessageType.IN else node

                count = msg_dict[msg_type].get((src, dst), 0)
                msg_dict[msg_type][(src, dst)] = count + 1

        for msg_type in msg_dict:
            for (src, dst), count in msg_dict[msg_type].items():
                if not src or not dst:
                    continue  # Defensive check

                x, y, rads_orientation = __get_message_positions_and_orientation(src, dst, net, msg_type)
                c = RegularPolygon(
                    (x, y),
                    orientation=rads_orientation,
                    **patch_kwargs,
                    fc=MESSAGE_COLOR[msg_type],
                    label=msg_type,
                )
                l = axes.annotate(
                    f"{count}",
                    (x + 5, y + 5),
                    color="k",
                    fontsize=8,
                    zorder=MESSAGE_ANNOTATION_ZORDER,
                )
                msgCircles.append(c)

    if msgCircles:
        message_collection = PatchCollection(msgCircles, match_original=True)
        message_collection.set_picker(3)
        axes.add_collection(message_collection)


def __draw_labels(net: "NetworkType", node_size, dpi):
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


def draw_current_state(
    sim: "Simulation",
    axes: Axes = None,
    clear: bool = True,
    treeKey: str = None,
    dpi: int = 100,
    node_radius: int = 10,
    show_messages=True,
):
    """
    Function to draw the current state of the simulation.
    Automatically determines the current algorithm and draws the network accordingly. This includes a mapping of
    node colors to the status of the nodes, as well as the messages in the network.

    :param sim: Simulation object
    :param axes: matplotlib axes object
    :param clear: boolean to clear the axes before drawing
    :param treeKey: key in nodes memory (dictionary) where tree data is stored
    :param dpi: dots per inch
    :param node_radius: radius of nodes
    :param show_messages: boolean to show messages in the network
    :return: matplotlib figure object
    """

    net = sim.network
    currentAlgorithm = sim.get_current_algorithm()

    if axes is None:
        with plt.ioff():
            fig = plt.figure()
            axes = fig.add_subplot(1, 1, 1)

    if clear:
        axes.clear()

    axes.imshow(net.environment.image, vmin=0, cmap="binary_r", origin="lower")

    if treeKey:
        __draw_tree(treeKey, net, axes)
    __draw_edges(net, axes)
    node_colors = __create_and_get_color_labels(
        net, algorithm=currentAlgorithm, figure=axes.figure, show_messages=show_messages
    )

    __draw_nodes(net, axes, node_colors, radius_default=node_radius)
    if show_messages:
        __draw_messages(net, axes, message_radius=3 * node_radius / 4)
    __draw_labels(net, node_radius, dpi)

    step_text = " (step %d)" % sim.algorithmState["step"] if isinstance(currentAlgorithm, NodeAlgorithm) else ""
    axes.set_title((currentAlgorithm.name if currentAlgorithm else "") + step_text)

    axes.axis("off")
    # remove as much whitespace as possible
    axes.figure.tight_layout()
    axes.figure.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)

    return axes.figure


def create_animation(
    sim: "Simulation",
    treeKey: str = None,
    figsize=None,
    dpi: int = 100,
    node_radius: int = 10,
    milliseconds_per_frame: int = 200,
    frame_limit: int = 2000,
) -> animation.FuncAnimation:
    """
    Create an animation of the simulation.

    Example for visualizing in Jupyter Notebook:

    .. code-block:: python

        anim = create_animation(sim)

        video = anim.to_html5_video()

        from IPython.display import HTML
        HTML(video)

    Example for saving as a video file:

    .. code-block:: python

        from matplotlib.animation import FFMpegFileWriter

        moviewriter = FFMpegFileWriter()
        anim = draw.create_animation(sim)

        anim.save("flood.mp4", writer=moviewriter)

    :param sim: Simulation object
    :param treeKey: key in nodes memory (dictionary) where tree data is stored
    :param dpi: dots per inch
    :param node_radius: radius of nodes
    :param milliseconds_per_frame: milliseconds per frame
    :param frame_limit: limit of frames, default is 2000
    :return: animation object
    """

    with plt.ioff():  # Turn off interactive mode
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = fig.add_subplot(111)

        def draw_frame(i):
            if i == 0:
                sim.reset()

            ax.clear()
            draw_current_state(sim, ax, treeKey=treeKey, dpi=dpi, node_radius=node_radius)
            sim.run(1)

            if sim.is_halted():
                return

            return

        def frame_count():
            count = 0
            while True:
                if frame_limit and count >= frame_limit:
                    break
                elif not sim.is_halted() or count == 0:
                    yield count
                    count += 1
                else:
                    break

        return animation.FuncAnimation(
            fig,
            func=draw_frame,
            frames=frame_count,
            interval=milliseconds_per_frame,
            blit=False,
            cache_frame_data=False,
        )
