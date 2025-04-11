import math
import random
import time
from abc import abstractmethod
import networkx as nx
from helpers.draw_grid import draw_grid_internal
from graph.djikstras import compatibleGraph, djikstras, getPathFromATOB
from helpers.generic import HelperService
import constants as cnt


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
        self.bot_candidate_nodes = dict()

    # PHASE 2
    @abstractmethod
    def updatePingLikelyhoodProbabilities(self):
        pass

    # PHASE 2
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

    # PHASE 2
    def _getPingAndRedistributeProbabilities(self, ping_received):
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

    # PHASE 2
    def initialize_rat_probabilities(self):
        """Initialize uniform probabilities for all open cells (except bot's position)."""
        open_cells = self.ship.currently_open
        total_cells = len(open_cells)
        for cell in open_cells:
            self.rat_probability[cell] = 1.0 / total_cells
        return

    # PHASE 2
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

    # PHASE 2
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

    # PHASE 2
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

    # PHASE 2
    def _getPingFromCurrCell(self):
        ship = self.ship

        # Calculate ping probability
        d = HelperService.manhattan_distance(self.position, self.ship.curr_rat_pos)
        ping_prob = math.exp(-ship.alpha * (d - 1))

        # Simulate ping (random number <= ping_prob)
        ping_received = random.random() <= ping_prob
        return ping_received

    # PHASE 1
    def getBotPosition(self):
        while len(self.bot_candidate_nodes) > 1:
            if self.ship.t % 2 == 0:
                # Elimination phase
                self.eliminate_candidates_on_blocked_neighbours()
            else:
                # Movement phase - move to any open neighbor
                open_neighbors = HelperService.getOpenNeighbourListForNode(
                    self.ship, self.ship.curr_bot_pos, isIgnoreDiagonals=True)

                if not open_neighbors:
                    raise ValueError("Bot is trapped!")
                self.ship.curr_bot_pos = random.choice(open_neighbors)
            draw_grid_internal(self.ship)
            time.sleep(cnt.TIME_RATE)
            self.ship.t += 1

        time.sleep(cnt.TIME_RATE)
        return list(self.bot_candidate_nodes)[0]

    # PHASE 1
    def eliminate_candidates_on_blocked_neighbours(self):
        if not self.bot_candidate_nodes:
            return

        # Get blocked count for current position
        current_blocked = 8 - len(HelperService.getOpenNeighbourListForNode(
            self.ship, self.ship.curr_bot_pos))

        new_candidates = set()
        for node in self.bot_candidate_nodes:
            node_blocked = 8 - len(HelperService.getOpenNeighbourListForNode(
                self.ship, node))
            if node_blocked == current_blocked:
                new_candidates.add(node)

        # Always include current position if it would have been eliminated
        if self.ship.curr_bot_pos not in new_candidates:
            new_candidates.add(self.ship.curr_bot_pos)
        self.bot_candidate_nodes = new_candidates