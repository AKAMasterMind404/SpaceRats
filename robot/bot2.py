from robot.robot import Robot
import constants as cnt


class Bot2(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)
        self.sensedCount = 0

    def updatePingLikelihoodProbabilities(self):
        self.getPingAndUpdatePingLikelyhood()
        if self.sensedCount < cnt.MAX_SENSE:
            self.sensedCount += 1
        else:
            self.isMove = True
            self.sensedCount = 0