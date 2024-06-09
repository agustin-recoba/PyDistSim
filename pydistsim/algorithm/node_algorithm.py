from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from types import MethodType
from typing import TYPE_CHECKING

from pydistsim.algorithm.base_algorithm import BaseAlgorithm
from pydistsim.logger import logger
from pydistsim.message import Message
from pydistsim.message import MetaHeader as MessageMetaHeader
from pydistsim.observers import ObservableEvents

if TYPE_CHECKING:
    from pydistsim.network import Node


@dataclass
class Alarm:
    "Dataclass that represents an alarm set for a node."

    time_left: int
    message: Message
    node: "Node"
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


class StatusValues(StrEnum):
    """
    Enum that defines the possible statuses of the nodes.

    Instances of this class should be used as decorators for methods in subclasses of NodeAlgorithm.
    """

    def __call__(self, func: MethodType):
        assert (
            func.__name__ in Actions.__members__
        ), f"Invalid function name '{func.__name__}', please make sure it is one of {list(Actions.__members__)}."

        self.set_method(func)

        return func

    def implements(self, action: Actions):
        return hasattr(self, str(action))

    def get_method(self, action: Actions):
        return getattr(self, str(action))

    def set_method(self, method: MethodType):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.alarms: list[Alarm] = []

    ### BaseAlgorithm interface methods ###

    def step(self):
        logger.debug(
            "[{}] Step {} started",
            self.name,
            self.network.algorithmState["step"],
        )
        if not self.is_initialized():
            self.notify_observers(ObservableEvents.algorithm_started, self)
            self.initializer()

            if not any(len(node.outbox) + len(node.inbox) > 0 for node in self.network.nodes()):
                logger.warning("Initializer didn't send any message.")
        else:
            self.network.communicate()
            self._process_alarms()
            for node in self.network.nodes_sorted():
                self._node_step(node)
        logger.debug(
            "[{}] Step {} finished",
            self.name,
            self.network.algorithmState["step"],
        )
        self.network.algorithmState["step"] += 1

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
        )

    ### Algorithm methods ###

    def initializer(self):
        """
        Method used to initialize the algorithm. Is always called first.
        :class:`NodeAlgorithm` subclasses may want to reimplement it.

        Base implementation sends an INI message to the node with the lowest id.
        """
        logger.debug("Initializing algorithm {}.", self.name)
        node: "Node" = self.network.nodes_sorted()[0]
        node.push_to_inbox(Message(meta_header=NodeAlgorithm.INI))
        for node in self.network.nodes_sorted():
            node.status = self.Status.IDLE

    def send(self, source_node: "Node", message: Message):
        """
        Send a message to nodes listed in message's destination field.

        Note: Destination should be a list of nodes or one node.

        Update message's source field and inserts in node's outbox one copy
        of it for each destination.

        :param message: The message to be sent.
        :type message: Message
        """
        message.source = source_node
        if not isinstance(message.destination, Iterable):
            message.destination = [message.destination]
        for destination in message.destination:
            source_node.push_to_outbox(message.copy(), destination)

    ### Alarm methods ###

    def set_alarm(self, node: "Node", time: int, message: Message | None = None):
        """
        Set an alarm for the node.
        One unit of time is one step of the algorithm.
        After the time has passed, the alarm will trigger and the message will be sent to the node.
        When will that message be processed is not guaranteed to be immediate.

        Returns the alarm that was set, useful for disabling it later.

        :param node: The node for which the alarm is set.
        :type node: Node
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
        message.destination = node

        alarm = Alarm(time, message, node)
        self.alarms.append(alarm)
        return alarm

    def disable_all_node_alarms(self, node: "Node"):
        """
        Disable all alarms set for the node.

        :param node: The node for which the alarms are disabled.
        :type node: Node
        """
        to_delete_messages = [alarm.message for alarm in self.alarms if alarm.node == node]
        self.alarms = [alarm for alarm in self.alarms if alarm.node != node]

        for message in node.inbox.copy():
            if message in to_delete_messages and message in node.inbox:
                node.inbox.remove(message)

    def disable_alarm(self, alarm: Alarm):
        """
        Disable an alarm.

        :param alarm: The alarm to be disabled.
        :type alarm: Alarm
        """
        if alarm in self.alarms:
            self.alarms.remove(alarm)
        elif alarm.message in alarm.node.inbox:
            alarm.node.inbox.remove(alarm.message)

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
        elif alarm.message in alarm.node.inbox:
            alarm.node.inbox.remove(alarm.message)
            alarm.time_left += time_diff
            alarm.triggered = False
            self.alarms.append(alarm)
        else:
            raise ValueError("Alarm not found.")

    ### Private methods for algorithm execution ###

    def _node_step(self, node: "Node"):
        """Executes one step of the algorithm for given node."""
        message: Message = node.receive()

        if message:
            logger.debug("Processing step at node {}.", node.id)
            if message.destination is None or message.destination == node:
                # when destination is None it is broadcast message
                self._process_message(node, message)
            elif message.nexthop == node.id:
                self._forward_message(node, message)

    def _forward_message(self, node: "Node", message: Message):
        try:
            message.nexthop = node.memory["routing"][message.destination]
        except KeyError:
            logger.warning("Missing routing table or destination node not in it.")
        else:
            self.send(node, message)

    def _process_alarms(self):
        for alarm in self.alarms.copy():
            # copy to avoid errors produced by modifying the list while iterating
            alarm.time_left -= 1
            if alarm.time_left <= 0:
                self.alarms.remove(alarm)
                alarm.triggered = True
                alarm.node.push_to_inbox(alarm.message)

    def _process_message(self, node: "Node", message: Message):
        logger.debug("Processing message: 0x%x" % id(message))
        method_name = MSG_META_HEADER_MAP[message.meta_header]
        return self._process_action(method_name, node, message)

    def _process_action(self, action: Actions, node: "Node", message: Message):
        status: StatusValues = getattr(self.Status, node.status.value)

        method_name = f"{action}_{status}"
        default_name = f"{Actions.default}_{status}"

        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(node, message)
        elif hasattr(self, default_name):
            method = getattr(self, default_name)
            return method(node, message)

        logger.error(f"Method {self.name}.{action} not implemented for status {node.status}.")

    ### Metaclass methods ###

    def __configure_class__(clsname: str, bases: tuple[type, ...], dct: dict):
        """
        Metaclass method that configures the class by adding methods for all possible actions and statuses.

        :param clsname: The name of the class.
        :type clsname: str
        :param bases: The base classes of the class.
        :type bases: tuple[type, ...]
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
            def __unresolved_action_method__(alg_instance: "NodeAlgorithm", node: "Node", message: Message):
                alg_instance._process_action(action, node, message)

            dct[action] = __unresolved_action_method__

            for status in status_class:
                if status.implements(action):
                    # Create a method for invocations like `self.default_IDLE(node, message)`
                    # As the method is created in the class, super() will work.
                    dct[f"{action}_{status}"] = status.get_method(action)
