import math
import sys
import time
import statistics
import numpy as np

import status_io
from hardware import RPi_Lidar
from utils import Point3
from mobility_platform import Mobility
from multiprocessing import Lock
from status_platform import status
status.lock = Lock()

unit = 304.8
def main(render, debug):
    print("starting brain")
    brain = Brain(render)
    if debug:
        for scan in brain.lidar.scanner():
            brain.io.send_data(('lidar-test-points', scan))
    for i in range(3):
        brain.move((1, 0))

class Brain:
    def __init__(self, render=False):
        self.mob = Mobility(None)
        self.lidar = RPi_Lidar(None, "/dev/ttyAMA0")
        self.lidar.set_motor_duty(90)
        self.io = status_io.IOHandler()
        self.render = render
        if render:
            self.io.start('144.167.148.247', 9998)
            self.io.send_data(('lidar-test', None))

    def move(self, direction, sub_steps=1):
        x_component, y_component = direction
        sub_unit = unit / sub_steps
        for sub_line in range(sub_steps):
            action = self.mob.exec_line(Point3(sub_unit * y_component, sub_unit * x_component))
            action.set_status(status)
            action.start()
            while not action.complete:
                print(action.target[None], action.estimate_progress()[None])
            self.align_center()
            self.align_angle()

    def align_center(self):
        print("scanning")
        scanner = self.lidar.scanner()
        scan_agg = next(scanner)
        #self.io.send_data(('lidar-test-points', np.array([[120], [math.pi / 2], [1]])))
        #return
        for id, scan in zip(range(1), scanner):
            self.io.send_data(('lidar-test-points', scan))
            scan_agg = np.concatenate((scan, scan_agg), axis=1)
        scan_agg = scan_agg[..., scan_agg[0] != 0]
        if self.render:
            self.io.send_data(('lidar-test-points', scan_agg))
        left_point = scan_agg[0][get_closest_point(scan_agg[1], 3 * math.pi / 2)]
        right_point = scan_agg[0][get_closest_point(scan_agg[1], math.pi / 2)]
        span = left_point + right_point
        action = self.mob.exec_line(Point3(span/2 - right_point))
        action.set_status(status)
        action.start()
        while not action.complete:
            print(action.target[None], action.estimate_progress()[None])

    def align_angle(self):
        scanner = self.lidar.scanner()
        scan_agg = next(scanner)
        for id, scan in zip(range(1), scanner):
            scan_agg = np.concatenate((scan, scan_agg), axis=1)
        scan_agg = scan_agg[..., scan_agg[0] != 0]
        left_scan = scan_agg[..., np.logical_and(17 * math.pi / 12 < scan_agg[1], scan_agg[1] < 19 * math.pi / 12)]
        right_scan = scan_agg[..., np.logical_and(5 * math.pi / 12 < scan_agg[1], scan_agg[1] < 7 * math.pi / 12)]
        left_angle, *tail = np.polyfit(*pol2cart(left_scan[0], left_scan[1]), 1)
        right_angle, *tail = np.polyfit(*pol2cart(right_scan[0], right_scan[1]), 1)
        slope = statistics.mean([left_angle, right_angle])
        print("Angle divergence:", left_angle - right_angle)
        action = self.mob.rotate(math.atan(slope))
        action.set_status(status)
        action.start()
        while not action.complete:
            print(action.target, action.estimate_progress())


def get_closest_point(array, value):
    return np.argmin(np.abs(array - value))


def pol2cart(rho, phi) -> (np.array, np.array):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y

if __name__ == "__main__":
    main("render" in sys.argv, "debug" in sys.argv)
