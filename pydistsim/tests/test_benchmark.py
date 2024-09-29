from pydistsim.benchmark import AlgorithmBenchmark, MetricCollector
from pydistsim.demo_algorithms.broadcast import Flood
from pydistsim.demo_algorithms.santoro2007.yoyo import YoYo
from pydistsim.network.behavior import NetworkBehaviorModel
from pydistsim.utils.testing import PyDistSimTestCase


class MyCustomMetricCollector(MetricCollector):

    def create_report(self):
        report = super().create_report()

        report["test_qty"] = 42
        report["event_qty"] = len(self.metrics)

        return report


class TestBenchmark(PyDistSimTestCase):
    def test_flood_benchmark(self):
        benchmark = AlgorithmBenchmark(
            ((Flood, {"initial_information": "Hello Wold Test!"}),),
            network_sizes=range(1, 15),
            network_behavior=NetworkBehaviorModel.UnorderedRandomDelayCommunication,
            metric_collector_factory=MyCustomMetricCollector,
            max_time=60,
        )

        benchmark.run()

        df = benchmark.get_results_dataframe()

        assert "test_qty" in df.columns and "event_qty" in df.columns

        benchmark.plot_analysis(
            x_vars=["Network type"],
            y_vars=["event_qty"],
            result_filter=lambda df: df["Network type"] in ("complete", "ring"),
            grouped=False,
        )

        benchmark.plot_analysis()

    def test_yoyo_benchmark(self):
        yoyo_benchmark = AlgorithmBenchmark(
            (YoYo,),
            network_sizes=range(1, 15),
            metric_collector_factory=MyCustomMetricCollector,
            max_time=60,
        )

        yoyo_benchmark.run()

        df = yoyo_benchmark.get_results_dataframe()

        assert "test_qty" in df.columns and "event_qty" in df.columns

        yoyo_benchmark.plot_analysis(
            x_vars=["Network type"],
            y_vars=["event_qty"],
            result_filter=lambda df: df["Network type"] in ("complete", "ring"),
            grouped=False,
        )

        yoyo_benchmark.plot_analysis()
