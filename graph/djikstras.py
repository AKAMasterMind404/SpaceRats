import networkx as nx
import heapq


def compatibleGraph(ship: nx.Graph, graph: list) -> dict:
    adjacencyList = {}
    exclude_nodes = {node for node in ship.nodes if ship.nodes[node].get('weight', 1) == 1}

    for node, neighbors in graph:
        if node in exclude_nodes:
            continue

        adjacencyList[node] = []
        for neighbor, attr in neighbors.items():
            if neighbor not in exclude_nodes:
                adjacencyList[node].append({
                    'node': neighbor,
                    'dist': attr.get('weight', 1)
                })

    return adjacencyList

def _findDistanceFromNode1ToNode2(graph: dict, node1: tuple, node2: tuple):
    if node1 == node2:
        raise NameError(f'Node 1 and Node 2 have the same value {node1}!')

    node2Neighbours = graph[node2]
    dist = float('inf')
    for nb in node2Neighbours:
        if nb['node'] == node1:
            dist = nb['dist']
    return dist


def _findCurr(queue: dict, visited: set):
    least = float('inf')
    curr = None

    for node in queue.keys():
        prop = queue[node]
        if prop['shortest'] < least and node not in visited:
            curr = node
            least = prop['shortest']

    return curr


def _createPriorityQueue(graph: dict, startNode: tuple):
    queue = dict()
    for node in graph.keys():
        shortest = 0 if node == startNode else float('inf')
        queue[node] = {'shortest': shortest, 'prev': None}

    return queue


def getPathFromATOB(queue: dict, A: tuple, B: tuple):
    if B not in queue:
        raise nx.NetworkXNoPath(f"Target node {B} not in graph")

    if queue[B]['shortest'] == float('inf'):
        raise nx.NetworkXNoPath(f"No path exists from {A} to {B}")

    path = []
    curr = B

    while curr != A:
        path.append(curr)
        curr = queue[curr]['prev']
        if curr is None:  # Shouldn't happen if we checked for inf earlier
            raise nx.NetworkXNoPath(f"Path broken from {A} to {B}")

    return path[::-1]

def djikstras(graph: dict, startNode: tuple):
    if startNode not in graph:
        raise ValueError("Start node not in graph")

    visited = set()
    queue = _createPriorityQueue(graph, startNode)

    while len(visited) != len(graph):
        curr = _findCurr(queue, visited)
        if curr is None:  # No reachable nodes left
            break

        for neighbour in graph[curr]:
            neighbourNode = neighbour['node']
            if neighbourNode in visited:
                continue

            new_dist = queue[curr]['shortest'] + neighbour['dist']
            if new_dist < queue[neighbourNode]['shortest']:
                queue[neighbourNode]['shortest'] = new_dist
                queue[neighbourNode]['prev'] = curr

        visited.add(curr)

    return queue