import time
import random
import math
from robot.robot import Robot
import constants as cnt
from helpers.generic import HelperService


class Bot2(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)
        self.sensedCount = 0

    def updateProbabilities(self):
        """
        Simulates the rat detector ping:
        1. Computes ping probability based on distance to rat.
        2. Generates a random ping/no ping.
        3. Updates cell probabilities using Bayes' rule.
        """
        ping_received = self._getPingFromCurrCell()

        # Update probabilities based on ping
        self._getPingAndRedistributeProbabilities(ping_received)
        if self.sensedCount < 5:
            HelperService.printDebug(f"Sensed {self.sensedCount + 1} times, ping was {'received' if ping_received else 'not received'}")
            time.sleep(cnt.TIME_RATE)
            self.sensedCount += 1
        else:
            self.isMove = True
            self.sensedCount = 0
        return ping_received