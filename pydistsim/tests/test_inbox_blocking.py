import unittest

from pydistsim.algorithm import NodeAlgorithm, StatusValues
from pydistsim.algorithm.node_wrapper import NodeAccess
from pydistsim.message import Message
from pydistsim.network import NetworkGenerator
from pydistsim.simulation import Simulation


class TimerAlgorithm(NodeAlgorithm):

    class Status(StatusValues):
        BLOCKER = "BLOCKER"
        OTHER = "OTHER"

    def initializer(self):
        node0 = self.network.nodes_sorted()[0]
        node0.push_to_inbox(Message(meta_header=NodeAlgorithm.INI))
        node0.status = self.Status.BLOCKER

        node1 = self.network.nodes_sorted()[1]
        node1.push_to_inbox(Message(meta_header=NodeAlgorithm.INI))
        node1.status = self.Status.OTHER

    @Status.OTHER
    def spontaneously(self, node: NodeAccess, message: Message):
        n = tuple(node.neighbors())[0]

        self.send(node, 1, n, "ONE")
        self.send(node, 2, n, "TWO")
        self.send(node, 3, n, "THREE")
        self.send(node, 4, n, "FOUR")

    @Status.BLOCKER
    def spontaneously(self, node: NodeAccess, message: Message):
        n = tuple(node.neighbors())[0]

        self.close(node, n)
        self.block_inbox(node, lambda m: m.header != "FOUR")
        self.block_inbox(node, lambda m: m.data != 1)
        node.memory["ALARM"] = False
        self.set_alarm(node, 3)

    @Status.BLOCKER
    def alarm(self, node: NodeAccess, message: Message):
        n = tuple(node.neighbors())[0]
        node.memory["ALARM"] = True
        self.open(node, n)

    @Status.BLOCKER
    def receiving(self, node: NodeAccess, message: Message):
        print(message)

        assert node.memory["ALARM"]
        node.memory[f"RECEIVED_{node.clock}"] = str(message.data)


class TestMsgBlocking(unittest.TestCase):

    def test_blocking(self):
        self.net = NetworkGenerator.generate_complete_network(2)
        sim = Simulation(self.net)
        sim.algorithms = (TimerAlgorithm,)

        sim.run()

        for node in self.net.nodes():
            if node.status == TimerAlgorithm.Status.BLOCKER:
                assert "1" not in node.memory.values()
                assert "4" not in node.memory.values()
                assert "2" in node.memory.values()
                assert "3" in node.memory.values()
