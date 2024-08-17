from numpy import array, average, diag, dot, linalg, ones, sqrt

from pydistsim.demo_algorithms.niculescu2003.floodingupdate import FloodingUpdate


class Trilaterate(FloodingUpdate):

    required_params = (
        # key in memory for true position data (only landmarks)
        "truePositionKey",
        # key in memory for storing estimated position
        "positionKey",
        # key in memory for storing hopsize data
        "hopsizeKey",
    )

    def initiator_condition(self, node):
        return node.memory[self.truePositionKey] is not None  # if landmark

    def initiator_data(self, node):
        return node.memory[self.hopsizeKey]

    def handle_flood_message(self, node, message):
        if self.hopsizeKey in node.memory:
            return None
        node.memory[self.hopsizeKey] = message.data
        self.estimate_position(node)
        return node.memory[self.hopsizeKey]

    def estimate_position(self, node):
        TRESHOLD = 0.1
        MAX_ITER = 10

        # get landmarks with hopsize data
        landmarks = list(node.memory[self.dataKey].keys())
        # calculate estimated distances
        if len(landmarks) >= 3:
            landmark_distances = [node.memory[self.dataKey][lm][2] * node.memory[self.hopsizeKey] for lm in landmarks]
            landmark_positions = [array(node.memory[self.dataKey][lm][:2]) for lm in landmarks]
            # take centroid as initial estimation
            pos = average(landmark_positions, axis=0)
            W = diag(ones(len(landmarks)))
            counter = 0

            def dist(x, y):
                return sqrt(dot(x - y, x - y))

            while True:
                J = array([(lp - pos) / dist(lp, pos) for lp in landmark_positions])
                range_correction = array(
                    [dist(landmark_positions[li], pos) - landmark_distances[li] for li, lm in enumerate(landmarks)]
                )
                pos_correction = dot(linalg.inv(dot(dot(J.T, W), J)), dot(dot(J.T, W), range_correction))
                pos = pos + pos_correction
                counter += 1
                if sqrt(sum(pos_correction**2)) < TRESHOLD or counter >= MAX_ITER:
                    break
            if counter < MAX_ITER:
                node.memory[self.positionKey] = pos
