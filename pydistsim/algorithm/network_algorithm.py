from pydistsim.algorithm.base_algorithm import Algorithm


class NetworkAlgorithm(Algorithm):
    """
    Abstract base class for specific centralized algorithms.

    This class is used as base class holding real network algorithm
    classes in its __subclassess__ for easy instantiation

    Method __init__ and run should be implemented in subclass.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_halted = False

    def step(self):
        self._is_halted = True
        return self.run()

    def run(self):
        raise NotImplementedError

    def is_halted(self):
        return self._is_halted
