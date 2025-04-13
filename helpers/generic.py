import constants as cnt


class HelperService:

    @staticmethod
    def printDebug(arg: str):
        if cnt.K_DEBUG_MODE:
            print(arg)

    @staticmethod
    def directions(node: tuple) -> list:
        x, y = node
        return [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1),
                (x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)]

    @staticmethod
    def nonDiagDirections(node: tuple) -> list:
        x, y = node
        return [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]

    @staticmethod
    def getOpenNeighbourListForNode(graph, node: tuple, isIgnoreDiagonals: bool = False) -> list:
        directions = HelperService.nonDiagDirections(node) if isIgnoreDiagonals else HelperService.directions(node)

        openNeighbours = []
        grid_size = cnt.GRID_SIZE  # Assuming this exists

        for newX, newY in directions:
            # Check bounds first
            if 0 <= newX < grid_size and 0 <= newY < grid_size:
                nodeAtDxDy = graph.Ship.nodes.get((newX, newY), None)
                if nodeAtDxDy and nodeAtDxDy['weight'] == cnt.CELL_OPENED:
                    openNeighbours.append((newX, newY))

        return openNeighbours

    @staticmethod
    def getClosedNeighborCount(graph, node: tuple) -> int:
        """Counts actual blocked/closed neighbors (more reliable than 8 - open)"""
        directions = HelperService.directions(node)
        grid_size = cnt.GRID_SIZE
        closed_count = 0

        for newX, newY in directions:
            if 0 <= newX < grid_size and 0 <= newY < grid_size:
                node_data = graph.Ship.nodes.get((newX, newY), None)
                if not node_data or node_data['weight'] == cnt.CELL_CLOSED:
                    closed_count += 1
            else:
                # Count out-of-bounds as closed
                closed_count += 1

        return closed_count

    @staticmethod
    def pickACellWithHighestRatProbability(pd1: dict, pd2: dict):
        combinedDict = dict()
        for cell in pd1.keys():
            v1 = pd1[cell]
            v2 = pd2[cell]
            combinedDict[cell] = v1*v2
        cell = max(combinedDict.items(), key=lambda x: x[1])[0]
        return cell

    @staticmethod
    def manhattan_distance(cell1, cell2):
        dist = abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])
        return dist
