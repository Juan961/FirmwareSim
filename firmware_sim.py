from math import atan2, pi, sqrt


from controller import Robot


from telemetry import mqtt_init_sub, telemetry_worker, telemetry_queue


robot = Robot()
timestep = int(robot.getBasicTimeStep())


left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
compass = robot.getDevice('compass')
gps = robot.getDevice('gps')
lidar = robot.getDevice('LDS-01')
lidar.enable(timestep)
lidar.enablePointCloud()


for m in [left_motor, right_motor]:
    m.setPosition(float('inf'))
    m.setVelocity(0.0)

compass.enable(timestep)
gps.enable(timestep)

target_pos = { "x": 0, "y": 0 }
telemetry_counter = 0

# 0 NOTHING, 1 IS OCCUPIED
grid = [ [0 for _ in range(240)] for _ in range(240) ]

KP_STEER = 1
ANGLE_THRESHOLD = 0.0349066 # 2 deg


def wrap_pi(a):
    while a > pi: a -= 2*pi
    while a <= -pi: a += 2*pi
    return a


def rad_to_deg(rad:float):
    deg = (rad / pi) * 180.0
    
    if deg < 0:
        deg += 360
    
    return deg


while robot.step(timestep) != -1:
    range_image = lidar.getRangeImage()

    direction = compass.getValues()
    heading = atan2(direction[0], direction[1])
    deg_north = rad_to_deg(heading)

    pos = gps.getValues()
    bearing = atan2(target_pos["y"] - pos[1], target_pos["x"] - pos[0])
    deg_tar = rad_to_deg(bearing)

    error_angle = wrap_pi(bearing - heading)
    error_angle_deg = rad_to_deg(error_angle)

    dist = sqrt( (target_pos["y"] - pos[1])**2 + (target_pos["x"] - pos[0])**2)

    """ if dist < 0.2:
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
    elif abs(error_angle) > ANGLE_THRESHOLD:
        steer = max(min(error_angle * KP_STEER, 1.5), -1.5)
        left_motor.setVelocity(-steer)
        right_motor.setVelocity(steer)
    else:
        left_motor.setVelocity(2.0)
        right_motor.setVelocity(2.0)
    """

    telemetry_counter += 1

    # FORWARD = range_image[180]
    # BACKWARD = range_image[0]
    # LEFT = range_image[90]
    # RIGHT = range_image[270]

    if telemetry_counter % 20 == 0:
        # print(f"Heading: {deg_north:.2f} | Bearing: {deg_tar:.2f} | Error: {error_angle_deg:.2f} | Pos X: {pos[0]:.2f} | Pos Y: {pos[1]:.2f}")
        print(f"Start: {range_image[0]:.2f} | 90: {range_image[90]:.2f} | 180: {range_image[180]:.2f} | 270: {range_image[270]:.2f} | 360: {range_image[359]:.2f}")
        # print(f"North: {deg_north:.2f} | Target: {deg_tar:.2f} | Error: {error_angle:.2f} | Distance: {dist:.2f}")
        # print(f"Pos X: {pos[0]:.2f} | Pos Y: {pos[1]:.2f} | Pos Z: {pos[2]:.2f}")
