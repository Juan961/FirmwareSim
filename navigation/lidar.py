import math
from typing import List, Tuple


# grid -> 120 x 120 each cell is 5cm
# lidar readings -> 360 degres, 0 to inf distance in meters
# - FORWARD 0 deg = range_image[180]
# - BACKWARD 180 deg = range_image[0]
# - LEFT 270 deg = range_image[90]
# - RIGHT 90 deg = range_image[270]
# current_pos: (x, y) in meters
# heading: int degrees (0 = north, 180 = south)


GRID_SIZE = 120
CELL_SIZE = 0.05 # 5cm per cell
WORLD_SIZE = 6 # 6m arena
DECAY_RATE = 0.05 # Decay old obstacle readings
ROBOT_WIDTH = 0.16
ROBOT_HEIGHT = 0.16


def world_to_grid(x: float, y: float) -> Tuple[int, int]:
    grid_x = int((x + WORLD_SIZE / 2) / CELL_SIZE)
    grid_y = int((y + WORLD_SIZE / 2) / CELL_SIZE)

    grid_x = max(0, min(GRID_SIZE - 1, grid_x))
    grid_y = max(0, min(GRID_SIZE - 1, grid_y))
    
    return grid_x, grid_y


def grid_to_world(grid_x: int, grid_y: int) -> Tuple[float, float]:
    x = (grid_x * CELL_SIZE) - (WORLD_SIZE / 2) + (CELL_SIZE / 2)
    y = (grid_y * CELL_SIZE) - (WORLD_SIZE / 2) + (CELL_SIZE / 2)

    return x, y


def bresenham_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return points


def update_grid_status(grid: List[List[int]], lidar_readings: List[float], current_pos: Tuple[float, float], heading: int) -> List[List[int]]:
    new_grid = [row[:] for row in grid]

    # CLEAN ROBOT POSITION
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if new_grid[r][c] == -1.0:
               new_grid[r][c] = 0.0

    robot_grid_x, robot_grid_y = world_to_grid(current_pos[0], current_pos[1])

    for lidar_index, distance in enumerate(lidar_readings):
        if distance >= 6.0 or distance < ROBOT_WIDTH:
            continue

        world_angle_deg = (270 - heading - lidar_index) % 360
        world_angle_rad = math.radians(world_angle_deg)

        obs_x = current_pos[0] + distance * math.cos(world_angle_rad)
        obs_y = current_pos[1] + distance * math.sin(world_angle_rad)

        grid_x, grid_y = world_to_grid(obs_x, obs_y)

        line_points = bresenham_line(robot_grid_x, robot_grid_y, grid_x, grid_y)

        # Mark free space along the entire ray
        for px, py in line_points:
            if 0 <= px < GRID_SIZE and 0 <= py < GRID_SIZE:
                new_grid[py][px] = 0.0

        buffer = 1  # Mark 1 cell in each direction
        for dx in range(-buffer, buffer + 1):
            for dy in range(-buffer, buffer + 1):
                nx, ny = grid_x + dx, grid_y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    new_grid[ny][nx] = 1

    # ROBOT POSITION
    robot_size_in_cells = int(max(ROBOT_WIDTH, ROBOT_HEIGHT) / CELL_SIZE / 2) + 1
    for dx in range(-robot_size_in_cells, robot_size_in_cells + 1):
        for dy in range(-robot_size_in_cells, robot_size_in_cells + 1):
            nx, ny = robot_grid_x + dx, robot_grid_y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                new_grid[ny][nx] = -1.0

    return new_grid
