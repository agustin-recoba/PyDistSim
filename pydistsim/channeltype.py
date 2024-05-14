from typing import TYPE_CHECKING

from numpy import sqrt
from numpy.random import random

from pydistsim.conf import settings

if TYPE_CHECKING:
    from pydistsim.environment import Environment
    from pydistsim.network import Network
    from pydistsim.node import Node


class ChannelType:
    """ChannelType abstract base class.

    This class represents an abstract base class for different types of channels.
    Subclasses of ChannelType should implement the `in_comm_range` method.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def __new__(self, environment: "Environment" = None, **kwargs):
        """Return instance of default ChannelType."""
        for cls in self.__subclasses__():
            if cls.__name__ == settings.CHANNEL_TYPE:
                return super().__new__(cls)

        # if self is not ChannelType class (as in pickle.load_newobj) return
        # instance of self
        return object.__new__(self)

    def in_comm_range(self, network: "Network", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        This method should be implemented by subclasses to determine if two nodes
        are within communication range.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError


class Udg(ChannelType):
    """Unit disc graph channel type.

    This class represents the Unit Disc Graph (UDG) channel type. It determines if
    two nodes are within communication range based on their positions and communication
    range.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def __init__(self, environment: "Environment"):
        self.environment = environment

    def in_comm_range(self, network: "Network", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        Two nodes are in communication range if they can see each other and are
        positioned so that their distance is smaller than the communication range.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        p1 = network.pos[node1]
        p2 = network.pos[node2]
        d = sqrt(sum(pow(p1 - p2, 2)))
        if d < node1.commRange and d < node2.commRange:
            if self.environment.are_visible(p1, p2):
                return True
        return False


class Complete(ChannelType):
    """Complete channel type.

    This class represents the Complete channel type. It always returns True,
    indicating that any two nodes are within communication range.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def __init__(self, environment: "Environment"):
        self.environment = environment

    def in_comm_range(self, network: "Network", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        This method always returns True, indicating that any two nodes are within
        communication range.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        return True


class SquareDisc(ChannelType):
    """Square Disc channel type.

    This class represents the Square Disc channel type. It determines if two nodes
    are within communication range based on their positions, communication range,
    and a probability of connection.

    :param environment: The environment in which the channel operates.
    :type environment: Environment
    """

    def __init__(self, environment: "Environment"):
        self.environment = environment

    def in_comm_range(self, network: "Network", node1: "Node", node2: "Node"):
        """Check if two nodes are within communication range.

        Two nodes are in communication range if they can see each other, are positioned
        so that their distance is smaller than the communication range, and satisfy a
        probability of connection.

        :param network: The network in which the nodes are connected.
        :type network: Network
        :param node1: The first node.
        :type node1: Node
        :param node2: The second node.
        :type node2: Node
        :return: True if the nodes are within communication range, False otherwise.
        :rtype: bool
        """
        p1 = network.pos[node1]
        p2 = network.pos[node2]
        d = sqrt(sum(pow(p1 - p2, 2)))
        if random() > d**2 / node1.commRange**2:
            if self.environment.are_visible(p1, p2):
                assert node1.commRange == node2.commRange
                return True
        return False
