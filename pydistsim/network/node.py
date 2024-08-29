from copy import copy, deepcopy
from typing import TYPE_CHECKING, Optional

from pydistsim.conf import settings
from pydistsim.logging import LogLevels, logger
from pydistsim.network.sensor import CompositeSensor
from pydistsim.observers import ObservableEvents, ObserverManagerMixin

if TYPE_CHECKING:
    from pydistsim.message import Message
    from pydistsim.network.network import NetworkType
    from pydistsim.network.sensor import Sensor


class Node(ObserverManagerMixin):
    """
    Represents a node in a network.

    :param network: Optional network object to which the node belongs.
    :type network: Network, optional
    :param commRange: Communication range of the node.
    :type commRange: int, optional
    :param sensors: Tuple of sensor types or names.
    :type sensors: tuple[type[Sensor] | str], optional
    :param kwargs: Additional keyword arguments.
    """

    next_node_id = 1

    def __init__(
        self,
        network: Optional["NetworkType"] = None,
        commRange: None | int = None,
        sensors: None | tuple[type["Sensor"] | str] = None,
        **kwargs,
    ):
        super().__init__()
        self._compositeSensor = CompositeSensor(self, sensors or settings.SENSORS)
        self.network = network
        self._commRange = commRange or settings.COMM_RANGE
        self.id = self.__class__.next_node_id
        self.__class__.next_node_id += 1
        self._inboxDelay = True

        self._status = None
        self.outbox: list["Message"] = []
        self._inbox: list["Message"] = []
        self.memory = {}
        self.clock = 0

    def __repr__(self):
        return self.__repr_str__(self.id)

    @staticmethod
    def __repr_str__(id):
        return "<Node id=%s>" % id

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]

        # Shallow copy of the object
        copy_n = copy(self)
        memo[id(self)] = copy_n

        copy_n.id = self.__class__.next_node_id
        self.__class__.next_node_id += 1

        # Deep copy of the mutable attributes
        copy_n._compositeSensor = deepcopy(self._compositeSensor, memo)
        copy_n.network = deepcopy(self.network, memo)
        copy_n.outbox = deepcopy(self.outbox, memo)
        copy_n._inbox = deepcopy(self._inbox, memo)
        copy_n.memory = deepcopy(self.memory, memo)

        copy_n.clear_observers()

        return copy_n

    @property
    def status(self):
        """
        Get the status of the node.

        :return: The status of the node.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status: str):
        """
        Set the status of the node.

        :param status: The status to be set.
        :type status: str
        """
        self.notify_observers(
            ObservableEvents.node_status_changed,
            node=self,
            previous_status=self._status,
            new_status=status,
        )
        self._status = status

    def reset(self):
        """
        Reset the node's state.

        Clears the outbox, inbox, status, and memory of the node.
        """
        self.outbox: list["Message"] = []
        self._inbox: list["Message"] = []
        self._status = None
        self.memory = {}
        self.clock = 0

    def receive(self):
        """
        Pop message from inbox but only if it has been there at least one step.

        Messages should be delayed for one step for visualization purposes.
        Messages are processed without delay only if they are pushed into empty
        inbox. So if inbox is empty when push_to_inbox is called _inboxDelay is
        set to True.

        This method is used only internally and is not supposed to be used
        inside algorithms.

        :return: The received message, or None if no message is available.
        :rtype: Message or None
        """
        if self._inbox and not self._inboxDelay:
            # TODO: implement precedence in message type: Spontaneously > Alarm > Receiving
            message = self._inbox.pop()
            logger.debug("Node {} received message {}", self.id, message.__repr__())
        else:
            message = None
        self._inboxDelay = False
        return message

    @property
    def inbox(self):
        """
        Get the inbox of the node.

        :return: The inbox of the node.
        :rtype: list[Message]
        """
        return self._inbox

    def push_to_inbox(self, message: "Message"):
        """
        Push a message to the inbox of the node.

        :param message: The message to be pushed to the inbox.
        :type message: Message
        """
        self._inboxDelay = self._inboxDelay or not self._inbox
        self._inbox.insert(0, message)
        logger.debug("Message delivered to {}", self)
        self.notify_observers(ObservableEvents.message_delivered, message)

    def push_to_outbox(self, message: "Message", destination: "Node"):
        """
        Push a message to the outbox of the node.

        :param message: The message to be pushed to the outbox.
        :type message: Message
        :param destination: The destination node of the message.
        :type destination: Node
        """
        message.destination = destination
        self.outbox.insert(0, message)
        logger.debug("Node {} sent message {}.", self.id, message.__repr__())
        self.notify_observers(ObservableEvents.message_sent, message)

    @property
    def compositeSensor(self):
        """
        Get the composite sensor of the node.

        :return: The composite sensor of the node.
        :rtype: CompositeSensor
        """
        return self._compositeSensor

    @compositeSensor.setter
    def compositeSensor(self, compositeSensor):
        """
        Set the composite sensor of the node.

        :param compositeSensor: The composite sensor to be set.
        :type compositeSensor: CompositeSensor
        """
        self._compositeSensor = CompositeSensor(self, compositeSensor)

    @property
    def sensors(self):
        """
        Get the sensors of the node.

        :return: The sensors of the node.
        :rtype: list[Sensor]
        """
        return self._compositeSensor.sensors

    @sensors.setter
    def sensors(self, sensors: tuple[type["Sensor"] | str]):
        """
        Set the sensors of the node.

        :param sensors: The sensors to be set.
        :type sensors: tuple[type[Sensor] | str]
        """
        self._compositeSensor = CompositeSensor(self, sensors)

    @property
    def commRange(self) -> int:
        """
        Get the communication range of the node.

        :return: The communication range of the node.
        :rtype: int
        """
        return self._commRange

    @commRange.setter
    def commRange(self, commRange: int):
        """
        Set the communication range of the node.

        :param commRange: The communication range to be set.
        :type commRange: int
        """
        self._commRange = commRange
        if self.network and hasattr(self.network, "recalculate_edges"):
            self.network.recalculate_edges([self])

    def get_log(self):
        """
        Get the log messages stored in the node's memory.

        :return: The log messages.
        :rtype: list[tuple[LogLevels, str, dict]]
        """
        if "log" not in self.memory:
            self.memory["log"] = []
        return self.memory["log"]

    def log(self, message: str, level: LogLevels = LogLevels.WARNING):
        """
        Insert a log message in the node's memory.

        :param message: The log message to be inserted.
        :type message: str
        :param level: The log level of the message.
        :type level: LogLevels, optional
        """
        assert isinstance(message, str)
        context = {
            "algorithm": str(self.network.simulation.get_current_algorithm()),
            "algorithmState": self.network.simulation.algorithmState,
            "clock": self.clock,
        }
        if "log" not in self.memory:
            self.memory["log"] = [(level, message, context)]
        else:
            self.memory["log"].append((level, message, context))

    def get_dic(self):
        """
        Get the node's information as a dictionary.

        :return: The node's information.
        :rtype: dict
        """
        return {
            "1. info": {
                "id": self.id,
                "status": self.status or "",
                "position": self.network.pos[self],
                "orientation": self.network.ori[self],
            },
            "2. communication": {
                "range": self.commRange,
                "inbox": self.box_as_dic("inbox"),
                "outbox": self.box_as_dic("outbox"),
            },
            "3. memory": self.memory,
            "4. sensors": {
                sensor.name(): (
                    "%s(%.3f)"
                    % (
                        sensor.probabilityFunction.name,
                        sensor.probabilityFunction.scale,
                    )
                    if hasattr(sensor, "probabilityFunction") and sensor.probabilityFunction is not None
                    else ("", 0)
                )
                for sensor in self.compositeSensor.sensors
            },
            "5. clock": self.clock,
        }

    def box_as_dic(self, box: str):
        """
        Convert a message box to a dictionary representation.

        :param box: The message box to be converted.
        :type box: str
        :return: The dictionary representation of the message box.
        :rtype: dict
        """
        messagebox = self.__getattribute__(box)
        dic = {}
        for i, message in enumerate(messagebox):
            dic.update(
                {
                    "%d. Message"
                    % (i + 1,): {
                        "1 header": message.header,
                        "2 source": message.source,
                        "3 destination": message.destination,
                        "4 data": message.data,
                    }
                }
            )
        return dic

    def unbox(self):
        return self
