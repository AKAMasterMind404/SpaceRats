from robot.robot import Robot
from helpers.generic import HelperService
import constants as cnt


class Bot3(Robot):
    def __init__(self, ship, position):
        super().__init__(ship, position)
        self.rat_probability = self._getInitialProbabilities()
        self.pingLikelyHood = self._getInitialProbabilities()

    def updateRatProbabilities(self):
        ship = self.ship
        total_prob = 0
        total_prob_list = []

        for cell in ship.currently_open:
            p_cell_new = 0
            cell_neighbors = HelperService.getOpenNeighbourListForNode(ship, cell, isIgnoreDiagonals=True)

            for neighbour in cell_neighbors:
                pRatInNeighbor = 0 if cell == self.position else self.rat_probability[neighbour]
                neighbourNeighbours = HelperService.getOpenNeighbourListForNode(ship, neighbour, isIgnoreDiagonals=True)
                pRatFromCellToNeighbor = 1 / len(neighbourNeighbours)
                p_cell_new += pRatInNeighbor * pRatFromCellToNeighbor

            total_prob += p_cell_new
            total_prob_list.append(cell)

        for i, cell in enumerate(ship.currently_open):
            self.rat_probability[cell] = total_prob_list[i] / total_prob

    def updatePingLikelyhoodProbabilities(self):
        ship = self.ship
        ping_received = self._getPingFromCurrCell()
        bot_pos = self.position
        rat_pos = ship.curr_rat_pos

        total_prob = 0
        probList = []

        for cell in ship.currently_open:
            p_rat_prob_given_ping = self.rat_probability[cell] if ping_received else 1 - self.rat_probability[cell]
            p_rat_in_cell_new = (p_rat_prob_given_ping * self.pingLikelyHood[cell]) / HelperService.manhattan_distance(
                bot_pos, rat_pos)
            probList.append(p_rat_in_cell_new)
            total_prob += p_rat_in_cell_new

        for i, cell in enumerate(ship.currently_open):
            self.rat_probability[cell] = probList[i] / total_prob

    def _getInitialProbabilities(self):
        openCells = self.ship.currently_open
        allProbabilities = dict()

        for cell in openCells:
            allProbabilities[cell] = 1 / len(openCells)

        return allProbabilities
