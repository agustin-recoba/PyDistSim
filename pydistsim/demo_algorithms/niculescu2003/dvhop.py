from numpy import array, concatenate, dot, sqrt

from pydistsim.algorithm.node_wrapper import SensorNodeAccess
from pydistsim.demo_algorithms.niculescu2003.floodingupdate import FloodingUpdate


class DVHop(FloodingUpdate):
    """
    Data is {landmark: [x,y,hop_count], ...}
    """

    required_params = ("truePositionKey", "hopsizeKey")
    NODE_ACCESS_TYPE = SensorNodeAccess

    def initiator_condition(self, node: "SensorNodeAccess"):
        node.memory[self.truePositionKey] = node.compositeSensor.read().get("TruePos", None)
        # true if node is one of the landmarks
        return node.memory[self.truePositionKey] is not None

    def initiator_data(self, node: "SensorNodeAccess"):
        return {node.id: concatenate((node.memory[self.truePositionKey][:2], [1]))}

    def handle_flood_message(self, node: "SensorNodeAccess", message):
        if self.dataKey not in node.memory:
            node.memory[self.dataKey] = {}
        updated_data = {}
        for landmark_id, landmark_data in list(message.data.items()):
            # skip if landmark in message data is current node
            if landmark_id == node.id:
                continue
            # update only if this is first received data from landmark or new
            # hopcount is smaller than previous minimum
            if (
                landmark_id not in node.memory[self.dataKey]
                or landmark_data[2] < node.memory[self.dataKey][landmark_id][2]
            ):
                node.memory[self.dataKey][landmark_id] = array(landmark_data)
                # increase hopcount
                landmark_data[2] += 1
                updated_data[landmark_id] = landmark_data

        # if node is one of the landmarks then it should recalculate hopsize
        if node.memory[self.truePositionKey] is not None:
            self.recalculate_hopsize(node)

        return updated_data

    def recalculate_hopsize(self, node: SensorNodeAccess):
        pos = node.memory[self.truePositionKey]
        try:
            landmarks_count = len(node.memory[self.dataKey])
        except KeyError:
            pass
        else:

            def dist(x, y):
                return sqrt(dot(x - y, x - y))

            if landmarks_count > 0:
                node.memory[self.hopsizeKey] = sum(
                    [dist(lp[:2], pos) for lp in list(node.memory[self.dataKey].values())]
                ) / sum([lp[2] for lp in list(node.memory[self.dataKey].values())])
