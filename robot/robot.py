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
        self.rat_probability = self.getInitialProbabilities()
        self.ping_probability = self.getInitialProbabilities()
        self.bot_candidate_nodes = dict()

    # PHASE 2
    @abstractmethod
    def updatePingLikelihoodProbabilities(self):
        pass

    # PHASE 2
    def moveBot(self):
        if self.path is None:
            target_cell = HelperService.pickACellWithHighestRatProbability(
                self.rat_probability,
                self.ping_probability
            )
            self.targetCell = target_cell
            self.path = self.calculatePath(target_cell)
            draw_grid_internal(self.ship)

        if len(self.path) > 0:
            self.position = self.path.pop(0)

            if not self.ship.is_rat_moving and self.position != self.ship.curr_rat_pos:
                # Setting cells along the path as non probable while moving in case of stationary rat
                self.ping_probability[self.position] = 0
                self.rat_probability[self.position] = 0

            isBotFound = self.position == self.ship.curr_rat_pos
            if isBotFound:
                return isBotFound
        else:
            self.isMove = False
            self.path = None

        draw_grid_internal(self.ship)
        return False

    # PHASE 2
    def updateRatProbabilities(self):
        new_prob = {cell: 0.0 for cell in self.ship.currently_open}

        if self.ship.is_rat_moving:
            noise_level = 0.01  # 1% uniform noise
            uniform_prob = noise_level / len(self.ship.currently_open)
            for cell in new_prob:
                new_prob[cell] = uniform_prob

        for cell in self.ship.currently_open:
            # Only zero out if stationary rat and not current rat position
            if cell == self.position and not self.ship.is_rat_moving and cell != self.ship.curr_rat_pos:
                new_prob[cell] = 0
                continue

            neighbors = HelperService.getOpenNeighbourListForNode(self.ship, cell)
            if not neighbors:
                continue

            transition_prob = 1.0 / len(neighbors)
            for neighbor in neighbors:
                new_prob[cell] += self.rat_probability[neighbor] * transition_prob

        # Constant minimum probability (very small)
        min_prob = 1e-10 if self.ship.is_rat_moving else 0

        # Normalize
        total = sum(new_prob.values())
        if total > 0:
            for cell in new_prob:
                self.rat_probability[cell] = max(new_prob[cell] / total, min_prob)

    # PHASE 2
    def getPingAndUpdatePingLikelyhood(self):
        ping_received = self.getPingFromCurrCell()
        bot_pos = self.position

        # We replace a cell with min_prob if it was previously bots location
        # This is done so that the cell could be considered as an option after bot leaves it
        min_prob = 1e-10 if self.ship.is_rat_moving else 0
        max_prob = 1 - min_prob

        total_prob = 0
        probList = []

        for cell in self.ship.currently_open:
            d = HelperService.manhattan_distance(bot_pos, cell)
            sensor_model = math.exp(-self.ship.alpha * (d - 1))

            if not self.ship.is_rat_moving and self.ping_probability[cell] == 0:
                probList.append(0)
                continue

            new_prob = self.ping_probability[cell] * (sensor_model if ping_received else (1 - sensor_model))
            new_prob = max(min(new_prob, max_prob), min_prob)
            probList.append(new_prob)
            total_prob += new_prob

        # Normalize
        if total_prob > 0:
            for i, cell in enumerate(self.ship.currently_open):
                self.ping_probability[cell] = probList[i] / total_prob

    # PHASE 2
    def getInitialProbabilities(self):
        """Initialize uniform probabilities for all open cells (except bot's position)."""
        open_cells = self.ship.currently_open
        total_cells = len(open_cells)
        newDict = dict()
        for cell in open_cells:
            newDict[cell] = 1.0 / total_cells
        return newDict

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
    def getPingFromCurrCell(self):
        # Calculate ping probability
        d = HelperService.manhattan_distance(self.position, self.ship.curr_rat_pos)
        ping_prob = math.exp(-self.ship.alpha * (d - 1))

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
