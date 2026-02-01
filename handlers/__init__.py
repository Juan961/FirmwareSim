import time

from math import atan2, sqrt


from utils.angles import wrap_pi, deg_to_rad
from navigation.lidar import update_grid_status, world_to_grid, grid_to_world
from navigation.a_star import a_star
from remote import commands_queue


KP_STEER = 1
ANGLE_THRESHOLD = deg_to_rad(5)
DISTANCE_THRESHOLD = 0.2


class MissionControl:
    def __init__(self, left_motor=None, right_motor=None):
        self.coords = {
            "lat": 0.0,
            "lon": 0.0
        }

        self.lidar_readings = []

        self.heading = 0.0

        self.right_motor = right_motor
        self.right_motor_speed = 0.0

        self.left_motor = left_motor
        self.left_motor_speed = 0.0

    def set_motors(self, left_motor, right_motor):
        """Set motor references for thread-based control"""
        self.left_motor = left_motor
        self.right_motor = right_motor
    
    def set_motor_speeds(self, right_speed, left_speed):
        self.right_motor.setVelocity(right_speed)
        self.right_motor_speed = right_speed

        self.left_motor.setVelocity(left_speed)
        self.left_motor_speed = left_speed

    def new_data(self, data):
        self.coords["lat"] = data.get("lat", self.coords["lat"])
        self.coords["lon"] = data.get("lon", self.coords["lon"])
        self.heading = data.get("heading", self.heading)
        self.lidar_readings = data.get("lidar", self.lidar_readings)
    
    def get_motor_speeds(self):
        return self.right_motor_speed, self.left_motor_speed


mission_control = MissionControl()


def goto(message_id:str, payload):
    lat_target, lon_target = payload.get("lat"), payload.get("lon")

    at_target = False

    last_applied_time = time.time()

    left_motor = mission_control.left_motor
    right_motor = mission_control.right_motor

    grid = [[ 0 for _ in range(120) ] for _ in range(120)]

    while not at_target and (time.time() - last_applied_time) < 0.01:
        # Data from the device
        lat, lon = mission_control.coords["lat"], mission_control.coords["lon"]
        heading = mission_control.heading
        range_image = mission_control.lidar_readings

        # Compute target distance
        target_dist = sqrt( (lat_target - lat)**2 + (lon_target - lon)**2)

        grid_current_position = world_to_grid(lon, lat)
        grid_target_position = world_to_grid(lon_target, lat_target)

        grid = update_grid_status(grid, range_image, (lon, lat), deg_to_rad(heading))

        path = a_star(grid, grid_current_position, grid_target_position)

        if path and len(path) > 10:
            next_waypoint_grid = path[10]
            next_target_pos = grid_to_world(next_waypoint_grid[0], next_waypoint_grid[1])
        else:
            next_target_pos = (lon_target, lat_target)

        bearing = atan2(next_target_pos[0] - lon, next_target_pos[1] - lat)

        local_error_angle = wrap_pi(bearing - heading)

        local_dist = sqrt((next_target_pos[1] - lat)**2 + (next_target_pos[0] - lon)**2)

        if target_dist < DISTANCE_THRESHOLD:
            if target_dist < 0.2 and local_dist < 0.2:
                left_motor.setVelocity(0)
                right_motor.setVelocity(0)
                at_target = True

        elif abs(local_error_angle) > ANGLE_THRESHOLD:
            base_speed = 1
            steer = max(min(local_error_angle * KP_STEER, 1), -1)
            left_motor.setVelocity(base_speed+steer)
            right_motor.setVelocity(base_speed-steer)

        else:
            left_motor.setVelocity(2.0)
            right_motor.setVelocity(2.0)

        last_applied_time = time.time()

    print("FINISHED GOTO COMMAND")

    commands_queue.mark_command_completed(message_id)

