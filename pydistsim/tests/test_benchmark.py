from pydistsim.benchmark import AlgorithmBenchmark
from pydistsim.demo_algorithms.broadcast import Flood
from pydistsim.demo_algorithms.santoro2007.yoyo import YoYo
from pydistsim.metrics import MetricCollector
from pydistsim.network.behavior import ExampleProperties
from pydistsim.utils.testing import PyDistSimTestCase


class TestMetricCollector(MetricCollector):

    def create_report(self):
        report = super().create_report()

        report["test_qty"] = 42
        report["event_qty"] = len(self.metrics)

        return report


class TestBenchmark(PyDistSimTestCase):
    def test_flood_benchmark(self):
        benchmark = AlgorithmBenchmark(
            ((Flood, {"initial_information": "Hello Wold Test!"}),),
            network_sizes=range(1, 20),
            network_behavior=ExampleProperties.UnorderedRandomDelayCommunication,
            metric_collector_factory=TestMetricCollector,
        )

        benchmark.run()

        df = benchmark.get_results_dataframe()

        assert "test_qty" in df.columns and "event_qty" in df.columns

        benchmark.plot_analysis(
            x_vars=["Net. gen. type"],
            y_vars=["event_qty"],
            result_filter=lambda df: df["Net. gen. type"] in ("complete", "ring"),
            grouped=False,
        )

        benchmark.plot_analysis()

    def test_yoyo_benchmark(self):
        yoyo_benchmark = AlgorithmBenchmark(
            (YoYo,),
            network_sizes=range(1, 20),
            metric_collector_factory=TestMetricCollector,
        )

        yoyo_benchmark.run()

        df = yoyo_benchmark.get_results_dataframe()

        assert "test_qty" in df.columns and "event_qty" in df.columns

        yoyo_benchmark.plot_analysis(
            x_vars=["Net. gen. type"],
            y_vars=["event_qty"],
            result_filter=lambda df: df["Net. gen. type"] in ("complete", "ring"),
            grouped=False,
        )

        yoyo_benchmark.plot_analysis()
