import pygame
import constants as cnt
import time
import graph.graph as g
from helpers.draw_grid import draw_grid


def ui_game(alpha: float, bot_type, is_rat_moving, isUseIpCells: bool = False, isUsePresetPos: bool = False):
    pygame.init()

    screen_width, screen_height = 800, 800  # Default size
    cnt.CELL_SIZE, cnt.SCREEN_SIZE = cnt.update_grid_constants(cnt.GRID_SIZE, screen_width, screen_height)

    screen = pygame.display.set_mode(cnt.SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption("The Bot is on Fire!")

    graph = g.getGraph(screen, bot_type, alpha, is_rat_moving, isUseIpCells, isUsePresetPos)
    running = True

    # Graph lifecycle -
    # 1. create_manhattan_graph
    # 2. initialize_ship_opening
    # 3. Open up the Ship
    # 4. Open up dead ends if any
    # 5. Randomly Spawn Bot, Button and Fire
    # 6. Run the simulation, check for game stopping conditions
    # 7. Return the time taken, q, bot info and whether fire was extinguished or not

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                cnt.CELL_SIZE, cnt.SCREEN_SIZE = cnt.update_grid_constants(cnt.GRID_SIZE, screen_width, screen_height)
                screen = pygame.display.set_mode(cnt.SCREEN_SIZE, pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if cnt.SCREEN_SIZE[0] // 2 - 50 <= x <= cnt.SCREEN_SIZE[0] // 2 + 50 and cnt.SCREEN_SIZE[1] - 40 <= y <= \
                        cnt.SCREEN_SIZE[1] - 10:
                    if graph.game_over:
                        graph = g.getGraph(screen, bot_type, alpha, is_rat_moving, isUseIpCells, isUsePresetPos)
                    else:
                    # while not graph.game_over:
                        draw_grid(screen, graph, graph.n)
                        graph.proceed()
                        time.sleep(cnt.TIME_RATE)
        draw_grid(screen, graph, cnt.GRID_SIZE)

    pygame.quit()
