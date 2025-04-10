import random
import math
from robot.robot import Robot
from helpers.generic import HelperService


class Bot1(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)

    def useDetector(self):
        """
        Simulates the rat detector ping:
        1. Computes ping probability based on distance to rat.
        2. Generates a random ping/no ping.
        3. Updates cell probabilities using Bayes' rule.
        """
        ship = self.ship

        # Calculate ping probability
        d = HelperService.manhattan_distance(self.position, self.ship.curr_rat_pos)
        ping_prob = math.exp(-ship.alpha * (d - 1))

        # Simulate ping (random number <= ping_prob)
        ping_received = random.random() <= ping_prob

        # Update probabilities based on ping
        self.update_rat_probabilities(ping_received)
        self.isMove = True

        ship.t += 1
        return ping_received
