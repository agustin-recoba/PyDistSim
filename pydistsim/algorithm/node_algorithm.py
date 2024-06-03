from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from pydistsim.algorithm.base_algorithm import Algorithm
from pydistsim.logger import logger
from pydistsim.message import Message
from pydistsim.message import MetaHeader as MessageMetaHeader
from pydistsim.observers import ObservableEvents

if TYPE_CHECKING:
    from pydistsim.network import Node


class ActionEnum(StrEnum):
    default = "default"
    receiving = "receiving"
    spontaneously = "spontaneously"
    alarm = "alarm"


MSG_META_HEADER_MAP = {
    MessageMetaHeader.NORMAL_MESSAGE: ActionEnum.receiving,
    MessageMetaHeader.INITIALIZATION_MESSAGE: ActionEnum.spontaneously,
    MessageMetaHeader.ALARM_MESSAGE: ActionEnum.alarm,
}


@dataclass
class Alarm:
    time: int
    message: Message
    node: "Node"


class StatusValues(StrEnum):
    def __call__(self, func: Callable):
        assert (
            func.__name__ in ActionEnum.__members__
        ), f"Invalid function name '{func.__name__}', please make sure it is one of {list(ActionEnum.__members__)}."

        setattr(self, func.__name__, func)
        return func

    def implements(self, action: ActionEnum | str):
        return hasattr(self, str(action))


class NodeAlgorithm(Algorithm):
    """
    Abstract base class for specific distributed algorithms.

    In subclass following functions and attributes should be defined:

    - class attribute STATUS - dictionary in which keys are all possible
      node statuses and values are functions defining what node should do
      if in that status.
      STATUS must be written at the bottom after all functions are defined
    - all functions in STATUS.values() should be defined as class methods
    - initializer: (optionally) Pass INI message to nodes that should
      start the algorithm and set some attributes needed by the specific
      algorithm

    """

    INI = MessageMetaHeader.INITIALIZATION_MESSAGE

    class Status(StatusValues):
        IDLE = "IDLE"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alarms: list[Alarm] = []

    def step(self):
        logger.debug(
            "[{}] Step {} started",
            self.name,
            self.network.algorithmState["step"],
        )
        if not self.is_initialized():
            self.notify_observers(ObservableEvents.algorithm_started, self)
            self.initializer()
            # TODO: log a warning when initializer does not send any message
            # if not self.network.network_outbox:
            #     logger.warning("Initializer didn't send any message (even INI).")
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

    def _node_step(self, node: "Node"):
        """Executes one step of the algorithm for given node."""
        message: Message = node.receive()

        if message:
            logger.debug("Processing step at node {}.", node.id)
            if message.destination is None or message.destination == node:
                # when destination is None it is broadcast message
                processed = self._process_message(node, message)
                if not processed:
                    node.push_to_inbox(message)  # put back to start of queue
            elif message.nexthop == node.id:
                self._forward_message(node, message)

    def _forward_message(self, node: "Node", message: Message):
        try:
            message.nexthop = node.memory["routing"][message.destination]
        except KeyError:
            logger.warning("Missing routing table or destination node not in it.")
        else:
            self.send(node, message)

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

    def _process_alarms(self):
        for alarm in self.alarms.copy():
            # copy to avoid errors produced by modifying the list while iterating
            alarm.time -= 1
            if alarm.time == 0:
                self.alarms.remove(alarm)
                alarm.node.push_to_inbox(alarm.message)

    def set_alarm(self, node: "Node", time: int, message: Message | None = None):
        """
        Set an alarm for the node.
        One unit of time is one step of the algorithm.
        After the time has passed, the alarm will trigger and the message will be sent to the node.
        When will that message be processed is not guaranteed to be immediate.

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

    def disable_node_alarms(self, node: "Node"):
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
        if alarm.message in alarm.node.inbox:
            alarm.node.inbox.remove(alarm.message)

    def _process_message(self, node: "Node", message: Message):
        status: StatusValues = getattr(self.Status, node.status.value)
        logger.debug("Processing message: 0x%x" % id(message))
        method_name = MSG_META_HEADER_MAP[message.meta_header]

        if status.implements(method_name):
            method = getattr(status, method_name)
            method(self, node, message)
        elif status.implements(ActionEnum.default):
            method = getattr(status, ActionEnum.default)
            method(self, node, message)
        else:
            logger.error(f"Method {method_name} not implemented for status {node.status}.")
        return True

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
