import math
from abc import abstractmethod
import networkx as nx
from helpers.draw_grid import draw_grid_internal
from graph.djikstras import compatibleGraph, djikstras, getPathFromATOB
from helpers.generic import HelperService


class Robot:
    def __init__(self, ship, position):
        self.ship = ship  # Ship grid (30x30)
        self.position = position  # Bot's current position (set after Phase 1)
        self.path = None
        self.isMove = False
        self.targetCell = None
        self.isRatMoving = ship.is_rat_moving
        self.rat_probability = {}  # KB: Maps cells to rat probabilities
        self.initialize_rat_probabilities()

    def moveBot(self):
        if self.path is None:
            target_cell = HelperService.pickACellWithHighestRatProbability(self.rat_probability)
            self.targetCell = target_cell
            self.path = self.calculatePath(target_cell)
            draw_grid_internal(self.ship)

        if len(self.path) > 0:
            self.position = self.path.pop(0)
            isBotFound = self.checkIfBotInCurrentCellAndUpdateRatKnowledge()
            if isBotFound: return isBotFound
        else:
            self.isMove = False
            self.path = None

        draw_grid_internal(self.ship)
        return False

    @abstractmethod
    def useDetector(self):
        pass

    def initialize_rat_probabilities(self):
        """Initialize uniform probabilities for all open cells (except bot's position)."""
        open_cells = self.ship.currently_open
        total_cells = len(open_cells)
        for cell in open_cells:
            self.rat_probability[cell] = 1.0 / total_cells
        return

    def checkIfBotInCurrentCellAndUpdateRatKnowledge(self):
        if self.position == self.ship.curr_rat_pos:
            return True

        # Set current cell probability to 0 (rat not here)
        isRatStationary = not self.ship.is_rat_moving
        if isRatStationary:
            self.rat_probability[self.position] = 0

        # Re-normalize: Divide all probabilities by the sum of remaining probabilities
        total_prob = sum(self.rat_probability.values())
        for node in self.rat_probability:
            self.rat_probability[node] /= total_prob

        return False

    def addCellToKnowledgebaseAndReadjustProbability(self):
        """
        Only used when rat is moving. Resets zero-probability cells since rat could have moved anywhere.
        For stationary rats, cells are permanently ruled out (prob=0 never changes).
        """
        if not self.ship.is_rat_moving:
            return  # Never adjust probabilities for stationary rats

        # Rat is moving - reset ALL zero-probability cells
        MIN_PROB = 1e-5
        for cell in self.rat_probability:
            if self.rat_probability[cell] == 0:
                self.rat_probability[cell] = MIN_PROB

        # Renormalize
        total_prob = sum(self.rat_probability.values())
        if total_prob > 0:
            for cell in self.rat_probability:
                self.rat_probability[cell] /= total_prob
        else:
            # Emergency reset if all probabilities were 0
            for cell in self.rat_probability:
                self.rat_probability[cell] = 1.0 / len(self.rat_probability)

    def update_rat_probabilities(self, ping_received):
        """
        Updates rat probabilities using Bayes' rule:
        - If ping: Increase prob for nearby cells, decrease for far cells.
        - If no ping: Do the opposite.
        - Cells with prob=0 are NEVER updated (rat can't be there).
        """
        alpha = self.ship.alpha

        total_prob = 0.0
        for cell in self.rat_probability:
            isRatStationary = not self.ship.is_rat_moving
            if cell == self.position and isRatStationary:
                self.rat_probability[cell] = 0  # Rat can't be in current cell
                continue

            # Skip cells already marked as impossible (prob=0)
            if self.rat_probability[cell] == 0 and isRatStationary:
                continue

            d = HelperService.manhattan_distance(self.position, cell)
            likelihood = math.exp(-alpha * (d - 1)) if ping_received else 1 - math.exp(-alpha * (d - 1))
            self.rat_probability[cell] *= likelihood
            total_prob += self.rat_probability[cell]

        # Normalize probabilities (only non-zero cells)
        for cell in self.rat_probability:
            if self.rat_probability[cell] > 0:
                self.rat_probability[cell] /= total_prob

    def calculatePath(self, target_cell: tuple):
        ship = self.ship.Ship
        adj_list = list(ship.adjacency())
        comp_graph = compatibleGraph(ship, adj_list)

        # Validate target exists in the compatible graph
        if target_cell not in comp_graph:
            HelperService.printDebug(f"Target cell {target_cell} is not in the compatible graph!")
            return []

        # Run Dijkstra's
        try:
            queue = djikstras(comp_graph, startNode=self.position)
            path = getPathFromATOB(queue, self.position, target_cell)
            return path
        except nx.NetworkXNoPath:
            HelperService.printDebug(f"No path exists from {self.position} to {target_cell}!")
            return []
        except Exception as e:
            HelperService.printDebug(f"Error in path calculation: {str(e)}")
            return []
