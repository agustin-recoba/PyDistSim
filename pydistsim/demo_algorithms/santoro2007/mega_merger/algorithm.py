import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypedDict, TypeVar

from pydistsim.algorithm import NodeAlgorithm, StatusValues
from pydistsim.algorithm.node_wrapper import DMANodeAccess, NeighborLabel
from pydistsim.demo_algorithms.santoro2007.mega_merger.labels import (
    COUNTRIES,
    IATA_AIRPORTS,
)
from pydistsim.logging import logger
from pydistsim.message import Message
from pydistsim.restrictions.communication import BidirectionalLinks
from pydistsim.restrictions.reliability import TotalReliability
from pydistsim.restrictions.topological import Connectivity

PARENT = "parent"


class MMStatus(StatusValues):
    INITIATOR = "INITIATOR"
    SLEEPING = "SLEEPING"
    ASKING_OUTSIDE = "ASKING_OUTSIDE"
    COMPUTING_MIN_WEIGHTS = "COMPUTING_MIN_WEIGHTS"
    WAITING_PARENT = "WAITING_PARENT"
    ELECTED = "ELECTED"
    NOT_ELECTED = "NOT_ELECTED"


class MMHeaders(StrEnum):
    ARE_YOU_OUTSIDE = "ARE_YOU_OUTSIDE"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    LET_US_MERGE = "LET_US_MERGE"
    MERGE_ME = "MERGE_ME"
    NOTIFICATION = "NOTIFICATION"
    MIN_LINK_WEIGHT = "MIN_LINK_WEIGHT"
    TERMINATION = "TERMINATION"


@dataclass(slots=True, frozen=True)
class City:
    name: int
    level: int
    is_downtown: bool

    def make_child(self):
        return City(name=self.name, level=self.level, is_downtown=False)

    def __eq__(self, other):
        if self is other:
            return True
        if other is None:
            return False
        if not isinstance(other, City):
            return False

        return self.name == other.name


class MMNode(DMANodeAccess):
    """
    MMNode class represents a node in the Mega Merger algorithm.

    Attributes:
        id (int): Unique identifier for the node.
        city (City): The city associated with the node.
        weight (dict[NeighborLabel, int]): Weights of the links to neighboring nodes.

        internal_links (set[NeighborLabel]): Set of internal links to neighboring nodes.
        children (set[NeighborLabel]): Set of child nodes.
        tree_key (dict[str, NeighborLabel]): Dictionary mapping tree keys to neighbor labels.
        blocked_messages (dict[tuple[NeighborLabel, MMHeaders], Message]): Messages that are blocked and waiting to be
            processed.
        external_received (bool): Flag indicating if an external message has been received since the last reset.
        weight_received (set[NeighborLabel]): Set of neighbors from which weight has been received since the last round
            of asking for the minimum weight.
        min_weight (int): Minimum weight among the links received in the last round.
        asking_min_weight (bool): Flag indicating if the node is asking for the minimum weight.
        last_min_weight_sent (int): Last minimum weight sent by the node.
        link_trying_merge (NeighborLabel): Link that is trying to merge.
        link_asking_outside (NeighborLabel): Link that is asking for an outside connection.
        link_with_min_weight (NeighborLabel): Link directing to the minimum weight (might be this link or another down
            the tree).
    """

    id: int
    city: City
    weight: dict[NeighborLabel, int]

    internal_links: set[NeighborLabel]
    children: set[NeighborLabel]
    tree_key: dict[str, NeighborLabel]
    blocked_messages: dict[tuple[NeighborLabel, MMHeaders], Message]

    external_received: bool
    weight_received: set[NeighborLabel]
    min_weight: int
    asking_min_weight: bool
    last_min_weight_sent: int
    link_trying_merge: NeighborLabel
    link_asking_outside: NeighborLabel
    link_with_min_weight: NeighborLabel


T = TypeVar("T")


class MegaMergerParameters(TypedDict, Generic[T]):
    """
    Class to specify the parameters for the Mega Merger algorithm.

    The list of weights and cities must have at least the same size of edges and nodes in the network, respectively.
    Additionally, both list must be disjoint, i.e., no city can be a weight and vice-versa.
    Obviously, the `INF_WEIGHT` must be bigger than any weight or city and must be comparable in type to both
    (`>` and `<` must work).

    Attributes:
        percentage_of_initiators (float): Percentage of initiators in the network.
        INF_WEIGHT (T): Value representing infinity.
        WEIGHT_LIST (list[T]): List of weights for the links.
        CITY_LIST (list[T]): List of cities in the network.
    """

    percentage_of_initiators: float
    INF_WEIGHT: T
    WEIGHT_LIST: list[T] | Callable[[int], T]
    CITY_LIST: list[T] | Callable[[int], T]


class ExampleParameters:
    countries_parameters: MegaMergerParameters = {
        "percentage_of_initiators": 0.4,
        "WEIGHT_LIST": IATA_AIRPORTS,  # 3-letter airport code
        "CITY_LIST": COUNTRIES,  # 2-letter country code
        "INF_WEIGHT": "ZZZZ",  # comparable to both WEIGHT_LIST and CITY_LIST
    }

    numerical_parameters: MegaMergerParameters = {
        "percentage_of_initiators": 0.5,
        "CITY_LIST": lambda i: i + 1,  # positives
        "WEIGHT_LIST": lambda i: -i - 1,  # negatives
        "INF_WEIGHT": 9999999,  # bigger than any weight or city
    }


class MegaMergerAlgorithm(NodeAlgorithm):
    """
    Mega-Merger
    ===========

    This algorithm is a distributed algorithm that elects a single node in a network.
    The way it works is by creating cities (a grouping of nodes) and merging them together, while
    maintaining a tree structure with a root (the downtown node) that makes the decisions.

    Ultimately, when the cities are merged, the downtown node is elected as the root of the tree.

    The algorithm is based on the descriptions in the book `Design and Analysis of Distributed
    Algorithms <http://eu.wiley.com/WileyCDA/WileyTitle/productCd-0471719978,descCd-description.html>`_
    by Nicola Santoro.

    Parameters
    ----------

    percentage_of_initiators : float
        The percentage of initiators in the network.

    INF_WEIGHT : T
        Value representing infinity.

    WEIGHT_LIST : list[T] | Callable[[int], T]
        Mapping of weights for the links.

    CITY_LIST : list[T] | Callable[[int], T]
        Mapping of cities in the network.
    """

    default_params: MegaMergerParameters = ExampleParameters.countries_parameters

    Status = MMStatus

    S_init = (MMStatus.INITIATOR, MMStatus.SLEEPING)
    S_term = (MMStatus.ELECTED, MMStatus.NOT_ELECTED)

    algorithm_restrictions = (
        BidirectionalLinks,
        TotalReliability,
        Connectivity,
    )

    def _create_wrapper_manager(self):
        return self.NODE_WRAPPER_MANAGER_TYPE(self.network, MMNode)

    def initializer(self):
        # Initialize the nodes and the weights dictionary
        nodes: list[MMNode] = list(self.nwm.nodes())
        random.shuffle(nodes)
        for i, node in enumerate(nodes):
            node.weight = {}
            node.id = self.CITY_LIST(i) if callable(self.CITY_LIST) else self.CITY_LIST[i]
            node.status = MMStatus.SLEEPING

        # Initialize the weights
        edges = list(self.nwm.edges())
        random.shuffle(edges)
        for i, ((u_own_view, us_view_of_v), (v_own_view, vs_view_of_u)) in enumerate(edges):
            u_own_view.weight[us_view_of_v] = v_own_view.weight[vs_view_of_u] = (
                self.WEIGHT_LIST(i) if callable(self.WEIGHT_LIST) else self.WEIGHT_LIST[i]
            )

        # Choose the initiators
        quantity_of_initiators = math.floor(self.percentage_of_initiators * len(self.network) + 1)
        for node in set(
            random.choices(
                tuple(self.network.nodes()),
                k=quantity_of_initiators,
            )
        ):
            node.status = MMStatus.INITIATOR
            node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI, destination=node))

    @MMStatus.INITIATOR
    def default(self, node: MMNode, message: Message):
        self.on_awakening(node, message if message.meta_header != NodeAlgorithm.INI else None)

    @MMStatus.SLEEPING
    def receiving(self, node: MMNode, message: Message):  # noqa: F811
        self.on_awakening(node, message)

    def on_awakening(self, node: MMNode, message: Message = None):
        node.status = MMStatus.COMPUTING_MIN_WEIGHTS

        node.city = City(name=node.id, level=1, is_downtown=True)
        node.internal_links = set()
        node.blocked_messages = {}
        node.tree_key = {PARENT: None}
        node.children = set()
        node.external_received = False
        node.weight_received = set()
        node.link_trying_merge = None
        node.link_asking_outside = None
        node.link_with_min_weight = None
        node.min_weight = self.INF_WEIGHT

        if self.get_external_links(node):
            node.status = MMStatus.COMPUTING_MIN_WEIGHTS
            node.asking_min_weight = True
            self.fire_next_are_you_outside(node)

            if message:
                self.receiving_COMPUTING_MIN_WEIGHTS(
                    node, message
                )  # undirected call to `receiving` when status is COMPUTING_MIN_WEIGHTS

        else:
            self.when_termination(node)

    @MMStatus.ASKING_OUTSIDE
    def receiving(self, node: MMNode, message: Message):  # noqa: F811
        self.log_received(node, message)

        match message.header:
            case MMHeaders.ARE_YOU_OUTSIDE:
                self.on_are_you_outside(node, message)
            case MMHeaders.EXTERNAL:
                self.on_external(node, message)
            case MMHeaders.INTERNAL:
                self.on_internal(node, message)
            case MMHeaders.LET_US_MERGE:
                self.on_let_us_merge(node, message)
            case MMHeaders.MIN_LINK_WEIGHT:
                self.on_min_link_weight(node, message)
            case MMHeaders.NOTIFICATION:
                self.on_notification(node, message)
            case _:
                logger.debug(f"ASKING_OUTSIDE: {message.header}")

    @MMStatus.COMPUTING_MIN_WEIGHTS
    def receiving(self, node: MMNode, message: Message):  # noqa: F811
        self.log_received(node, message)

        match message.header:
            case MMHeaders.ARE_YOU_OUTSIDE:
                self.on_are_you_outside(node, message)
            case MMHeaders.LET_US_MERGE:
                self.on_let_us_merge(node, message)
            case MMHeaders.MERGE_ME:
                self.on_merge_me(node, message)
            case MMHeaders.NOTIFICATION:
                self.on_notification(node, message)
            case MMHeaders.MIN_LINK_WEIGHT:
                if node.asking_min_weight:
                    self.on_min_link_weight(node, message)
                else:
                    self.log_ignore(node, message)
            case MMHeaders.TERMINATION:
                self.on_termination(node, message)
            case _:
                logger.debug(f"COMPUTING_MIN_WEIGHTS: {message.header}")

    @MMStatus.NOT_ELECTED
    def receiving(self, node: MMNode, message: Message):  # noqa: F811
        self.log_received(node, message)

        match message.header:
            case MMHeaders.NOTIFICATION:
                self.on_notification(node, message)  # a terminated node may still change its city
            case _:
                logger.debug(f"NOT_ELECTED: {message.header}")

    @MMStatus.WAITING_PARENT
    def receiving(self, node: MMNode, message: Message):  # noqa: F811
        self.log_received(node, message)

        match message.header:
            case MMHeaders.ARE_YOU_OUTSIDE:
                self.on_are_you_outside(node, message)
            case MMHeaders.LET_US_MERGE:
                self.on_let_us_merge(node, message)
            case MMHeaders.MERGE_ME:
                self.on_merge_me(node, message)
            case MMHeaders.NOTIFICATION:
                self.on_notification(node, message)
            case MMHeaders.TERMINATION:
                self.on_termination(node, message)
            case _:
                logger.debug(f"WAITING_PARENT: {message.header}")

    def log_received(self, node: MMNode, message: Message):
        logger.info(f"Receiving\t{message.header} ({message.source.unbox()} --> {node.unbox()}, data={message.data})")

    def log_ignore(self, node: MMNode, message: Message):
        logger.info(f"Ignoring\t{message.header} ({message.source.unbox()} --> {node.unbox()}, data={message.data})")

    def on_are_you_outside(self, node: MMNode, message: Message):
        """
        Handles the 'are you outside' message received by a node.

        This method processes the message to determine if the node is part of the same city as the sender
        or if it is outside. Depending on the city levels and the source of the message, it will either
        handle the message internally, send an internal or external response, or block the message.
        """
        other_city: City = message.data
        my_city: City = node.city

        if my_city == other_city:
            if node.link_asking_outside == message.source:
                self.on_internal(node, message)
            else:
                self.send(node_source=node, data=None, destination=message.source, header=MMHeaders.INTERNAL)
                self.add_internal_link(node, message.source)
        elif my_city.level >= other_city.level:
            self.send(node_source=node, data=None, destination=message.source, header=MMHeaders.EXTERNAL)
        else:
            self.block_msg(node, message)

    def on_external(self, node: MMNode, message: Message):
        """
        Handles the reception of an external message by a node.

        This method is called when a node receives a message confirming the link leads to an external node.
        It updates the node's state and processes the message according to the
        Mega Merger algorithm.

        Behavior:
            - Sets the node's `external_received` flag to True.
            - If the message source is not the expected link, logs a debug message and ignores the message.
            - Updates the node's status to `COMPUTING_MIN_WEIGHTS` (prev. was `ASKING_OUTSIDE`).
            - Updates the link with the minimum weight.
            - If the node is done asking outside:
                - If the node is the downtown, sends a "let us merge" message.
                - If the node is not the root, sends the minimum link weight to the parent node and updates the
                node's status.
            - If the minimum weight is infinite, triggers partial termination.
        """
        node.external_received = True

        if node.link_asking_outside != message.source:
            logger.debug(f"External message from {message.source} not expected")
            self.log_ignore(node, message)
            return

        node.link_asking_outside = None
        node.status = MMStatus.COMPUTING_MIN_WEIGHTS

        self.update_link_with_min_weight(node, message.source, node.weight[message.source])

        if self.is_done_asking_outside(node):  # DONE ASKING OUTSIDE
            if not node.tree_key[PARENT]:  # ROOT
                self.send_let_us_merge(node, node.city.make_child(), node.min_weight)

            else:  # NOT ROOT
                self.send(
                    node_source=node,
                    data=node.min_weight,
                    destination=node.tree_key[PARENT],
                    header=MMHeaders.MIN_LINK_WEIGHT,
                )
                node.asking_min_weight = False
                node.status = MMStatus.WAITING_PARENT
                node.last_min_weight_sent = node.min_weight
                if node.min_weight == self.INF_WEIGHT:
                    self.partial_termination(node)

    def partial_termination(self, node):
        """
        Handles the partial termination of a node in the Mega Merger algorithm.

        This method sets the status of the given node to NOT_ELECTED and sends a
        termination message to all its children nodes.

        Partial termination means that the node is not elected as the downtown node and neither
        it nor its children will make any further progress in the algorithm.
        """
        node.status = MMStatus.NOT_ELECTED
        self.send(node_source=node, data=None, destination=node.children, header=MMHeaders.TERMINATION)

    def on_internal(self, node: MMNode, message: Message):
        """
        Handles the internal message received by a node.

        This method processes an internal message received by a node and updates the node's state accordingly.
        It performs the following actions:
        - Sets as internal the link between the node and the message source.
        - Checks if the message source is the expected link asking outside.
            - If not, logs a debug message and ignores the message.
        - Updates the node's status to COMPUTING_MIN_WEIGHTS if the message source is the expected.
        - If the node is done asking outside:
            - If the node is the root, triggers a new merge or the global termination.
            - If the node is not the root, sends the minimum link weight to the parent node.
        """

        self.add_internal_link(node, message.source)

        if node.link_asking_outside != message.source:
            logger.debug(f"Internal message from {message.source} not expected")
            self.log_ignore(node, message)
            return
        node.link_asking_outside = None
        node.status = MMStatus.COMPUTING_MIN_WEIGHTS

        if self.is_done_asking_outside(node):
            if not node.tree_key[PARENT]:  # ROOT
                if self.is_termination(node):
                    self.when_termination(node)
                else:
                    self.send_let_us_merge(node, node.city.make_child(), node.min_weight)

            else:  # NOT ROOT
                w = node.min_weight if node.min_weight else self.INF_WEIGHT
                self.send(
                    node_source=node,
                    data=w,
                    destination=node.tree_key[PARENT],
                    header=MMHeaders.MIN_LINK_WEIGHT,
                )
                node.status = MMStatus.WAITING_PARENT
                node.asking_min_weight = False
                node.last_min_weight_sent = w
                if w == self.INF_WEIGHT:
                    node.status = MMStatus.NOT_ELECTED

        elif len(self.get_external_links(node)) > 0:
            node.asking_min_weight = True
            self.fire_next_are_you_outside(node)

    def on_let_us_merge(self, node: MMNode, message: Message):
        """
        Handles the LET_US_MERGE message received by a node.

        This method processes the LET_US_MERGE message and determines the appropriate action based on the
        relationship between the sender and the receiver nodes, as well as their respective cities and levels.

        Actions:
        - If the sender's city is the same as the receiver's city, sends the LET_US_MERGE message down the tree.
        - If the merge is considered friendly, it triggers a friendly merge.
        - If the receiver's city level is higher than the sender's, it triggers a forced merge.
        - If the receiver's city level is the same as the sender's, it blocks the message.
        - Otherwise, it ignores the message.
        """
        logger.info(f"LET_US_MERGE: {message.source.unbox()} -> {node.unbox()}")

        sender_city, other_id, road_weight = message.data
        my_city = node.city

        if my_city == sender_city:
            if node.link_with_min_weight and node.min_weight != self.INF_WEIGHT:
                self.send_let_us_merge(node, sender_city, road_weight)

        elif self.is_friendly_merge(node, message) and message.source in self.get_external_links(node):
            self.when_friendly_merge(node, message)
        elif my_city.level > sender_city.level and message.source in self.get_external_links(node):
            self.send(
                node_source=node,
                data=(my_city.make_child(), not self.is_done_asking_outside(node)),
                destination=message.source,
                header=MMHeaders.MERGE_ME,
            )
            self.add_child(node, message.source)

            self.add_internal_link(node, message.source)
        elif my_city.level == sender_city.level and message.source in self.get_external_links(node):
            self.block_msg(node, message)
        else:
            self.log_ignore(node, message)

    def add_child(self, node, child):
        node.children.add(child)

    def send_let_us_merge(self, node, new_city, road_weight):
        """
        Sends a 'LET_US_MERGE' message from the given node to its link with the minimum weight.

        This method handles both border and internal nodes. For border nodes, it checks if the
        minimum weight of the node matches the provided road weight before sending the message.
        If the weights do not match, an error is logged and the method returns without sending
        the message. For internal nodes, it sends the message directly.
        """
        # BORDER NODE
        if node.link_with_min_weight in self.get_external_links(node):
            if node.min_weight != road_weight:
                logger.error(f"MIN_WEIGHT != road_weight: {node.min_weight} != {road_weight}")
                return

            # INTERNAL NODE
            self.send(
                node_source=node,
                data=(new_city, node.id, node.min_weight),
                destination=node.link_with_min_weight,
                header=MMHeaders.LET_US_MERGE,
            )

            node.link_trying_merge = node.link_with_min_weight

            def let_us_merge_processor(blocked_message: Message, deleter: Callable[[], None]):
                if blocked_message.source in self.get_internal_links(node):  # Already merged
                    deleter()

                elif self.is_friendly_merge(node, blocked_message):
                    deleter()
                    self.when_friendly_merge(node, blocked_message)
                    return False

                return True

            self.unblock_by_header(node, MMHeaders.LET_US_MERGE, let_us_merge_processor)
        else:
            # INTERNAL NODE
            self.send(
                node_source=node,
                data=(new_city, node.id, node.min_weight),
                destination=node.link_with_min_weight,
                header=MMHeaders.LET_US_MERGE,
            )

    def on_merge_me(self, node: MMNode, message: Message):
        """
        Handles the MERGE_ME message received by a node.

        This method processes the MERGE_ME message, which indicates a forced merge between the sender and the receiver.
        It triggers the merge and updates the node's state accordingly.
        """

        new_city, to_ask_min_weight = message.data
        new_city: City

        if new_city == node.city:
            self.log_ignore(node, message)
            return

        self.set_city(node, new_city)
        self.add_internal_link(node, message.source)

        if node.tree_key[PARENT]:
            node.children.add(node.tree_key[PARENT])
        self.set_parent(node, message.source)

        self.send(
            node_source=node,
            data=(new_city.make_child(), to_ask_min_weight),
            destination=node.children,
            header=MMHeaders.NOTIFICATION,
        )

        self.when_city_change(node, new_city, to_ask_min_weight)

    def on_notification(self, node: MMNode, message: Message):
        """
        Handles the notification message received by a node.

        This method processes a notification message, updates the node's city,
        and manages the parent-child relationships within the node's tree structure.
        It also sends the notification to the node's children and triggers any
        necessary actions when the city changes.
        """
        new_city, to_ask_min_weight = message.data
        new_city: City

        if new_city == node.city:
            self.log_ignore(node, message)
            return

        self.set_city(node, new_city)

        if message.source in node.children:

            if node.tree_key[PARENT]:
                node.children.add(node.tree_key[PARENT])

            self.set_parent(node, message.source)
            node.children.remove(message.source)

        self.send(
            node_source=node,
            data=(new_city, to_ask_min_weight),
            destination=node.children,
            header=MMHeaders.NOTIFICATION,
        )

        self.when_city_change(node, new_city, to_ask_min_weight)

    def when_city_change(self, node, new_city, to_ask_min_weight):
        """
        Handles the event when a node's city changes.

        This method resets the node's metadata and processes blocked messages
        related to merging and external status checks. Depending on the new city's
        level and the message's city level, it either merges the node with the
        source of the message or marks the source as internal or external.

        Internal Processors:
        - let_us_merge_processor: Processes messages with the header LET_US_MERGE.
        - are_you_outside_processor: Processes messages with the header ARE_YOU_OUTSIDE.

        If `to_ask_min_weight` is True, the node's status is set to COMPUTING_MIN_WEIGHTS,
        and it initiates the process to ask for the minimum weight from external links.
        """
        self.reset_meta(node)

        def let_us_merge_processor(blocked_message: Message, deleter: Callable[[], None]):
            msg_city, other_id, road_weight = blocked_message.data

            if blocked_message.source in self.get_internal_links(node):  # Already merged
                deleter()

            elif new_city.level > msg_city.level and new_city != msg_city:
                deleter()

                self.send(
                    node_source=node,
                    data=(new_city, to_ask_min_weight),
                    destination=blocked_message.source,
                    header=MMHeaders.MERGE_ME,
                )
                self.add_child(node, blocked_message.source)
                self.add_internal_link(node, blocked_message.source)

            return True

        self.unblock_by_header(node, MMHeaders.LET_US_MERGE, let_us_merge_processor)

        def are_you_outside_processor(blocked_message: Message, deleter: Callable[[], None]):
            msg_city = blocked_message.data

            if new_city == msg_city:
                deleter()

                self.send(node_source=node, data=None, destination=blocked_message.source, header=MMHeaders.INTERNAL)
                self.add_internal_link(node, blocked_message.source)
            elif new_city.level >= msg_city.level:
                deleter()

                self.send(node_source=node, data=None, destination=blocked_message.source, header=MMHeaders.EXTERNAL)

            return True

        self.unblock_by_header(node, MMHeaders.ARE_YOU_OUTSIDE, are_you_outside_processor)

        if to_ask_min_weight:
            node.status = MMStatus.COMPUTING_MIN_WEIGHTS
            node.asking_min_weight = True
            if len(self.get_external_links(node)) > 0:
                self.fire_next_are_you_outside(node)
            else:
                if node.tree_key[PARENT] and self.is_done_asking_outside(node):
                    self.send_INF_WEIGHT(node)
                    node.status = MMStatus.COMPUTING_MIN_WEIGHTS
                    node.asking_min_weight = False
                    node.last_min_weight_link = self.INF_WEIGHT
                    node.status = MMStatus.NOT_ELECTED

    def on_min_link_weight(self, node: MMNode, message: Message):
        """
        Handles the event when a minimum link weight message is received by a node.

        This method processes the received message, updates the node's state, and
        determines the next steps based on the node's role in the tree (root or non-root).
        """

        if message.source not in node.children:
            self.log_ignore(node, message)
            return

        node.weight_received.add(message.source)

        self.update_link_with_min_weight(node, message.source, message.data)

        if not self.is_done_asking_outside(node):
            return

        # DONE ASKING OUTSIDE
        if not node.tree_key[PARENT]:  # IM ROOT
            if self.is_termination(node):
                self.when_termination(node)
            else:
                logger.info(f"DOWNTOWN LET_US_MERGE {node.unbox()}")
                self.send_let_us_merge(node, node.city.make_child(), node.min_weight)
        else:
            self.send(
                node_source=node,
                data=node.min_weight,
                destination=node.tree_key[PARENT],
                header=MMHeaders.MIN_LINK_WEIGHT,
            )
            node.status = MMStatus.WAITING_PARENT
            node.asking_min_weight = False
            node.last_min_weight_sent = node.min_weight
            if not node.min_weight or node.min_weight == self.INF_WEIGHT:
                node.status = MMStatus.NOT_ELECTED

    def on_termination(self, node: MMNode, message: Message):
        self.when_termination(node)

    def when_termination(self, node: MMNode):
        if node.tree_key[PARENT] is None:
            node.status = MMStatus.ELECTED
            self.set_city(node, City(name=node.city.name, level=-1, is_downtown=True))
        else:
            node.status = MMStatus.NOT_ELECTED
            self.set_city(node, City(name=node.city.name, level=-1, is_downtown=False))

        # Unnecessary, as the children will already be partially terminated
        # self.send(node_source=node, data=None, destination=node.children, header=MMHeaders.TERMINATION)

    def is_termination(self, node: MMNode):
        if node.tree_key[PARENT]:
            raise ValueError("This node is not the root of the tree")

        return self.is_done_asking_outside(node) and (node.min_weight is None or node.min_weight == self.INF_WEIGHT)

    def is_done_asking_outside(self, node: MMNode):
        return (node.external_received or len(self.get_external_links(node)) == 0) and (
            node.children.issubset(node.weight_received)
        )

    def update_link_with_min_weight(self, node: MMNode, neighbor: NeighborLabel, weight: int):
        if (node.link_with_min_weight is None) or weight < node.min_weight:
            node.link_with_min_weight = neighbor
            node.min_weight = weight
            return True

        return False

    def block_msg(self, node: MMNode, message: Message):
        node.blocked_messages[(message.source, message.header)] = message

    def unblock_by_header(
        self, node: MMNode, header: MMHeaders, unblocked_processor: Callable[[Message, Callable[[], None]], bool]
    ):
        for key in tuple(filter(lambda s_h: s_h[1] == header, node.blocked_messages)):
            message = node.blocked_messages[key]

            if not unblocked_processor(
                blocked_message=message,
                deleter=lambda: node.blocked_messages.pop(key),
            ):
                break

    def is_friendly_merge(self, node: MMNode, message: Message):
        sender_city, other_id, road_weight = message.data
        sender_level = sender_city.level
        my_level = node.city.level

        return my_level == sender_level and message.source == node.link_trying_merge

    def when_friendly_merge(self, node: MMNode, message: Message):
        new_level = node.city.level + 1  # LEVEL INCREASED
        new_city_id = node.weight[message.source]
        other_city, other_id, road_weight = message.data

        if node.id < other_id:
            new_city = City(new_city_id, new_level, True)
            if node.tree_key[PARENT]:
                node.children.add(node.tree_key[PARENT])
                self.set_parent(node, None)
            node.children.add(message.source)
        else:
            new_city = City(new_city_id, new_level, False)
            if node.tree_key[PARENT]:
                node.children.add(node.tree_key[PARENT])
            self.set_parent(node, message.source)

        self.set_city(node, new_city)

        self.send(
            node_source=node,
            data=(new_city.make_child(), True),
            destination=node.children,  # check self.get_internal_links(node),
            header=MMHeaders.NOTIFICATION,
        )

        self.add_internal_link(node, message.source)

        self.when_city_change(node, new_city, True)

    def fire_next_are_you_outside(self, node: MMNode):
        "Assumes there are external links"
        external_links = self.get_external_links(node)
        min_link, min_weight = min(((n, node.weight[n]) for n in external_links), key=lambda x: x[1])

        if node.link_asking_outside != min_link:
            self.send(
                node_source=node,
                data=node.city.make_child(),
                destination=min_link,
                header=MMHeaders.ARE_YOU_OUTSIDE,
            )
            node.link_asking_outside = min_link
            node.status = MMStatus.ASKING_OUTSIDE

    def send_INF_WEIGHT(self, node: MMNode):
        self.send(
            node_source=node,
            data=self.INF_WEIGHT,
            destination=node.tree_key[PARENT],
            header=MMHeaders.MIN_LINK_WEIGHT,
        )

    def reset_meta(self, node: MMNode):
        logger.info(f"Reset meta: {node.unbox()}")

        node.weight_received = set()
        node.link_with_min_weight = None
        node.link_trying_merge = None
        node.external_received = False
        node.min_weight = self.INF_WEIGHT

    def get_external_links(self, node: MMNode):
        return set(node.neighbors()) - node.internal_links

    def get_internal_links(self, node: MMNode):
        return node.internal_links

    def add_internal_link(self, node: MMNode, neighbor: NeighborLabel):
        node.internal_links.add(neighbor)

    def set_city(self, node: MMNode, city: City):
        logger.info(f"NEW CITY {node.unbox()}: {city}")

        node.city = city

    def set_parent(self, node: MMNode, parent: NeighborLabel):
        logger.info(
            f"NEW PARENT {node.unbox()}: new {parent.unbox() if parent else None}, previous: {node.tree_key[PARENT].unbox() if node.tree_key[PARENT] else None}"
        )
        node.tree_key[PARENT] = parent
