from graph.graph import getGraph
from graph.sample.sample1 import currently_open_1, dead_ends_1

# A function that runs a simulation without screen / ui elements
def auto_game(alpha, bot_type, is_rat_moving, isUseIpCells: bool = True, isUsePresetPos: bool = True):
    print(f"Autogame started alpha: {alpha}, rat moving: {is_rat_moving}, bot: {bot_type}")
    graph = getGraph(None, bot_type, alpha, is_rat_moving, isUseIpCells, isUsePresetPos)
    # Graph life cycle same as in UI GAME

    if isUseIpCells:
        graph.currently_open = currently_open_1
        graph.dead_ends_1 = dead_ends_1

    while not graph.game_over:
        graph.proceed()
    return graph
