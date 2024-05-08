from collections.abc import Callable
from enum import StrEnum
from inspect import getmembers

import pydistsim.network as nt
from pydistsim.logger import logger
from pydistsim.message import Message
from pydistsim.message import MetaHeader as MessageMetaHeader
from pydistsim.node import Node


class ActionEnum(StrEnum):
    default = "default"
    receiving = "receiving"
    spontaneously = "spontaneously"
    alarm = "alarm"


MSG_META_HEADER_MAP = {
    MessageMetaHeader.NORMAL_MESSAGE: ActionEnum.receiving,
    MessageMetaHeader.INITALIZATION_MESSAGE: ActionEnum.spontaneously,
    MessageMetaHeader.ALARM_MESSAGE: ActionEnum.alarm,
}


class StatusValues(StrEnum):
    def __call__(self, func: Callable):
        assert (
            func.__name__ in ActionEnum.__members__
        ), f"Invalid function name '{func.__name__}', please make sure it is one of {list(ActionEnum.__members__)}."

        setattr(self, func.__name__, func)
        return func

    def implements(self, action: ActionEnum | str):
        return hasattr(self, str(action))


class AlgorithmMeta(type):
    """Metaclass for required and default params extension and update."""

    def __new__(cls, clsname, bases, dct):
        """
        Collect required and default params from class bases and extend and
        update those in dct that have been sent for new class.

        """
        rps = []
        dps = {}
        for base in bases[::-1]:
            base_rps = dict(getmembers(base)).get("required_params", [])
            rps.extend(base_rps)
            base_dps = dict(getmembers(base)).get("default_params", {})
            dps.update(base_dps)
        rps.extend(dct.get("required_params", []))
        dps.update(dct.get("default_params", {}))
        all_params = rps + list(dps.keys())

        assert len(rps) == len(
            set(rps)
        ), "Some required params %s defined in multiple classes." % str(rps)
        assert len(all_params) == len(
            set(all_params)
        ), "Required params {} and default params {} should be unique.".format(
            str(rps),
            str(list(dps.keys())),
        )

        dct["required_params"] = tuple(rps)
        dct["default_params"] = dps
        return super().__new__(cls, clsname, bases, dct)


class Algorithm(metaclass=AlgorithmMeta):
    """
    Abstract base class for all algorithms.

    Currently there are two main subclasses:
        * NodeAlgorithm used for distributed algorithms
        * NetworkAlgorithm used for centralized algorithms

    When writing new algorithms make them subclass either of NodeAlgorithm or
    NetworkAlgorithm.

    Every algorithm instance has a set of required and default params:
        * Required params must be given to algorithm initializer as a keyword
            arguments.
        * Default params can be given to algorithm initializer as a keyword
            arguments, if not their class defines default value.

    Note: On algorithm initialization all params are converted to instance
    attributes.

    For example:

    class SomeAlgorithm(NodeAlgorithm):
        required_params = ('rp1',)
        default_params = {'dp1': 'dv1',}

    >>> net = Network()
    >>> alg = SomeAlgorithm(net, rp1='rv1')
    >>> alg.rp1
    'rv1'
    >>> alg.dp1
    'dv1'

    Params in algorithm subclasses are inherited from its base classes, that
    is, required params are extended and default are updated:
        * required_params are union of all required params of their ancestor
            classes.
        * default_params are updated so default values are overridden in
            subclasses

    """

    required_params = ()
    default_params = {}

    def __init__(self, network, **kwargs):
        self.network: nt.Network = network
        self.name = self.__class__.__name__
        logger.debug("Instance of %s class has been initialized." % self.name)

        for required_param in self.required_params:
            if required_param not in list(kwargs.keys()):
                raise PyDistSimAlgorithmException("Missing required param.")

        # set default params
        for dp, val in list(self.default_params.items()):
            self.__setattr__(dp, val)

        # override default params
        for kw, arg in list(kwargs.items()):
            self.__setattr__(kw, arg)

    def __eq__(self, value: object) -> bool:
        return self.__dict__ == value.__dict__ and isinstance(value, self.__class__)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


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

    As indication of global termination of algorithm some method could
    optionally return True.

    """

    INI = MessageMetaHeader.INITALIZATION_MESSAGE

    class Status(StatusValues):
        IDLE = "IDLE"

    def initializer(self):
        """Pass INI message to certain nodes in network based on type."""
        node = self.network.nodes_sorted()[0]
        self.network.outbox.insert(
            0, Message(meta_header=NodeAlgorithm.INI, destination=node)
        )
        for node in self.network.nodes_sorted():
            node.status = self.Status.IDLE

    def step(self, node: Node):
        """Executes one step of the algorithm for given node."""
        message: Message = node.receive()
        if message:
            if message.destination is None or message.destination == node:
                # when destination is None it is broadcast message
                return self._process_message(node, message)
            elif message.nexthop == node.id:
                self._forward_message(node, message)

    def _forward_message(self, node: Node, message: Message):
        try:
            message.nexthop = node.memory["routing"][message.destination]
        except KeyError:
            logger.warning("Missing routing table or destination node not in it.")
        else:
            node.send(message)

    def _process_message(self, node: Node, message: Message):
        status = getattr(self.Status, node.status.value)
        print(message)
        method_name = MSG_META_HEADER_MAP[message.meta_header]

        if status.implements(method_name):
            method = getattr(status, method_name)
            return method(self, node, message)
        elif status.implements(ActionEnum.default):
            method = getattr(status, ActionEnum.default)
            return method(self, node, message)
        else:
            logger.error(
                f"Method {method_name} not implemented for status {node.status}."
            )


class NetworkAlgorithm(Algorithm):
    """
    Abstract base class for specific centralized algorithms.

    This class is used as base class holding real network algorithm
    classes in its __subclassess__ for easy instantiation

    Method __init__ and run should be implemented in subclass.

    """

    def run(self):
        raise NotImplementedError


class PyDistSimAlgorithmException(Exception):
    pass
