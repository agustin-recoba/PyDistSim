"""Drawing functions for visualizing the simulation."""

import math
from collections.abc import Callable
from enum import StrEnum
from functools import cache, reduce
from typing import TYPE_CHECKING, Any, Union

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.figure import Figure
from matplotlib.patches import Circle, RegularPolygon
from networkx import draw_networkx_edges as __d_netx_edges
from networkx import draw_networkx_labels as __d_netx_labels
from numpy import uint8, zeros

from pydistsim._exceptions import SimulationException
from pydistsim.algorithm.node_algorithm import NodeAlgorithm
from pydistsim.logging import logger
from pydistsim.simulation import Simulation

if TYPE_CHECKING:
    from pydistsim.message import Message
    from pydistsim.network.network import NetworkType
    from pydistsim.network.node import Node


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


def __get_message_positions_and_orientation(xd, yd, xs, ys, direction: MessageType) -> tuple[float, float, float]:

    angle_in_rads = -math.pi / 2 + math.atan2(yd - ys, xd - xs)

    x = y = None
    if direction == MessageType.OUT:
        offset = 1 / 6
    elif direction == MessageType.IN:
        offset = 7 / 8
    elif direction == MessageType.TRANSIT:
        offset = 1 / 3
    elif direction == MessageType.LOST:
        offset_distance = 10 * (-1 if angle_in_rads < 0 else 1)

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


def __draw_tree(tree_key: str, net: "NetworkType", axes: Axes):
    """
    Show tree representation of network.

    Attributes:
        tree_key (str):
            key in nodes memory (dictionary) where tree data is stored
            storage format can be a list off tree neighbors or a dict:
                {'parent': parent_node,
                    'children': [child_node1, child_node2 ...]}
    """
    (nodes, edges) = net.get_tree_net(tree_key, return_subnetwork=False)
    if nodes:
        __d_netx_edges(
            net,
            net.pos,
            edges,
            edge_color="tab:brown",
            width=2.5,
            alpha=EDGES_ALPHA + 0.2,
            ax=axes,
        )


@cache
def __draw_nodes(node_pos_color: tuple[tuple[int, tuple[float, ...], str]], fig_id=0) -> PatchCollection:
    nodeCircles = []
    for radius, pos, color in node_pos_color:
        c = Circle(
            pos,
            radius,
            color=color,
            ec="k",
            lw=1.0,
            ls="solid",
            picker=3,
        )
        nodeCircles.append(c)
    node_collection = PatchCollection(nodeCircles, match_original=True)
    node_collection.set_picker(3)

    return node_collection


@cache
def __create_figure_legend(color_map: tuple, algorithm_name: str, show_messages: bool, fig_id=0):
    proxy_kwargs = {
        "xy": (0, 0),
        "radius": 8.0,
        "ec": "k",
        "lw": 1.0,
        "ls": "solid",
    }

    # Node status legend
    proxy = []
    labels = []
    for status, color in color_map:
        proxy.append(
            Circle(
                color=color,
                **proxy_kwargs,
            )
        )
        labels.append(status)

    legends = []
    legends += [
        plt.gcf().legend(
            proxy,
            labels,
            loc="outside right upper",
            fontsize=9,
            ncol=1,
            # bbox_to_anchor=(1.6, 0.75),
            title="Statuses for\n%s:" % algorithm_name,
        )
    ]

    if show_messages:
        # Message legend
        legends += [
            plt.gcf().legend(
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
                loc="outside right lower",
                ncol=1,
                # bbox_to_anchor=(1.5, 0.2),
                fontsize=9,
                title="Messages:",
            )
        ]

    return legends


def __create_and_get_color_labels(net, algorithm=None, subclusters=None, figure: Figure = None, show_messages=True):
    node_colors = {}
    if algorithm:
        color_map = {}
        if isinstance(algorithm, NodeAlgorithm):
            for ind, status in enumerate(algorithm.Status.__members__):
                color_map.update({status: NODE_COLORS[ind]})
            if figure:
                figure.legends = __create_figure_legend(
                    tuple(color_map.items()), algorithm.name, show_messages, id(figure)
                )

        for n in net.nodes():
            if n.status == "" or n.status not in list(color_map.keys()):
                node_colors[n] = "k"
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


def __draw_edges(net, edges, axes) -> LineCollection:
    return __d_netx_edges(net, net.pos, alpha=EDGES_ALPHA, edgelist=edges, ax=axes)


def __draw_messages(
    net: "NetworkType", axes: Axes, message_colors: Callable[["Message", MessageType], Any], message_radius: float
):
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

    msg_artists = []

    message_collection = {
        node: {
            MessageType.OUT: [
                ([(msg, msg.destination)] if msg.destination is not None else list(net.adj[node].keys()))
                for msg in node.outbox
            ],
            MessageType.IN: [[(msg, msg.source)] for msg in node.inbox],
            MessageType.TRANSIT: [
                [(msg, other_node) for msg in net.get_transit_messages(node, other_node) if msg.source == node]
                for other_node in net.out_neighbors(node)
                if net.get_transit_messages(node, other_node)
            ],
            MessageType.LOST: [
                [(msg, other_node) for msg in net.get_lost_messages(node, other_node) if msg.source == node]
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
            for msg, dest in reduce(lambda x, y: x + y, dest_lists, []):
                if dest is None:
                    continue

                src = node if msg_type != MessageType.IN else dest
                dst = dest if msg_type != MessageType.IN else node

                count, msgs = msg_dict[msg_type].get((src, dst), (0, []))
                msgs.append(msg)
                msg_dict[msg_type][(src, dst)] = count + 1, msgs

        for msg_type in msg_dict:
            for (src, dst), (count, msgs) in msg_dict[msg_type].items():
                if not src or not dst:
                    continue  # Defensive check

                x, y, rads_orientation = __get_message_positions_and_orientation(*net.pos[dst], *net.pos[src], msg_type)

                triangle_artist = RegularPolygon(
                    (x, y),
                    orientation=rads_orientation,
                    **patch_kwargs,
                    fc=MESSAGE_COLOR[msg_type] if not message_colors else message_colors(msgs[0], msg_type),
                    label=msg_type,
                )

                if count > 1:
                    axes.annotate(
                        f"{count}",
                        (x + 5, y + 5),
                        color="k",
                        fontsize=8,
                        zorder=MESSAGE_ANNOTATION_ZORDER,
                    )
                msg_artists.append(triangle_artist)

    if msg_artists:
        message_collection = PatchCollection(msg_artists, match_original=True)
        message_collection.set_picker(3)
        axes.add_collection(message_collection)


def __draw_labels(net: "NetworkType", node_size, dpi) -> dict["Node", plt.Text]:
    label_pos = {}
    from math import sqrt

    if not callable(node_size):
        label_delta = 1.5 * sqrt(node_size) * dpi / 100
    for n in net.nodes():
        if callable(node_size):
            label_delta = 1.5 * sqrt(node_size(n)) * dpi / 100
        label_pos[n] = net.pos[n].copy() + label_delta

    return __d_netx_labels(
        net,
        label_pos,
        labels=net.labels,
        horizontalalignment="left",
        verticalalignment="bottom",
    )


def draw_current_state(
    sim: Union["Simulation", "NetworkType"],
    axes: Axes = None,
    clear: bool = True,
    tree_key: str = None,
    dpi: int = 100,
    node_radius: int | Callable[["Node"], int] = 10,
    node_positions: dict | Callable[[], dict["Node", tuple[float, ...]]] = None,
    node_colors: dict | Callable[[], dict["Node", Any]] = None,
    edge_filter: list = None,
    show_messages: bool = True,
    message_colors: Callable[["Message", MessageType], Any] = None,
    message_size: int = None,
    show_legends: bool = True,
    space_for_legend: float = 0.15,
    show_labels: bool = True,
    node_labels: dict["Node", str] | Callable[[], dict["Node", str]] = None,
):
    """
    Function to draw the current state of the simulation or network. This function is used to visualize the network
    and the messages in the network.
    Automatically determines the current algorithm and draws the network accordingly. This includes a mapping of
    node colors to the status of the nodes, as well as the messages in the network.

    :param sim: Simulation or Network object
    :param axes: matplotlib axes object
    :param clear: boolean to clear the axes before drawing
    :param tree_key: key in nodes memory (dictionary) where tree data is stored
    :param dpi: dots per inch
    :param node_radius: radius of nodes
    :param node_positions: dictionary of node positions or function to get node positions
    :param node_colors: dictionary of node colors or function to get node colors
    :param edge_filter: list of edges to draw
    :param show_messages: boolean to show messages in the network
    :param show_legends: boolean to show legends
    :param space_for_legend: space for legend, as a porcentage of the figure
    :param show_labels: boolean to show labels of nodes
    :param node_labels: dictionary of node labels or function to get node labels
    :return: matplotlib figure object
    """

    if isinstance(sim, Simulation):
        net = sim.network

        try:
            currentAlgorithm = sim.get_current_algorithm()
        except SimulationException:
            currentAlgorithm = None
    else:
        net = sim
        currentAlgorithm = None

    if node_positions:
        pos_aux = net.pos
        net.pos = node_positions() if callable(node_positions) else node_positions

    if axes is None:
        with plt.ioff():
            fig, axes = plt.subplots()

    if clear:
        axes.clear()

    axes.pcolormesh(net.environment.image, vmin=0, cmap="binary_r")

    if tree_key:
        __draw_tree(tree_key, net, axes)

    __draw_edges(net, edge_filter, axes)

    __create_nodes(axes, node_radius, node_colors, show_messages, show_legends, net, currentAlgorithm)

    if show_labels:
        if node_labels:
            aux_labels = net.labels
            net.labels = node_labels() if callable(node_labels) else node_labels

        __draw_labels(net, node_radius, dpi)

    if show_messages:
        if not callable(node_radius):
            message_size = message_size or 3 * node_radius / 4
        else:
            assert message_size is not None, "Message size must be provided when node_radius is a function."

        __draw_messages(net, axes, message_colors, message_radius=message_size)

    step_text = " (step %d)" % sim.algorithmState["step"] if isinstance(currentAlgorithm, NodeAlgorithm) else ""
    axes.set_title((currentAlgorithm.name if currentAlgorithm else "") + step_text)

    # remove as much whitespace as possible
    axes.axis("off")
    plt.tight_layout()
    if show_legends:
        plt.gcf().subplots_adjust(left=0, bottom=0, right=1 - space_for_legend, top=0.95)
    else:
        plt.gcf().subplots_adjust(left=0, bottom=0, right=1, top=0.95)

    if node_positions:
        net.pos = pos_aux

    if node_labels and show_labels:
        net.labels = aux_labels

    return axes.figure


def __create_nodes(axes, node_radius, node_colors, show_messages, show_legends, net, currentAlgorithm):
    if not node_colors:
        node_colors = __create_and_get_color_labels(
            net,
            algorithm=currentAlgorithm,
            figure=axes.figure if show_legends else None,
            show_messages=show_messages,
        )
    elif callable(node_colors):
        node_colors = node_colors()

    if isinstance(node_colors, dict):
        node_pos_color = ((n, net.pos[n], node_colors.get(n, "r")) for n in net.nodes())
    else:
        node_pos_color = ((n, net.pos[n], node_colors) for n in net.nodes())

    if callable(node_radius):
        node_radius_pos_color = tuple((node_radius(n), tuple(pos), color) for n, pos, color in node_pos_color)
    else:
        node_radius_pos_color = tuple((node_radius, tuple(pos), color) for n, pos, color in node_pos_color)

    patches = __draw_nodes(node_radius_pos_color, fig_id=id(plt.gcf()))
    patches.axes = axes
    patches.figure = axes.figure
    axes.add_collection(patches)

    return patches


def create_animation(
    sim: "Simulation",
    figsize=None,
    dpi: int = 100,
    milliseconds_per_frame: int = 300,
    frame_limit: int = 2000,
    **kwargs,
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
    :param figsize: figure size
    :param dpi: dots per inch
    :param milliseconds_per_frame: milliseconds per frame
    :param frame_limit: limit of frames, default is 2000
    :param kwargs: additional keyword arguments to pass to the :func:`draw_current_state` function
    :return: animation object
    """
    exception_occurred = False

    with plt.ioff():  # Turn off interactive mode
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        def draw_frame(frame_index):
            nonlocal exception_occurred

            if exception_occurred:
                return

            if frame_index == 0:
                sim.reset()

            draw_current_state(sim, ax, dpi=dpi, **kwargs)

            try:
                sim.run(1)
            except BaseException as e:
                exception_occurred = True
                logger.exception(e)

            return ax.artists

        def frame_count():
            frame_index = 0

            def should_continue():
                if exception_occurred:
                    return False

                if frame_limit and frame_index >= frame_limit:
                    logger.warning("Frame limit reached.")
                    return False

                if not sim.is_halted():
                    logger.debug(f"Frame {frame_index}, simulation still running.")
                    return True

                if frame_index == 0:
                    logger.debug(f"Frame {frame_index}, simulation not started.")
                    return True

                return False

            while True:
                if should_continue():
                    yield frame_index
                    frame_index += 1
                else:
                    yield frame_index
                    break

        return animation.FuncAnimation(
            fig,
            func=draw_frame,
            frames=frame_count,
            interval=milliseconds_per_frame,
            cache_frame_data=True,
            save_count=frame_limit,
        )
