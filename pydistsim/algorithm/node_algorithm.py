from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from types import NoneType
from typing import TYPE_CHECKING, Union

from pydistsim.algorithm.base_algorithm import AlgorithmException, BaseAlgorithm
from pydistsim.algorithm.node_wrapper import NodeAccess
from pydistsim.logging import logger
from pydistsim.message import Message
from pydistsim.message import MetaHeader as MessageMetaHeader
from pydistsim.observers import ObservableEvents
from pydistsim.restrictions.axioms import FiniteCommunicationDelays, LocalOrientation

if TYPE_CHECKING:
    from pydistsim.algorithm.node_wrapper import NeighborLabel
    from pydistsim.network import Node


@dataclass
class Alarm:
    """
    Dataclass that represents an alarm set for a node.
    """

    time_left: int
    message: Message
    node: "NodeAccess"
    triggered: bool = False


class Actions(StrEnum):
    """
    Enum that defines the possible actions that can be triggered by a message.
    """

    default = "default"
    receiving = "receiving"
    spontaneously = "spontaneously"
    alarm = "alarm"


MSG_META_HEADER_MAP = {
    MessageMetaHeader.NORMAL_MESSAGE: Actions.receiving,
    MessageMetaHeader.INITIALIZATION_MESSAGE: Actions.spontaneously,
    MessageMetaHeader.ALARM_MESSAGE: Actions.alarm,
}


ActionMethod = Callable[["NodeAlgorithm", "NodeAccess", Message], NoneType]


class StatusValues(StrEnum):
    """
    Enum that defines the possible statuses of the nodes.

    Instances of this class should be used as decorators for methods in subclasses of :class:`NodeAlgorithm`.
    """

    def __call__(self, func: ActionMethod):
        """
        Decorator that sets the method for the action and status.

        :param func: The method to be set.
        :type func: ActionMethod
        :return: The method that was set.
        :rtype: ActionMethod
        """

        assert (
            func.__name__ in Actions.__members__
        ), f"Invalid function name '{func.__name__}', please make sure it is one of {list(Actions.__members__)}."

        self.set_method(func)

        return func

    def implements(self, action: Actions):
        return hasattr(self, str(action))

    def get_method(self, action: Actions):
        return getattr(self, str(action))

    def set_method(self, method: ActionMethod):
        setattr(self, method.__name__, method)


class NodeAlgorithm(BaseAlgorithm):
    """
    Base class for distributed algorithms.

    In subclass, the following functions and attributes should be defined:

    - Class attribute Status - subclass of StatusValues that defines all the possible statuses of the nodes
      STATUS must be written at the bottom after all functions are defined
    - Initializer: (optionally) Pass INI message to nodes that should
      start the algorithm and set some attributes needed by the specific
      algorithm
    """

    INI = MessageMetaHeader.INITIALIZATION_MESSAGE

    class Status(StatusValues):
        "Example of StatusValues subclass that defines the possible statuses of the nodes."

        IDLE = "IDLE"

    algorithm_restrictions = (
        FiniteCommunicationDelays,
        LocalOrientation,
    )

    S_init = ()
    "Tuple of statuses that nodes should have at the beginning of the algorithm."

    S_term = ()
    "Tuple of statuses that nodes should have at the end of the algorithm."

    NODE_ACCESS_TYPE: type[NodeAccess] = NodeAccess
    "Type of the node access proxy. Default is :class:`NodeAccess`."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.alarms: list[Alarm] = []

    ### BaseAlgorithm interface methods ###

    def step(self, check_restrictions: bool):
        if not self.is_initialized():
            self.notify_observers(ObservableEvents.algorithm_started, self)
            self.initializer()
            if check_restrictions:
                self.check_restrictions()

            if not any(len(node.outbox) + len(node.inbox) > 0 for node in self.network.nodes()):
                logger.warning("Initializer didn't send any message.")
        else:
            self.network.communicate()
            self._process_alarms()
            for node in self.network.nodes_sorted():
                self._node_step(node)

        self.notify_observers(ObservableEvents.step_done, self)

    def is_halted(self):
        """
        Check if the distributed algorithm has come to an end or deadlock,
        i.e. there are no messages to pass and no alarms set.

        A not-started algorithm is considered halted.

        :return: True if the algorithm is halted, False otherwise.
        :rtype: bool
        """
        return (
            all((len(node.inbox) == 0 and len(node.outbox) == 0) for node in self.network.nodes())
            and len(self.alarms) == 0
            and all(len(self.network.get_transit_messages(u, v)) == 0 for u, v in self.network.edges())
        )

    ### Algorithm methods ###

    def initializer(self):
        """
        Method used to initialize the algorithm. Is always called first.
        :class:`NodeAlgorithm` subclasses may want to reimplement it.

        Base implementation sends an INI message to the node with the lowest id and applies all restrictions.
        """
        logger.trace("Initializing algorithm {}.", self.name)
        self.apply_restrictions()

        node: "Node" = self.network.nodes_sorted()[0]
        node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI))
        for node in self.network.nodes_sorted():
            node.status = self.Status.IDLE

    def send_msg(self, node_source: "NodeAccess", message: Message):
        """
        Send a message to nodes listed in message's destination field.

        Note: Destination should be a list of nodes or one node.

        Update message's source field and inserts in node's outbox one copy
        of it for each destination.

        :param node_source: The node that sends the message.
        :type node_source: NodeAccess
        :param message: The message to be sent.
        :type message: Message
        """
        source_node: "Node" = node_source.unbox()  # unwrap the proxy

        message.source = source_node
        if not isinstance(message.destination, Iterable):
            message.destination = [message.destination]
        for destination_w in message.destination:
            destination: "Node" = destination_w.unbox()  # unwrap the proxy
            source_node.push_to_outbox(message.copy(), destination)

    def send(
        self,
        node_source: "NodeAccess",
        data: object,
        destination: Union["NeighborLabel", list["NeighborLabel"]],
        header: str = None,
    ):
        """
        Send content to destination, with header.

        :param node_w: Sender node
        :param data: Content to be received by destination nodes.
        :param destination: Destination node or list of destinations.
        :param header: Optional, header for the message.
        """
        self.send_msg(node_source, Message(data=data, header=header, destination=destination))

    ### Alarm methods ###

    def set_alarm(self, node_p: "NodeAccess", time: int, message: Message | None = None):
        """
        Set an alarm for the node.
        One unit of time is one step of the algorithm.
        After the time has passed, the alarm will trigger and the message will be sent to the node.
        When will that message be processed is not guaranteed to be immediate.

        Returns the alarm that was set, useful for disabling it later.

        :param node_p: The node for which the alarm is set.
        :type node: NodeProxy
        :param time: The time after which the alarm will trigger.
        :type time: int
        :param message: The message to be sent when the alarm triggers.
        :type message: Message
        :return: The alarm that was set.
        :rtype: Alarm
        """
        assert time > 0, "Time must be greater than 0."

        if message is None:
            message = Message()
        message.meta_header = MessageMetaHeader.ALARM_MESSAGE
        message.destination = node_p.unbox()

        alarm = Alarm(time, message, node_p)
        self.alarms.append(alarm)
        return alarm

    def disable_all_node_alarms(self, node_p: "NodeAccess"):
        """
        Disable all alarms set for the node.

        :param node: The node for which the alarms are disabled.
        :type node: NodeProxy
        """
        to_delete_messages = [alarm.message for alarm in self.alarms if alarm.node == node_p]
        self.alarms = [alarm for alarm in self.alarms if alarm.node != node_p]

        for message in node_p.unbox().inbox.copy():
            if message in to_delete_messages and message in node_p.inbox:
                node_p.inbox.remove(message)

    def disable_alarm(self, alarm: Alarm):
        """
        Disable an alarm.

        :param alarm: The alarm to be disabled.
        :type alarm: Alarm
        """
        if alarm in self.alarms:
            self.alarms.remove(alarm)
        elif alarm.message in alarm.node.unbox().inbox:
            alarm.node.unbox().inbox.remove(alarm.message)

    def update_alarm_time(self, alarm: Alarm, time_diff: int):
        """
        Update the time of an alarm by adding a time difference.
        The time difference can be negative.

        :param alarm: The alarm for which the time is updated.
        :type alarm: Alarm
        :param time_diff: The time difference to be added to the alarm's time.
        :type time_diff: int
        """
        if alarm in self.alarms:
            alarm.time_left += time_diff
        elif alarm.message in alarm.node.unbox().inbox:
            alarm.node.unbox().inbox.remove(alarm.message)
            alarm.time_left += time_diff
            alarm.triggered = False
            self.alarms.append(alarm)
        else:
            raise ValueError("Alarm not found. Cannot update time. Please check if it has been triggered.")

    ### Methods for algorithm evaluation ###

    def check_algorithm_initialization(self):
        """
        Check if the algorithm's current state matches the expected initial state.

        This method depends on the correct configuration of the :attr:`S_init` class attribute of the algorithm.
        """
        for node in self.network.nodes():
            if node.status not in self.S_init:
                raise AlgorithmException(
                    f"Node status not initialized as expected. Found {node.status} instead of any of {self.S_init}."
                )

    def check_algorithm_termination(self):
        """
        Check if the algorithm's current state matches the expected termination state.

        This method depends on the correct configuration of the :attr:`S_term` class attribute of the algorithm.
        """
        for node in self.network.nodes():
            if node.status not in self.S_term:
                raise AlgorithmException(
                    f"Node status not terminated as expected. Found {node.status} instead of any of {self.S_term}."
                )

    ### Private methods for algorithm execution ###

    def _node_step(self, node: "Node"):
        """Executes one step of the algorithm for given node."""
        message: Message = node.receive()

        if message:
            logger.debug("Processing step at node {}.", node.id)
            if message.destination is None or message.destination == node:
                # when destination is None it is broadcast message
                self._process_message(node, message)

    def _process_alarms(self):
        for alarm in self.alarms.copy():
            # copy to avoid errors produced by modifying the list while iterating
            alarm.time_left -= 1
            if alarm.time_left <= 0:
                self.alarms.remove(alarm)
                alarm.triggered = True
                alarm.node.unbox().push_to_inbox(alarm.message)

    def _process_message(self, node: "Node", message: Message):
        logger.debug("Processing message: 0x%x" % id(message))
        method_name = MSG_META_HEADER_MAP[message.meta_header]
        return self._process_action(method_name, node, message)

    def _process_action(self, action: Actions, node: "Node", message: Message):
        status: StatusValues = getattr(self.Status, node.status)

        node_proxy = self.NODE_ACCESS_TYPE(node)  # TODO: set offuscation here
        if message.source is not None:
            message.source = node_proxy._get_in_neighbor_proxy(message.source)
        if message.destination is not None:
            message.destination = node_proxy

        method_name = f"{action}_{status}"
        default_name = f"{Actions.default}_{status}"

        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(node_proxy, message)
        elif hasattr(self, default_name):
            method = getattr(self, default_name)
            return method(node_proxy, message)

        logger.error(f"Method {self.name}.{action} not implemented for status {node.status}.")

    def reset(self):
        super().reset()
        for node in self.network.nodes():
            self.NODE_ACCESS_TYPE._clear_from_memoization(node)

    ### Metaclass methods ###

    def __configure_class__(clsname: str, bases: tuple[type], dct: dict):
        """
        Metaclass method that configures the class by adding methods for all possible actions and statuses.

        :param clsname: The name of the class.
        :type clsname: str
        :param bases: The base classes of the class.
        :type bases: tuple[type]
        :param dct: The dictionary of the class.
        :type dct: dict
        """

        # Search for the Status class in the bases or in the dct
        status_class = None
        if "Status" in dct:
            status_class: StatusValues = dct["Status"]
        else:
            for base in bases:
                if hasattr(base, "Status") and issubclass(base.Status, StatusValues):
                    status_class: StatusValues = base.Status
                    break
        assert status_class is not None, "Status class not found in bases or in dct."

        # Create methods for all possible actions and statuses
        for action in Actions:
            # Create a method for invocations like `self.default(node, message)`
            # CAUTION: the resolution of the method is deferred to the instance, super() will not work
            def __unresolved_action_method__(alg_instance: "NodeAlgorithm", node: "NodeAccess", message: Message):
                alg_instance._process_action(action, node, message)

            dct[action] = __unresolved_action_method__

            for status in status_class:
                if status.implements(action):
                    # Create a method for invocations like `self.default_IDLE(node, message)`
                    # As the method is created in the class, super() will work.
                    dct[f"{action}_{status}"] = status.get_method(action)
