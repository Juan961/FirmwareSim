import heapq


from typing import List, Optional, TypeVar, Tuple


T = TypeVar('T')


class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic"""
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star(grid: List[List[int]], start_coord: Tuple[int, int], end_coord: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Simple A* pathfinding on a grid.
    
    Args:
        grid: 2D list where 0 = walkable, >0 = obstacle
        start_coord: (x, y) starting position
        end_coord: (x, y) goal position
    
    Returns:
        List of (x, y) coordinates representing the path from start to end
    """
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    
    # Validate coordinates
    if not (0 <= start_coord[0] < width and 0 <= start_coord[1] < height):
        return []
    if not (0 <= end_coord[0] < width and 0 <= end_coord[1] < height):
        return []
    
    # 4-directional neighbors (cardinal directions)
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    frontier = PriorityQueue()
    frontier.put(start_coord, 0)
    came_from: dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start_coord: None}
    cost_so_far: dict[Tuple[int, int], float] = {start_coord: 0}
    
    while not frontier.empty():
        current = frontier.get()
        
        # Goal reached
        if current == end_coord:
            break
        
        x, y = current
        
        # Check all neighbors
        for dx, dy in neighbors:
            next_x, next_y = x + dx, y + dy
            next_pos = (next_x, next_y)
            
            # Check bounds
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue
            
            # Check if walkable (0 = walkable, >0 = obstacle)
            if grid[next_y][next_x] > 0:
                continue
            
            # Calculate cost (1 for each step)
            new_cost = cost_so_far[current] + 1
            
            # Only proceed if we found a better path
            if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                cost_so_far[next_pos] = new_cost
                priority = new_cost + heuristic(next_pos, end_coord)
                frontier.put(next_pos, priority)
                came_from[next_pos] = current
    
    # Reconstruct path
    if end_coord not in came_from:
        return []  # No path found
    
    path = []
    current = end_coord
    while current is not None:
        path.append(current)
        current = came_from[current]
    
    return path[::-1]  # Reverse to get start -> end
