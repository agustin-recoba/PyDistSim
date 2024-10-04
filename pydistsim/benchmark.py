"""
This module contains the :class:`AlgorithmBenchmark` class, which is used to benchmark the performance of a given
algorithm.
"""

from collections.abc import Callable, Iterable
from random import randint, random
from time import time
from typing import Any, Literal

from pandas import DataFrame

from pydistsim.algorithm.node_algorithm import AlgorithmException, NodeAlgorithm
from pydistsim.logging import logger
from pydistsim.metrics import MetricCollector
from pydistsim.network.behavior import NetworkBehaviorModel
from pydistsim.network.generator import NetworkGenerator
from pydistsim.network.network import BidirectionalNetwork, Network, NetworkType
from pydistsim.simulation import AlgorithmsParam, Simulation


def decide_directed_class(directed: bool):
    if directed:
        return Network
    else:
        return BidirectionalNetwork


def decide_rect_shape(n: int):
    "Auxiliary function to choose shape so that `a * b ≈ n` and neither a or b are equal to 1 (most of the time)."

    b = max(randint(int(n / 6), int(n / 3)), 1)
    a = int(n / b)
    return {"a": a, "b": b}


DETERMINISTIC_GENERATORS = {
    "complete": lambda n, directed: NetworkGenerator.generate_complete_network(n, decide_directed_class(directed)),
    "hypercube": lambda n, directed: NetworkGenerator.generate_hypercube_network(
        n, network_type=decide_directed_class(directed)
    ),
    "ring": lambda n, directed: NetworkGenerator.generate_ring_network(n, decide_directed_class(directed)),
    "star": lambda n, directed: NetworkGenerator.generate_star_network(n, decide_directed_class(directed)),
    "square mesh": lambda n, directed: NetworkGenerator.generate_mesh_network(
        n, torus=False, network_type=decide_directed_class(directed)
    ),
    "square torus": lambda n, directed: NetworkGenerator.generate_mesh_network(
        n, torus=True, network_type=decide_directed_class(directed)
    ),
}


RANDOM_GENERATORS = {
    "homogeneous": lambda n, directed: NetworkGenerator(n, directed=directed).generate_homogeneous_network(random()),
    "rectangular mesh": lambda n, directed: NetworkGenerator.generate_mesh_network(
        torus=False, **decide_rect_shape(n), network_type=decide_directed_class(directed)
    ),
    "rectangular torus": lambda n, directed: NetworkGenerator.generate_mesh_network(
        torus=True, **decide_rect_shape(n), network_type=decide_directed_class(directed)
    ),
}

GENERATORS = {"DETERMINISTIC": DETERMINISTIC_GENERATORS, "RANDOM": RANDOM_GENERATORS}


class AlgorithmBenchmark:
    """
    This class is used to benchmark the performance of a given algorithm.


    ### Usage

    .. code-block:: python

        from pydistsim.benchmark import AlgorithmBenchmark
        from pydistsim.network.behavior import NetworkBehaviorModel

        benchmark = AlgorithmBenchmark(
            ((Flood, {"initial_information": "Hello Wold!"}), ),
            network_sizes=range(1, 40),
            network_behavior=NetworkBehaviorModel.UnorderedRandomDelayCommunication,
        )

        benchmark.run()

        plot = benchmark.plot_analysis() # In IPython, this will create a plot with the results

        df = benchmark.get_results_dataframe() # Get the results as a pandas DataFrame

    ### Params

    :param algorithm: The algorithm to benchmark. It can be a single algorithm or a tuple of algorithms.
    :type algorithm: AlgorithmsParam =  tuple[type[BaseAlgorithm] | tuple[type[BaseAlgorithm], dict]]
    :param max_time: The maximum time in seconds to run the benchmark.
    :type max_time: float, optional
    :param network_sizes: The sizes of the networks to generate and run the algorithm on.
    :type network_sizes: Iterable[int], optional
    :param directed_network: If the generated networks must be directed.
    :type directed_network: bool, False by default
    :param check_algorithm_termination: Whether to check if the algorithm terminated correctly. Only for NodeAlgorithms.
    :type check_algorithm_termination: bool, optional
    :param network_behavior: The network behavior model to use.
    :type network_behavior: NetworkBehaviorModel, optional
    :param metric_collector_factory: A factory function to create a MetricCollector instance.
    :type metric_collector_factory: Callable[[], MetricCollector], optional
    :param network_generators: A dict of dicts containing network generators.
    :type network_generators: dict[Literal["DETERMINISTIC", "RANDOM"], dict[str, Callable[[int, bool], "NetworkType"]]]
    :param network_repeat_count: A dict mapping generation type with the amount of repeats.
    :type network_repeat_count: dict[Literal["DETERMINISTIC", "RANDOM"], int]
    """

    def __init__(
        self,
        algorithm: AlgorithmsParam,
        max_time: float = float("inf"),
        network_sizes: Iterable[int] = range(1, 20),
        directed_network: bool = False,
        check_algorithm_termination: bool = True,
        network_behavior: "NetworkBehaviorModel" = NetworkBehaviorModel.IdealCommunication,
        metric_collector_factory: Callable[[], MetricCollector] = MetricCollector,
        network_generators: dict[
            Literal["DETERMINISTIC", "RANDOM"], dict[str, Callable[[int], "NetworkType"]]
        ] = GENERATORS,
        network_repeat_count: dict[Literal["DETERMINISTIC", "RANDOM"], int] = {"DETERMINISTIC": 1, "RANDOM": 5},
    ):
        self.results = []
        self.errors = []

        self.algorithm = algorithm
        self.max_time = max_time
        self.network_sizes = list(network_sizes)
        self.directed_network = directed_network
        self.check_algorithm_termination = check_algorithm_termination
        self.network_behavior = network_behavior
        self.metric_collector_factory = metric_collector_factory
        self.network_generators = network_generators
        self.network_repeat_count = network_repeat_count

    def run(self):
        """
        Run the benchmark
        """
        start_time = time()

        tests = self.get_test_params()

        for network_size, gen_name, gen in tests:
            if time() - start_time > self.max_time:
                logger.warning(
                    f"Time limit reached, stopping benchmark before on {gen_name} network of size {network_size}"
                )
                return

            try:
                logger.trace(f"Generating network '{gen_name}' of size {network_size}")
                network: "NetworkType" = gen(network_size, self.directed_network)
            except ValueError as e:
                logger.debug(f"Failed to generate '{gen_name}' network of size {network_size}. Reason: {e}")
                continue

            logger.trace(f"Running simulation on '{gen_name}' network of size {len(network)}")
            network.behavioral_properties = self.network_behavior

            metrics = self.metric_collector_factory()
            sim = Simulation(network, self.algorithm)
            algorithms_instances: Iterable[NodeAlgorithm] = sim._algorithms
            sim.add_observers(metrics)

            try:
                sim.run()
            except Exception as e:
                self._save_error(gen_name, network, e, "Algorithm failed to run.")

            if self.check_algorithm_termination:
                try:
                    for algorithm_instance in algorithms_instances:
                        algorithm_instance.check_algorithm_termination()
                except AlgorithmException as e:
                    self._save_error(gen_name, network, e, "S_term check failed.")

            self._save_result(gen_name, network, **metrics.create_report())

    def get_test_params(self) -> Iterable[tuple[int, str, Callable[[int], "NetworkType"]]]:
        tests = (
            (network_size, generation_name, generator)
            for network_size in self.network_sizes
            for gen_type, gen_dict in self.network_generators.items()
            for i in range(self.network_repeat_count[gen_type])
            for generation_name, generator in gen_dict.items()
        )

        return tests

    def _save_result(self, gen_name: str, network: "NetworkType", **metrics):
        logger.debug(f"Algorithm terminated correctly on '{gen_name}' network of size {len(network)}")
        self.results.append(
            {
                "Net. node count": len(network),
                "Net. edge count": len(network.edges()),
                "Network type": gen_name,
                **metrics,
            }
        )

    def _save_error(self, gen_name: str, network: "NetworkType", e: Exception, error_type: str):
        logger.error(f"{error_type} On '{gen_name}' network of size {len(network)}")
        self.errors.append(
            {
                "Net. node count": len(network),
                "Net. edge count": len(network.edges()),
                "Network type": gen_name,
                "Error type": error_type,
                "exception_args": e.args,
            }
        )

    def get_results_dataframe(self, grouped: bool = False):
        """
        Get the results of the benchmark as a pandas DataFrame.

        :param grouped: Group results by size and generation type.
        :param grouped: bool, optional
        :return: Results of the benchmark as a table.
        :rtype: DataFrame
        """

        # Group by "Net. node count", "Network type", "Net. edge count" and calculate the mean of the other columns
        # and return without the grouped rows
        if not grouped:
            return DataFrame(self.results)

        return (
            DataFrame(self.results).groupby(["Net. node count", "Network type", "Net. edge count"]).mean().reset_index()
        )

    def plot_analysis(
        self,
        x_vars: Iterable[str] = None,
        y_vars: Iterable[str] = None,
        result_filter: Callable[[dict[str, Any]], bool] = None,
        grouped=True,
        pairplot_kwargs: dict[str, Any] = {},
    ):
        """
        Plot the results of the benchmark using seaborn pairplot.

        ### Example call:

        .. code-block:: python

            benchmark.plot_analysis(
                x_vars=["Net. node count"],
                y_vars=["Qty. of messages sent", "Qty. of steps"],
                result_filter=lambda df: df["Network type"] in ('complete', 'ring'),
            )

        ### Params

        :param x_vars: The variables to plot on the x-axis. By default, it is node count and edge count.
        :type x_vars: Iterable[str], optional
        :param y_vars: The variables on the y-axis. By default, it is all variables except node count and edge count.
        :type y_vars: Iterable[str], optional
        :param result_filter: Filter the results row by row. Optional.
        :type result_filter: Callable[[dict[str, Any]], bool]
        :param grouped: Whether to group the results by network size and generation type.
        :type grouped: bool, optional
        :return: The seaborn pairplot object.
        """
        import seaborn as sns

        df = self.get_results_dataframe(grouped)

        if y_vars is None:
            y_vars = set(df.columns)
            y_vars.remove("Network type")
        else:
            y_vars = set(y_vars)

        x_vars = x_vars or {"Net. node count", "Net. edge count"}
        y_vars.remove("Net. node count") if "Net. node count" in y_vars else None
        y_vars.remove("Net. edge count") if "Net. edge count" in y_vars else None

        if result_filter:
            df = df[df.apply(result_filter, axis=1)]

        hue = None
        if df["Network type"].nunique() > 1:
            hue = "Network type"

        return sns.pairplot(df, x_vars=x_vars, y_vars=y_vars, hue=hue, diag_kind="hist", **pairplot_kwargs)
