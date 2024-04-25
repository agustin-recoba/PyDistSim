from enum import StrEnum
from pymote.message import Message, MetaHeader as MessageMetaHeader
from pymote.logger import logger
from pymote.node import Node
from inspect import getmembers

MSG_META_HEADER_MAP = {
    MessageMetaHeader.NORMAL_MESSAGE: "receiving",
    MessageMetaHeader.INITALIZATION_MESSAGE: "spontaneously",
    MessageMetaHeader.ALARM_MESSAGE: "alarm",
}


class StatusValues(StrEnum):
    def __call__(self, func):
        assert func.__name__ in [
            *MSG_META_HEADER_MAP.values(),
            "default",
        ], f"Invalid function name '{func.__name__}'."

        setattr(self, func.__name__, func)
        setattr(getattr(self, func.__name__), "implemented", True)
        return func

    def default(self, *args, **kwargs):
        raise NotImplementedError(
            f"Rection 'default' not implemented for state '{self.value}'."
        )
    setattr(default, "implemented", False)

    def receiving(self, *args, **kwargs):
        raise NotImplementedError(
            f"Rection 'receiving' not implemented for state '{self.value}'."
        )
    setattr(receiving, "implemented", False)


    def spontaneously(self, *args, **kwargs):
        raise NotImplementedError(
            f"Rection 'spontaneously' not implemented for state '{self.value}'."
        )
    setattr(spontaneously, "implemented", False)

    def alarm(self, *args, **kwargs):
        raise NotImplementedError(
            f"Rection 'alarm' not implemented for state '{self.value}'."
        )
    setattr(alarm, "implemented", False)


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
        ), "Required params %s and default params %s should be unique." % (
            str(rps),
            str(list(dps.keys())),
        )

        dct["required_params"] = tuple(rps)
        dct["default_params"] = dps
        return super(AlgorithmMeta, cls).__new__(cls, clsname, bases, dct)


class Algorithm(object, metaclass=AlgorithmMeta):
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
        self.network = network
        self.name = self.__class__.__name__
        logger.debug("Instance of %s class has been initialized." % self.name)

        for required_param in self.required_params:
            if required_param not in list(kwargs.keys()):
                raise PymoteAlgorithmException("Missing required param.")

        # set default params
        for dp, val in list(self.default_params.items()):
            self.__setattr__(dp, val)

        # override default params
        for kw, arg in list(kwargs.items()):
            self.__setattr__(kw, arg)


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
        node = self.network.nodes()[0]
        self.network.outbox.insert(
            0, Message(meta_header=NodeAlgorithm.INI, destination=node)
        )
        for node in self.network.nodes():
            node.status = self.Status.IDLE

    def step(self, node:Node):
        """Executes one step of the algorithm for given node."""
        message: Message = node.receive()
        if message:
            if message.destination is None or message.destination == node:
                # when destination is None it is broadcast message
                return self._process_message(node, message)
            elif message.nexthop == node.id:
                self._forward_message(node, message)

    def _forward_message(self, node:Node, message: Message):
        try:
            message.nexthop = node.memory["routing"][message.destination]
        except KeyError:
            logger.warn("Missing routing table or destination node not in it.")
        else:
            node.send(message)

    def _process_message(self, node:Node, message: Message):
        status = getattr(self.Status, node.status.value)
        print(message)
        method_name = MSG_META_HEADER_MAP.get(message.meta_header, "default")
        method = getattr(status, method_name)
        
        if method.implemented:
            return method(self, node, message)
        else:
            return status.default(self, node, message)

    def statuserr(self, node:Node, message: Message):
        logger.error("Can't handle status %s." % node.status)


class NetworkAlgorithm(Algorithm):
    """
    Abstract base class for specific centralized algorithms.

    This class is used as base class holding real network algorithm
    classes in its __subclassess__ for easy instantiation

    Method __init__ and run should be implemented in subclass.

    """

    def run(self):
        raise NotImplementedError


class PymoteAlgorithmException(Exception):
    pass
