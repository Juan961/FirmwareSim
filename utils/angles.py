from math import pi


def wrap_pi(a):
    while a > pi: a -= 2*pi
    while a <= -pi: a += 2*pi
    return a


def rad_to_deg(rad:float):
    deg = (rad / pi) * 180.0

    if deg < 0:
        deg += 360

    return deg

def deg_to_rad(deg:float):
    rad = (deg / 180.0) * pi

    return rad
