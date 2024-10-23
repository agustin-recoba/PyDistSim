from copy import copy, deepcopy
from inspect import getmembers
from typing import TYPE_CHECKING

from pydistsim.logging import logger
from pydistsim.observers import ObserverManagerMixin
from pydistsim.restrictions import CheckableRestriction
from pydistsim.restrictions.base_restriction import ApplicableRestriction

if TYPE_CHECKING:
    from pydistsim.network import NetworkType
    from pydistsim.simulation import Simulation


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

        assert len(rps) == len(set(rps)), "Some required params %s defined in multiple classes." % str(rps)
        assert len(all_params) == len(
            set(all_params)
        ), "Required params {} and default params {} should be unique.".format(
            str(rps),
            str(list(dps.keys())),
        )

        dct["required_params"] = tuple(rps)
        dct["default_params"] = dps

        logger.trace(f"Checking for __configure_class__ in dct of {clsname}")
        __configure_class__ = None
        if "__configure_class__" in dct:
            logger.trace("Found __configure_class__ in dct")
            __configure_class__ = dct["__configure_class__"]
        else:
            logger.trace("Did not find __configure_class__ in dct")
            for base in bases:
                if hasattr(base, "__configure_class__"):
                    logger.trace(f"Found __configure_class__ in base {base.__name__}")
                    __configure_class__ = base.__configure_class__
                    break
        if __configure_class__:
            logger.trace(f"Calling __configure_class__ for {clsname}")
            __configure_class__(clsname, bases, dct)

        return super().__new__(cls, clsname, bases, dct)


class BaseAlgorithm(ObserverManagerMixin, metaclass=AlgorithmMeta):
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

    algorithm_restrictions = ()
    "Tuple of restrictions that must be satisfied for the algorithm to run."

    def __init__(self, simulation: "Simulation", **kwargs):
        super().__init__()
        self.simulation: "Simulation" = simulation
        self.name = self.__class__.__name__
        logger.trace("Instance of {} class has been initialized.", self.name)

        for required_param in self.required_params:
            if required_param not in list(kwargs.keys()):
                raise AlgorithmException(f"Missing required param {required_param} for algorithm {self.name}.")

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

    def __hash__(self) -> int:
        return id(self)

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]

        # Shallow copy of the object
        copy_a = copy(self)
        memo[id(self)] = copy_a

        # Deep copy of the mutable attributes
        copy_a.simulation = deepcopy(self.simulation, memo)

        return copy_a

    @property
    def network(self) -> "NetworkType":
        return self.simulation.network

    def step(self, check_restrictions: bool, step: int):
        raise NotImplementedError

    def is_initialized(self):
        return self.simulation.algorithmState["step"] > 1 and self.simulation.get_current_algorithm() == self

    def is_halted(self):
        """
        Check if the distributed algorithm has come to an end or deadlock.
        """
        raise NotImplementedError

    def check_restrictions(self):
        """
        Check if the restrictions are satisfied. Does not apply ApplicableRestrictions.
        """
        logger.debug("Checking restrictions for algorithm {}.", self.name)
        for restriction in self.algorithm_restrictions:
            if issubclass(restriction, CheckableRestriction):
                logger.debug("Checking restriction {}.", restriction.__name__)
                if not restriction.check(self.network):
                    raise AlgorithmException(
                        f"Restriction {restriction.__name__} not satisfied for this network.\n"
                        + restriction.get_help_message(self.network)
                    )

    def apply_restrictions(self):
        """
        Apply all applicable restrictions.
        """
        for restriction in self.algorithm_restrictions:
            if issubclass(restriction, ApplicableRestriction):
                restriction.apply(self.network)

    def reset(self):
        """
        Reset the algorithm to its initial state.
        """
        ...


class AlgorithmException(Exception):
    pass
