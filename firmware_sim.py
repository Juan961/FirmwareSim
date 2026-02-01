import time
import json
from math import atan2
from threading import Thread


from controller import Robot


import handlers
from handlers import mission_control
from remote import mqtt_init_sub, telemetry_worker, commands_queue


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


mission_control.set_motors(left_motor, right_motor)


telemetry_counter = 0


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


current_command = None
current_command_status_file = "./remote/command_status.json"
current_command_status = None


threads = []


# thread_telemetry = Thread(target=telemetry_worker, args=())
# thread_telemetry.start()
# threads.append(thread_telemetry)

mqtt_init_sub()


while robot.step(timestep) != -1:
    # ==================== GENERAL SENSORS READING ====================
    range_image = lidar.getRangeImage()

    direction = compass.getValues()
    heading = atan2(direction[1], direction[0])
    [lon, lat, _] = gps.getValues()

    data = {
        "lat": lat,
        "lon": lon,
        "heading": heading,
        "lidar": range_image
    }

    mission_control.new_data(data)

    # ==================== MAIN COMMAND QUEUE HANDLER ====================
    if current_command is None and commands_queue.is_empty() == False:
        current_command = commands_queue.get_next_command()

    elif commands_queue.priorized_command_available(current_command):
        commands_queue.add_command(current_command)
        current_command = commands_queue.get_next_command()

    with open(current_command_status_file, "r") as f:
        data = json.load(f)

        if data.get("status"):
            current_command_status = data["status"]

    if current_command_status == "COMPLETED":
        print("===== Command completed =====")
        if current_command is not None:
            commands_queue.mark_command_completed(current_command["message_id"])
        current_command = None
        current_command_status = None
        # Clear the status file
        try:
            with open(current_command_status_file, "w") as f:
                json.dump({}, f)
        except Exception as e:
            print(f"Error clearing command status: {e}")

    elif current_command_status == "FAILED":
        print("===== Command failed =====")
        if current_command is not None:
            commands_queue.mark_command_failed(current_command["message_id"])
        current_command = None
        current_command_status = None
        # Clear the status file
        try:
            with open(current_command_status_file, "w") as f:
                json.dump({}, f)
        except Exception as e:
            print(f"Error clearing command status: {e}")

    elif current_command_status == "QUEUED":
        print("===== Starting command =====")
        func = getattr(handlers, current_command["command"].lower())
        thread = Thread(target=func, args=(current_command["message_id"], current_command["payload"],))
        thread.start()
        threads.append(thread)

        current_command_status = "IN_PROGRESS"

        commands_queue.mark_command_in_progress(current_command["message_id"])

    elif current_command_status == "IN_PROGRESS":
        pass

    telemetry_counter += 1

    if telemetry_counter % 20 == 0:
        pass
        # now = time.time()
        # image_path = f"/images/{now}.png"
        # camera.saveImage(image_path, 100)

        # save_grid_to_file(grid)
        # save_path_to_file(path if path else [], filename="debug_path.txt")

        # print(f"Status: {STATUS}", end=' | ')
        # print(f"Heading: {deg_north:.2f} | Bearing: {deg_tar:.2f} | Error: {error_angle_deg:.2f} | Pos X: {pos[0]:.2f} | Pos Y: {pos[1]:.2f}")
        # print(f"FORWARD: {range_image[180]:.2f} | BACKWARD: {range_image[0]:.2f} | RIGHT: {range_image[180]:.2f} | LEFT: {range_image[270]:.2f} | Pos X: {pos[0]:.2f} | Pos Y: {pos[1]:.2f}")
        # print(f"Pos: ({x:.2f}, {y:.2f}) | Local target: ({next_target_pos[0]:.2f}, {next_target_pos[1]:.2f}) | Heading {deg_north:.2f} | Global target angle: {deg_tar:.2f} | Local target angle: {deg_tar_local:.2f}")
        # print(f"Heading: {deg_north:.2f} | Pos: ({x:.2f}, {y:.2f}) | Target: ({next_target_pos[0]:.2f}, {next_target_pos[1]:.2f}) | Distance: {dist:.2f}m")

    time.sleep(0.1)
