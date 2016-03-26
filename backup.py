import math
import statistics
import numpy as np
from scipy.stats import linregress

from hardware import RPi_Lidar
from utils import Point3
from mobility_platform import Mobility
from multiprocessing import Lock
from status_platform import status
status.lock = Lock()

unit = 304.8
def main():
    brain = Brain()
    brain.move(1, 0)

class Brain:
    def __init__(self):
        self.mob = Mobility(None)
        self.lidar = RPi_Lidar(None)

    def move(self, direction, sub_steps=10):
        x_component, y_component = direction
        sub_unit = unit / sub_steps
        for sub_line in range(sub_steps):
            action = self.mob.exec_line(Point3(sub_unit * y_component, sub_unit * x_component))
            action.set_status(status)
            action.start()
            while not action.complete():
                pass
            self.align_center()

    def align_center(self):
        scan = yield from self.lidar.get_scan()
        left_point = scan[0][get_closest_point(scan[1], 3 * math.pi / 2)]
        right_point = scan[0][get_closest_point(scan[1], math.pi / 2)]
        action = self.mob.exec_line(Point3(left_point - right_point))
        action.set_status(status)
        action.start()
        while not action.complete():
            pass
        scan = yield from self.lidar.get_scan()
        left_scan = scan[..., (3 * math.pi / 4) < scan[1] < (5 * math.pi / 4)]
        right_scan = scan[..., (math.pi / 4) < scan[1] < (7 * math.pi / 4)]
        left_angle, *tail = linregress(*pol2cart(left_scan[0], left_scan[1]))
        right_angle, *tail = linregress(*pol2cart(right_scan[0], left_scan[1]))
        slope = statistics.mean([left_angle, right_angle])
        action = self.mob.rotate(math.atan(slope))
        action.set_status(status)
        action.start()
        while not action.complete():
            pass


def get_closest_point(array, value):
    return np.argmin(np.abs(array - value))

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

if __name__ == "__main__":
    main()