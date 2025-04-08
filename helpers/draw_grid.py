import pygame
import constants as cnt


def draw_grid(screen, game, n):
    if not screen: return
    screen.fill(cnt.WHITE)
    font = pygame.font.SysFont(None, 30)
    text = font.render(game.current_step, True, cnt.BLACK)
    screen.blit(text, (20, 10))

    for i in range(n):
        for j in range(n):
            x = j * (cnt.CELL_SIZE + cnt.MARGIN)
            y = i * (cnt.CELL_SIZE + cnt.MARGIN) + cnt.HEADER_HEIGHT
            node = (i, j)

            # Start with white for open cells, black for closed
            if game.Ship.nodes[node]['weight'] == cnt.CELL_OPENED:
                color = cnt.WHITE
            else:
                color = cnt.BLACK

            # Apply heatmap coloring if in knowledge base and cell is open
            if game.step == 4:
                rat_knowledge_base = game.currBot.rat_probability
                # Find max probability for normalization
                max_prob = max(rat_knowledge_base.values()) if rat_knowledge_base else 1
                if node in rat_knowledge_base and game.Ship.nodes[node]['weight'] == cnt.CELL_OPENED:
                    prob = rat_knowledge_base[node] / max_prob  # Normalize to 0-1
                    color = getColor(prob)

            # Special positions override everything
            if game.currBot:
                if game.currBot.path and node in game.currBot.path:
                    color = cnt.PURPLE
            if node == game.curr_rat_pos:
                color = cnt.BROWN
            elif node in game.bot_candidate_nodes:
                color = cnt.YELLOW
            if game.currBot and node == game.currBot.position:
                color = cnt.BLUE
            elif node == game.curr_bot_pos:
                color = cnt.BLUE

            try:
                pygame.draw.rect(screen, color, (x, y, cnt.CELL_SIZE, cnt.CELL_SIZE))
                pygame.draw.rect(screen, cnt.GRAY, (x, y, cnt.CELL_SIZE, cnt.CELL_SIZE), 1)
            except ValueError:
                print(color)
                raise ValueError

    # Rest of your code remains the same...
    pygame.draw.rect(screen, cnt.BLUE, (cnt.SCREEN_SIZE[0] // 2 - 50, cnt.SCREEN_SIZE[1] - 40, 100, 30))
    message = "Proceed" if game.canProceed else "Loading ..."
    if game.game_over: message = "Restart"
    text = font.render(message, True, cnt.WHITE)
    screen.blit(text, (cnt.SCREEN_SIZE[0] // 2 - 30, cnt.SCREEN_SIZE[1] - 35))

    pygame.display.flip()


def draw_grid_internal(graph):
    draw_grid(graph.screen, graph, graph.n)


def getColor(prob):
    # Smooth gradient from green (0.0) to red (1.0)
    if prob < 0.5:
        # Green to yellow transition (0.0-0.5)
        red = int(255 * (prob * 2))  # 0 → 255
        green = 255  # 255 → 255
    else:
        # Yellow to red transition (0.5-1.0)
        red = 255  # 255 → 255
        green = int(255 * ((1 - prob) * 2))  # 255 → 0

    color = (red, green, 0)
    # Optional: Add minimum brightness for visibility
    if sum(color) < 150:  # If too dark
        color = (min(255, red + 50), min(255, green + 50), 0)

    return color
