import networkx as nx
import random
import constants as cnt
import helpers.draw_grid as dg
from gateways.robotgateway import RobotGateway
from graph.sample.sample1 import dead_ends_1, currently_open_1
from helpers.generic import HelperService
from robot.robot import Robot


class ManhattanGraph:
    def __init__(self, screen, n, alpha, bot_type, is_rat_moving, isUseIpCells: bool = False, isUsePresetPos: bool = False):
        self.n = n  # Dimension of rhe 2d graph
        self.alpha = alpha  # Detection sensitivity
        self.bot_type = bot_type  # bot type
        self.is_rat_moving: bool = is_rat_moving
        self.game_over = False  # Indicates whether game may or may not be proceeded
        self.Ship = nx.Graph()  # Graph nodes represented using networkx.Graph object
        self.path = None  # Path outlined by the bot
        self.canProceed = True  # Indicates whether simulation is already under progress
        self.screen = screen  # pygame.screen - May or may not be None
        self.current_step = "Ship Expansion"  # Display Label
        self.currently_open = set()  # Nodes that are 'open', # Zero indicates 'open' and One indicates 'close'
        self.dead_ends = []  # cells that have 3 closed cells around them
        self.step = 1  # Track algorithm step
        self.curr_bot_pos = None  # Current position of bot
        self.curr_rat_pos = None  # Current and final button position
        self.isUseIpCells = isUseIpCells  # A boolean flag indicating opened cells are already defined
        self.isUsePresetPos = isUsePresetPos  # A boolean flag indicating fire, bot and button positions are already defined
        self.bot_candidate_nodes = set()  # A set of nodes that are currently open and could be the bots position
        self.currBot: Robot = None
        self.t = 0  # Time step, calculates how many times proceed() ahs been called. Also, a measure for no of steps taken by bot

    def create_manhattan_graph(self):
        for i in range(self.n):
            for j in range(self.n):
                node = (i, j)
                self.Ship.add_node(node, weight=cnt.CELL_CLOSED)
                if i > 0:
                    self.Ship.add_edge(node, (i - 1, j), weight=cnt.CELL_CLOSED)
                if j > 0:
                    self.Ship.add_edge(node, (i, j - 1), weight=cnt.CELL_CLOSED)

    def proceed(self):
        if self.step == 1:
            # Initialization
            self.currently_open = currently_open_1
            self.dead_ends = dead_ends_1
            for i, j in self.dead_ends:
                self.Ship.nodes[(i, j)]['weight'] = cnt.CELL_CLOSED
            for i, j in self.currently_open:
                self.Ship.nodes[(i, j)]['weight'] = cnt.CELL_OPENED
            self.step = 2
            return
        elif self.step == 2:
            dg.draw_grid_internal(self)
            currBot = RobotGateway(self, None, botType=self.bot_type)
            currBot.bot_candidate_nodes = set(self.currently_open)  # All open cells are initial candidates
            self.currBot = currBot
            self.curr_bot_pos = random.choice(list(self.currBot.bot_candidate_nodes))
            self.step = 3
            return
        elif self.step == 3:
            # PHASE 1
            self.currBot.position = self.currBot.getBotPosition()
            self.t = 0
            self.step = 4
            self.placeSpaceRat()
            return
        elif self.step == 4:
            # PHASE 2
            self.curr_bot_pos = None
            if self.currBot.rat_probability[self.curr_rat_pos] == 0:
                raise ValueError("Rat probability zero error")

            if self.currBot.position == self.curr_rat_pos or self.t > cnt.MAX_MOVES_CAP:
            # Code halt condition if too many timesteps are received or if rat is found
                self.step = 5
                return

            if self.currBot.isMove:
                isReached = self.currBot.moveBot()
                # Checks if bot is found whilst reaching the final target
                if isReached:
                    self.step = 5
                    return
            else:
                # Updates ping knowledge base
                self.currBot.updatePingLikelihoodProbabilities()

            if self.is_rat_moving:
                neighbors = HelperService.getOpenNeighbourListForNode(self, self.curr_rat_pos, isIgnoreDiagonals=True)
                cell_to_go_rat = random.choice(neighbors)
                self.curr_rat_pos = cell_to_go_rat
                self.currBot.updateRatProbabilities()
            # Increase the timestep
            self.t += 1

        elif self.step == 5:
            self.game_over = True
            return self
        dg.draw_grid_internal(self)
        return

    def placeSpaceRat(self):
        rat_candidates = self.currently_open.copy()
        rat_candidates.remove(self.curr_bot_pos)
        self.curr_rat_pos = random.choice(list(rat_candidates))


def getGraph(screen, bot_type, alpha, is_rat_moving, isUseIpCells: bool = False, isUsePresetPos: bool = False):
    graph = ManhattanGraph(screen=screen, n =cnt.GRID_SIZE, alpha=alpha, bot_type=bot_type, is_rat_moving = is_rat_moving, isUseIpCells=isUseIpCells,
                           isUsePresetPos=isUsePresetPos)
    graph.create_manhattan_graph()

    return graph
