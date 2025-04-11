import random
import math
from robot.robot import Robot
from helpers.generic import HelperService


class Bot1(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)

    def updatePingLikelyhoodProbabilities(self):
        """
        Simulates the rat detector ping:
        1. Computes ping probability based on distance to rat.
        2. Generates a random ping/no ping.
        3. Updates cell probabilities using Bayes' rule.
        """
        ping_received = self._getPingFromCurrCell()

        # Update probabilities based on ping
        self._getPingAndRedistributeProbabilities(ping_received)
        self.isMove = True
        self.ship.t += 1

        return ping_received

