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
    brain.align_from(math.pi, unit, flip=-1)
    brain.align_from(1 * math.pi / 2, unit, flip=-1, axis='y')

class Brain:
    def __init__(self, render=False):
        self.mob = Mobility(None)
        while not status.button_state():
            pass
        self.lidar = RPi_Lidar(None, "/dev/ttyAMA0")
        self.lidar.set_motor_duty(90)
        self.io = status_io.IOHandler()
        self.render = render
        if render:
            self.io.start('144.167.149.164', 9998)
            self.io.send_data(('lidar-test', None))

    def move_until_proc(self, front_prox):
        scan = self.get_x_scans(5)
        front_scan_polar = scan[..., np.logical_or(23 * math.pi / 12 < scan[1], scan[1] <  math.pi / 12)]
        front_scan = pol2cart(front_scan_polar[0], front_scan_polar[1])
        front_dist = int(np.min(front_scan[0])) - front_prox
        moves = int(front_dist / unit)
        approach = front_dist % unit
        for move in range(moves):
            self.move((1, 0))
        scan = self.get_x_scans(5)
        front_scan_polar = scan[..., np.logical_or(23 * math.pi / 12 < scan[1], scan[1] < math.pi / 12)]
        front_scan = pol2cart(front_scan_polar[0], front_scan_polar[1])
        front_dist = np.min(front_scan[0]) - front_prox
        self.move((1, 0), front_dist, 2)

    def move(self, direction, dist=unit, sub_steps=1, align=True):
        x_component, y_component = direction
        sub_unit = dist / sub_steps
        for sub_line in range(sub_steps):
            action = self.mob.exec_line(Point3(sub_unit * y_component, sub_unit * x_component))
            action.set_status(status)
            action.start()
            while not action.complete:
                print(action.target[None], action.estimate_progress()[None])
            if align:
                self.align_center()
                self.align_angle()

    def rotate_180(self):
        self.align_center()
        action = self.mob.rotate(180)
        action.set_status(status)
        status.start()
        while not action.complete():
            pass
        self.align_angle()

    def get_x_scans(self, x):
        scanner = self.lidar.scanner(offset=270)
        scan_agg = next(scanner)
        for id, scan in zip(range(x-1), scanner):
            scan_agg = np.concatenate((scan, scan_agg), axis=1)
        return scan_agg[..., scan_agg[0] != 0]

    def align_center(self):
        print("scanning")
        scan = self.get_x_scans(2)
        if self.render:
            self.io.send_data(('lidar-test-points', scan))
        left_point = scan[0][get_closest_point(scan[1], 3 * math.pi / 2)]
        right_point = scan[0][get_closest_point(scan[1], math.pi / 2)]
        span = left_point + right_point
        action = self.mob.exec_line(Point3(span/2 - right_point))
        action.set_status(status)
        action.start()
        while not action.complete:
            print(action.target[None], action.estimate_progress()[None])

    def align_from(self, angle, postion_from, flip=1, axis='x'):
        scan = self.get_x_scans(3)
        angle_offset = self.get_angle(scan)
        pos_offset = flip * (self.align_span(scan, angle - angle_offset) - postion_from)
        action = self.mob.rotate(angle_offset)
        self.do_action(action)
        if axis == 'x':
            action = self.mob.exec_line(Point3(0, axis))
        if axis == 'y':
            action = self.mob.exec_line(Point3(pos_offset))
        self.do_action(action)

        # left_offset = self.align_span(scan, (3 * math.py / 2) + angle_offset)
        # rear_offset = self.align_span(scan , (math.pi) + angle_offset)


    def get_angle(self, scan):
        right_scan = scan[..., np.logical_and(5 * math.pi / 12 < scan[1], scan[1] < 7 * math.pi / 12)]
        slope, *tail = np.polyfit(*self.pol2cart(right_scan[0], right_scan[1]), 1)
        return -math.atan(slope)

    def do_action(self, action):
        action.set_status(status)
        action.start()
        while not action.complete:
            pass

    def align_span(self, scan, angle_offset):
        return scan[0][self.get_closest_point(scan[1], angle_offset)]


    def align_angle(self, scan):
        right_scan = scan[..., np.logical_and(5 * math.pi / 12 < scan[1], scan[1] < 7 * math.pi / 12)]
        slope, *tail = np.polyfit(*self.pol2cart(right_scan[0], right_scan[1]), 1)
        return -math.atan(slope)

    def align_angle(self, angle_offset=0):
        scan = self.get_x_scans(2)
        left_scan = scan[..., np.logical_and(17 * math.pi / 12 < scan[1], scan[1] < 19 * math.pi / 12)]
        right_scan = scan[..., np.logical_and(5 * math.pi / 12 < scan[1], scan[1] < 7 * math.pi / 12)]
        left_angle, *tail = np.polyfit(*pol2cart(left_scan[0], left_scan[1]), 1)
        right_angle, *tail = np.polyfit(*pol2cart(right_scan[0], right_scan[1]), 1)
        slope = statistics.mean([left_angle, right_angle])
        print("Angle divergence:", left_angle - right_angle)
        action = self.mob.rotate(math.atan(slope) + angle_offset)
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
