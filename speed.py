import math
import sys
import time
import statistics
import numpy as np

import status_io
from hardware import RPi_Lidar
from hardware.APDS9960 import APDS9960
from utils import Point3
from mobility_platform import Mobility
from multiprocessing import Lock
from status_platform import status

status.lock = Lock()

unit = 304.8


GENERIC_VICTIM_REGION = ((-500, 500), (-500, 500))

def main(render, debug):
    print("starting brain")
    brain = Brain(render)
    if debug:
        for scan in brain.lidar.scanner():
            # brain.io.send_data(('lidar-test-points', pol2cart(scan[0], scan[1])))
            # import pdb; pdb.set_trace()
            brain.io.send_data(('lidar-test-points', scan))

    f = Field(brain)
    if render:
        brain.io.send_data(("lidar-box", GENERIC_VICTIM_REGION))
        brain.io.send_data(('lidar-test-points', brain.get_x_scans(2)))
    time.sleep(4)
    brain.align_angle(brain.get_x_scans(1), ref=(1, 0))
    brain.do_action(brain.mob.exec_line(Point3(0, 1000)))
    brain.align_angle(brain.get_x_scans(1), ref=(1, 0))
    brain.do_action(brain.mob.exec_line(Point3(1000, 0)))
    brain.align_angle(brain.get_x_scans(1), ref=(1, 0))
    brain.do_action(brain.mob.exec_line(Point3(0, -1000)))
    brain.align_angle(brain.get_x_scans(1), ref=(1, 0))
    brain.do_action(brain.mob.exec_line(Point3(-1000, 0)))
    brain.align_angle(brain.get_x_scans(1), ref=(1, 0))


class Field:
    def __init__(self, brain):
        self.brain = brain

    def start(self):
        self.brain.align_from(math.pi, 1.5 * unit, ref=(0, 1))

    def channel_0(self):
        self.brain.move((1, 0), ref=(1, 1), dist=unit * 4, sub_steps=2)
        self.brain.move((1, 0), ref=(1, 0), dist=unit)

    def entry(self):
        self.brain.align_from(3 * math.pi / 2, 1.75 * unit, flip=1, axis='y', ref=(0, 1))
        self.brain.align_from(1 * math.pi / 2, 0.5 * unit, flip=-1, axis='y', ref=(0, 1))
        self.brain.move((1, 0), ref=(1, 1))

    def channel_1_start(self):
        self.brain.move((1, 0), dist=4 * unit, sub_steps=4, ref=(0, 1))
        self.brain.move_until_proximity(ref=(0, 1), front_proximity=unit * 0.45)

    def channel_2_start(self):
        self.brain.move((1, 0), ref=(0, 1), dist=unit)
        self.brain.align_from(3 * math.pi / 2, 1.6 * unit, flip=1, axis='y', ref=(0, 1))
        self.brain.do_action(self.brain.mob.rotate(math.pi))
        self.brain.do_action(self.brain.align_angle(scan=self.brain.get_x_scans(5), ref=(1, 0)))
        self.brain.move((1, 0), ref=(1, 1), dist=unit * 2.2, sub_steps=2)

    def acquire_1(self):
        self.brain.align(ref=(1, 1), scans=20)
        status.prepare_pickup()

        self.brain.move_until_proximity(ref=(1, 1))
        status.pickup()

    def acquire_2(self):
        # import pdb; pdb.set_trace()
        status.prepare_pickup()

        self.brain.move_until_proximity(ref=(1, 1))
        status.pickup()

    def return_1_backwards(self):
        # import pdb;pdb.set_trace()
        self.brain.move((-1, 0), ref=(0, 1), dist=unit * .5, sub_steps=2)
        self.brain.move((-1, 0), ref=(1, 1), dist=unit * 2, sub_steps=2)
        self.brain.move((-1, 0), ref=(0, 1), dist=unit, sub_steps=1)
        self.brain.move((-1, 0), ref=(1, 1), dist=unit, sub_steps=1)
        self.brain.move((-1, 0), ref=(1, 0), dist=unit * 1.15)

    def score(self, ref=(0, 1)):
        self.brain.align(ref=ref, scans=15)
        self.brain.align_from(0, unit, axis='x', ref=ref, flip=-1)
        status.let_down()

    def return_2_backwards(self):
        self.brain.align_from(0, 1.5 * unit, axis='x', ref=(1, 1), flip=-1)
        self.brain.move((-1, 0), dist=2.07 * unit, ref=(1, 0))
        self.brain.align_from(math.pi / 2, 0.5 * unit, axis='y', ref=(1, 0))
        self.brain.move((1, 0), ref=(1, 1))
        self.brain.move((1, 0), dist=unit * 1.1, ref=(0, 1))

    def outfield(self):
        if self.brain.victim_in_region(*VICTIM_3_1_POSITION):
            self.acquire_3_1()

    def acquire_3_1(self):
        self.brain.do_action(self.brain.mob.rotate(-math.pi / 2))
        self.brain.move((1, 0), dist=unit * 2.5, ref=(1, 0), sub_steps=4)
        self.brain.align_to_victim()


class Brain:
    def __init__(self, render=False):
        self.mob = Mobility(None)
        while not status.button_state():
            pass
        self.lidar = RPi_Lidar(None, "/dev/ttyAMA0")
        self.lidar.set_motor_duty(90)
        self.adps = APDS9960()
        self.adps.initialize()
        self.adps.enablePower()
        self.adps.enable_light_sensor()
        self.io = status_io.IOHandler()
        self.render = render
        if render:
            self.io.start('144.167.151.226', 9998)
            # self.io.send_data(('config', 'lidar-test lidar-cart no-lidar-lines'))
            self.io.send_data(('config', 'lidar-test no-lidar-lines'))

    def get_red_or_yellow(self):
        self.adps.enable_light_sensor()
        red = self.adps.readRedLight()
        green = self.adps.readGreenLight()
        # import pdb; pdb.set_trace()
        if green > 0.75 * red:
            return 'yellow'
        else:
            return 'red'

    def move_until_proximity(self, front_proximity=95, ref=(1, 1)):
        for attempt in range(1):
            scan = self.get_x_scans(10)
            front_scan_polar = scan[..., np.logical_or(23 * math.pi / 12 < scan[1], scan[1] < math.pi / 12)]
            front_scan = pol2cart(front_scan_polar[0], front_scan_polar[1])
            front_dist = int(np.min(front_scan[0])) - front_proximity
            # import pdb; pdb.set_trace()
            front_shift = self.align_center(scan, offset=self.get_angle(scan, ref), ref=ref).target.y
            # print(front_shift, front_dist)
            self.do_action(self.mob.exec_line(Point3(front_shift, front_dist)))

    def move(self, direction, dist=unit, sub_steps=1, align=True, ref=(1, 1)):
        x_component, y_component = direction
        sub_unit = dist / sub_steps
        for sub_line in range(sub_steps):
            action = self.mob.exec_line(Point3(sub_unit * y_component, sub_unit * x_component))
            action.set_status(status)
            action.start()
            while not action.complete:
                print(action.target[None], action.estimate_progress()[None])
            if align:
                self.align(ref)

    def align(self, ref, scans=7):
        scan = self.get_x_scans(scans)
        angle = self.align_angle(scan, ref=ref)
        line = self.align_center(scan, offset=angle.target, ref=ref)
        self.do_action(angle)
        self.do_action(line)

    def rotate_180(self):
        self.align_center()
        action = self.mob.rotate(180)
        action.set_status(status)
        status.start()
        while not action.complete():
            pass
        self.align_angle()

    def get_x_scans(self, x):
        scanner = self.lidar.scanner()
        scan_agg = next(scanner)
        for id, scan in zip(range(x - 1), scanner):
            scan_agg = np.concatenate((scan, scan_agg), axis=1)
        scan = scan_agg[..., scan_agg[0] != 0]
        # self.io.send_data(('lidar-test-points', scan))
        return scan

    def align_center(self, scan, offset=0, ref=(1, 1), width=unit):
        left_ref, right_ref = ref
        left_point = scan[0][get_closest_point(scan[1], (math.pi / 2) - offset)]
        right_point = scan[0][get_closest_point(scan[1], (3 * math.pi / 2) - offset)]
        left_delta = width / 2 - left_point
        right_delta = right_point - width / 2
        # import pdb; pdb.set_trace()
        if left_ref and right_ref:
            shift = statistics.mean((left_delta, right_delta))
        elif left_ref:
            shift = left_delta
        else:
            shift = right_delta
        action = self.mob.exec_line(Point3(-shift))
        return action

    def align_to_victim(self, scans=10, front_prox=100, ref=False):
        scan_polar_raw = self.get_x_scans(scans)
        scan_polar = scan_polar_raw[
            ..., np.logical_or(15 * math.pi / 8 < scan_polar_raw[1], scan_polar_raw[1] < math.pi / 8)]
        poi = scan_polar[..., np.argmin(scan_polar[0])]
        angle = poi[1]
        if angle > math.pi:
            angle -= 2 * math.pi
        action = self.mob.rotate(-angle)
        self.do_action(action)
        front_dist = int(np.min(scan_polar[0])) - front_prox
        self.do_action(self.mob.exec_line(Point3(0, .9 * front_dist)))
        if ref:
            self.align(ref=(1, 1))
        scan_polar_raw = self.get_x_scans(scans)
        status.prepare_pickup()
        scan_polar = scan_polar_raw[
            ..., np.logical_or(15 * math.pi / 8 < scan_polar_raw[1], scan_polar_raw[1] < math.pi / 8)]
        poi = scan_polar[..., np.argmin(scan_polar[0])]
        angle = poi[1]
        if angle > math.pi:
            angle -= 2 * math.pi
        action = self.mob.rotate(-angle)
        self.do_action(action)
        front_dist = int(np.min(scan_polar[0])) - front_prox
        self.do_action(self.mob.exec_line(Point3(0, front_dist)))
        status.pickup()

    def victim_in_region(self, x_region=None, y_region=None, scans=10):
        # import pdb; pdb.set_trace()
        if not (x_region or y_region):
            raise ValueError
        scan_polar = self.get_x_scans(scans)
        scan = pol2cart(scan_polar[0], scan_polar[1] + math.pi / 2)
        self.io.send_data(('lidar-test-points', scan_polar))
        if x_region is not None:
            scan = scan[
                ...,
                np.logical_and(
                    scan[0] > x_region[0],
                    scan[0] < x_region[1]
                )
            ]
        if y_region is not None:
            scan = scan[...,
                        np.logical_and(
                            scan[1] > y_region[0],
                            scan[1] < y_region[1]
                        )
            ]
        # self.io.send_data(('lidar-test-points', scan))
        return list(np.shape(scan))[1] > 0

    def get_victim_position(self, x_region, y_region, scans=10):
        scan_polar = self.get_x_scans(scans)
        scan = pol2cart(scan_polar[0], scan_polar[1] + math.pi / 2)
        scan = scan[
            ...,
            np.logical_and(
                scan[0] > x_region[0],
                scan[0] < x_region[1]
            )
        ]

        scan = scan[...,
                    np.logical_and(
                        scan[1] > y_region[0],
                        scan[1] < y_region[1]
                    )
        ]
        return np.mean(scan, axis=1)

    def align_from(self, angle, postion_from, ref, flip=1, axis='x'):
        scan = self.get_x_scans(5)
        angle_offset = self.get_angle(scan, ref=ref)
        pos_offset = flip * (postion_from - self.align_span(scan, angle - angle_offset))
        action = self.mob.rotate(-angle_offset)
        self.do_action(action)
        if axis == 'x':
            action = self.mob.exec_line(Point3(0, pos_offset))
        if axis == 'y':
            action = self.mob.exec_line(Point3(pos_offset))
        self.do_action(action)

        # left_offset = self.align_span(scan, (3 * math.py / 2) + angle_offset)
        # rear_offset = self.align_span(scan , (math.pi) + angle_offset)

    def get_angle(self, scan, ref, t=0):
        left_ref, right_ref = ref
        left_scan = scan[..., np.logical_and(2 * math.pi / 12 < scan[1], scan[1] < 10 * math.pi / 12)]
        right_scan = scan[..., np.logical_and(14 * math.pi / 12 < scan[1], scan[1] < 22 * math.pi / 12)]
        left_cart_scan = pol2cart(left_scan[0], left_scan[1])
        right_cart_scan = pol2cart(right_scan[0], right_scan[1])
        if self.render:
            self.io.send_data(('lidar-test-points', np.concatenate((left_cart_scan, right_cart_scan), axis=1)))
        left_angle, *tail = np.polyfit(*left_cart_scan, 1)
        right_angle, *tail = np.polyfit(*right_cart_scan, 1)
        if left_ref and right_ref:
            slope = statistics.mean((left_angle, right_angle))
        elif left_ref:
            slope = left_angle
        else:
            slope = right_angle
        angle = math.atan(slope)
        print('calc angle:', math.degrees(angle))
        if abs(math.degrees(angle)) > 15 and t <= 3:
            # import pdb; pdb.set_trace()
            return self.get_angle(self.get_x_scans((t + 1) * 4), ref, t=1 + 1)

        return angle

    def do_action(self, action):
        action.set_status(status)
        action.start()
        while not action.complete:
            print(action.target, action.estimate_progress())

    def align_span(self, scan, angle_offset):
        return scan[0][get_closest_point(scan[1], angle_offset)]

    def align_angle(self, scan, ref=(0, 1)):
        angle = self.get_angle(scan, ref)
        action = self.mob.rotate(-angle)
        return action


def get_closest_point(array, value):
    return np.argmin(np.abs(array - value))


def pol2cart(rho, phi) -> (np.array, np.array):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array((x, y))


if __name__ == "__main__":
    main("render" in sys.argv, "debug" in sys.argv)
