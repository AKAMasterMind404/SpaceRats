from robot.robot import Robot


class Bot1(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)

    def updatePingLikelihoodProbabilities(self):
        self.getPingAndUpdatePingLikelyhood()
        self.isMove = True