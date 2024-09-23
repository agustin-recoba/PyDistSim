import os
import unittest

from pydistsim.demo_algorithms.broadcast import Flood
from pydistsim.network import Network, NetworkGenerator, NetworkType
from pydistsim.utils.npickle import read_npickle, write_npickle


class TestPickle(unittest.TestCase):
    def setUp(self):
        self.nets = []
        for size in (
            10,
            100,
            500,
        ):  # TODO at npickle.py says a recursion error occurs with 6000, couldnt reproduce it
            net = NetworkGenerator(size).generate_random_network()

            net.elected = net.nodes_sorted()[0]
            net.elected.memory[f"some_key_{size}"] = f"some_value_{size}"

            self.nets.append((size, net))

    def test_write_read(self):
        for i, (size, net) in enumerate(self.nets):
            net: Network
            with self.subTest(net=net):
                try:
                    write_npickle(net, f"net_test_{i}.tar.gz")

                    assert os.path.isfile(f"net_test_{i}.tar.gz"), "The file has not been created"

                    net_from_file: "NetworkType" = read_npickle(f"net_test_{i}.tar.gz")

                    assert type(net) == type(net_from_file), "The type of the object is not the same."

                    assert len(net.nodes()) == len(net_from_file.nodes()), "The number of nodes is not the same."

                    assert (
                        net.elected._internal_id == net_from_file.elected._internal_id
                    ), "The elected node is not the same."
                    assert (
                        net.elected.memory[f"some_key_{size}"] == net_from_file.elected.memory[f"some_key_{size}"]
                    ), "The value of the elected node is not the same."

                finally:
                    os.remove(f"net_test_{i}.tar.gz")
                    assert not os.path.isfile(f"net_test_{i}.tar.gz"), "The file has not been deleted"

    def test_read_not_found(self):
        with self.assertRaises(OSError):
            read_npickle("file_not_found.tar.gz")
