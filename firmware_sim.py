import time
from math import atan2, sqrt


from controller import Robot


from navigation.a_star import a_star
from navigation.lidar import update_grid_status, world_to_grid, grid_to_world
from remote import mqtt_init_sub, telemetry_worker, telemetry_queue

from utils.angles import wrap_pi, rad_to_deg, deg_to_rad


robot = Robot()
timestep = int(robot.getBasicTimeStep())


left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
compass = robot.getDevice('compass')
gps = robot.getDevice('gps')
camera = robot.getDevice('camera')
lidar = robot.getDevice('LDS-01')


for m in [left_motor, right_motor]:
    m.setPosition(float('inf'))
    m.setVelocity(0.0)


compass.enable(timestep)
gps.enable(timestep)
camera.enable(timestep)
lidar.enable(timestep)
lidar.enablePointCloud()


global_target_pos = { "x": 0, "y": 0 }
next_target_pos = { "x": 0, "y": 0 }
telemetry_counter = 0


KP_STEER = 1
ANGLE_THRESHOLD = deg_to_rad(5)
DISTANCE_THRESHOLD = 0.2


grid = [[ 0 for _ in range(120) ] for _ in range(120)]


STATUS = "IDLE"


def save_grid_to_file(grid, filename="debug_grid.txt"):
    try:
        with open(filename, "w") as f:
            for row in grid:
                line = " ".join([f"{val:.1f}" if isinstance(val, float) else str(val) for val in row])
                f.write(line + "\n")
    except Exception as e:
        print(f"Error saving grid: {e}")


def save_path_to_file(path, filename="debug_path.txt"):
    try:
        with open(filename, "w") as f:
            for coord in path:
                line = f"{coord[0]} {coord[1]}"
                f.write(line + "\n")
    except Exception as e:
        print(f"Error saving path: {e}")


while robot.step(timestep) != -1:
    # ==================== GENERAL SENSORS ====================
    range_image = lidar.getRangeImage()

    direction = compass.getValues()
    heading = atan2(direction[1], direction[0])
    deg_north = rad_to_deg(heading)

    [x, y, _] = gps.getValues()
    bearing = atan2(global_target_pos["y"] - y, global_target_pos["x"] - x)
    deg_tar = rad_to_deg(bearing)

    global_error_angle = wrap_pi(bearing - heading)
    global_error_angle_deg = rad_to_deg(global_error_angle)

    target_dist = sqrt( (global_target_pos["y"] - y)**2 + (global_target_pos["x"] - x)**2)

    # ==================== NAVIGATION ====================
    grid_current_position = world_to_grid(x, y)
    grid_target_position = world_to_grid(global_target_pos["x"], global_target_pos["y"])

    grid = update_grid_status(grid, range_image, (x, y), deg_north)

    path = a_star(grid, grid_current_position, grid_target_position)

    if path and len(path) > 10:
        next_waypoint_grid = path[10]
        next_target_pos = grid_to_world(next_waypoint_grid[0], next_waypoint_grid[1])
    else:
        next_target_pos = (global_target_pos["x"], global_target_pos["y"])

    bearing = atan2(next_target_pos[0] - x, next_target_pos[1] - y)
    deg_tar_local = rad_to_deg(bearing)

    local_error_angle = wrap_pi(bearing - heading)
    local_error_angle_deg = rad_to_deg(local_error_angle)

    local_dist = sqrt((next_target_pos[1] - y)**2 + (next_target_pos[0] - x)**2)

    if target_dist < DISTANCE_THRESHOLD:
        if target_dist < 0.2 and local_dist < 0.2:
            STATUS = "AT TARGET"
            left_motor.setVelocity(0)
            right_motor.setVelocity(0)
        else:
            STATUS = "REACHED WAYPOINT"
    elif abs(local_error_angle) > ANGLE_THRESHOLD:
        base_speed = 1
        steer = max(min(local_error_angle * KP_STEER, 1), -1)
        left_motor.setVelocity(base_speed+steer)
        right_motor.setVelocity(base_speed-steer)
        STATUS = f"TURNING TO {'RIGHT' if steer > 0 else 'LEFT'}"
    else:
        STATUS = "MOVING FORWARD"
        left_motor.setVelocity(2.0)
        right_motor.setVelocity(2.0)

    telemetry_counter += 1

    if telemetry_counter % 20 == 0:
        # now = time.time()
        # image_path = f"/images/{now}.png"
        # camera.saveImage(image_path, 100)

        save_grid_to_file(grid)
        save_path_to_file(path if path else [], filename="debug_path.txt")

        print(f"Status: {STATUS}", end=' | ')
        # print(f"Heading: {deg_north:.2f} | Bearing: {deg_tar:.2f} | Error: {error_angle_deg:.2f} | Pos X: {pos[0]:.2f} | Pos Y: {pos[1]:.2f}")
        # print(f"FORWARD: {range_image[180]:.2f} | BACKWARD: {range_image[0]:.2f} | RIGHT: {range_image[180]:.2f} | LEFT: {range_image[270]:.2f} | Pos X: {pos[0]:.2f} | Pos Y: {pos[1]:.2f}")
        print(f"Pos: ({x:.2f}, {y:.2f}) | Local target: ({next_target_pos[0]:.2f}, {next_target_pos[1]:.2f}) | Heading {deg_north:.2f} | Global target angle: {deg_tar:.2f} | Local target angle: {deg_tar_local:.2f}")
        # print(f"Heading: {deg_north:.2f} | Pos: ({x:.2f}, {y:.2f}) | Target: ({next_target_pos[0]:.2f}, {next_target_pos[1]:.2f}) | Distance: {dist:.2f}m")
