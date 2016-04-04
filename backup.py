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
    
    brain.align_from(math.pi, 1.5 * unit, ref=(0, 1))
    brain.align_from(1 * math.pi / 2, 1.75 * unit, flip=1, axis='y', ref=(0, 1))
    brain.align_from(3 * math.pi / 2, 0.5 * unit, flip=-1, axis='y', ref=(0, 1))
    #brain.align(ref=(1, 0))
    brain.move((1, 0), ref=(1, 1)) 
    brain.move((1, 0), dist=4 * unit, sub_steps=4, ref=(0, 1))
    brain.move_until_proc(ref=(0, 1), front_prox=unit*0.5)
    brain.align(ref=(1, 1))
    status.claw(True)
    status.rail(True)
    brain.move_until_proc(ref=(1, 1))
    status.claw(False)
    time.sleep(1)
    status.rail(False)
    time.sleep(0.3)
    #import pdb;pdb.set_trace()
    brain.move((-1, 0), ref=(0, 1), dist=unit * .5, sub_steps=2)
    brain.move((-1, 0), ref=(1, 1), dist=unit * 2, sub_steps=2)
    brain.move((-1, 0), ref=(0, 1), dist=unit, sub_steps=1)
    brain.move((-1, 0), ref=(1, 1), dist=unit, sub_steps=1)
    brain.move((-1, 0), ref=(1, 0), dist=unit)
    brain.do_action(brain.mob.rotate(math.pi))
    brain.align(ref=(0, 1), scans=15)
    brain.align_from(0, unit, axis='x', ref=(1, 1), flip=-1)
    status.rail(False)
    time.sleep(0.5)
    status.claw(False)

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

    def move_until_proc(self, front_prox=95, ref=(1, 1)):
        for attemp in range(1):
            scan = self.get_x_scans(10)
            front_scan_polar = scan[..., np.logical_or(23 * math.pi / 12 < scan[1], scan[1] <  math.pi / 12)]
            front_scan = pol2cart(front_scan_polar[0], front_scan_polar[1])
            front_dist = int(np.min(front_scan[0])) - front_prox
            #import pdb; pdb.set_trace()
            front_shift = self.align_center(scan, ref=ref).target.y
            #print(front_shift, front_dist)
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
        scanner = self.lidar.scanner(flip=True, offset=270)
        scan_agg = next(scanner)
        for id, scan in zip(range(x-1), scanner):
            scan_agg = np.concatenate((scan, scan_agg), axis=1)
        return scan_agg[..., scan_agg[0] != 0]

    def align_center(self, scan, offset=0, ref=(1, 1), width=unit):
        left_ref, right_ref = ref
        left_point = scan[0][get_closest_point(scan[1], (3 * math.pi / 2) - offset)]
        right_point = scan[0][get_closest_point(scan[1], (math.pi / 2) - offset)]
        left_delta = width /2 - left_point
        right_delta = right_point - width / 2
        #import pdb; pdb.set_trace()
        if left_ref and right_ref:
            shift = statistics.mean((left_delta, right_delta))
        elif left_ref:
            shift = left_delta
        else:
            shift = right_delta
        action = self.mob.exec_line(Point3(-shift))
        return action

    def align_from(self, angle, postion_from, ref, flip=1, axis='x'):
        scan = self.get_x_scans(5)
        angle_offset = self.get_angle(scan, ref=ref)
        pos_offset = flip * (postion_from - self.align_span(scan, angle - angle_offset))
        action = self.mob.rotate(angle_offset)
        self.do_action(action)
        if axis == 'x':
            action = self.mob.exec_line(Point3(0, pos_offset))
        if axis == 'y':
            action = self.mob.exec_line(Point3(pos_offset))
        self.do_action(action)

        # left_offset = self.align_span(scan, (3 * math.py / 2) + angle_offset)
        # rear_offset = self.align_span(scan , (math.pi) + angle_offset)

    def get_angle(self, scan, ref):
        left_ref, right_ref = ref
        left_scan = scan[..., np.logical_and(14 * math.pi / 12 < scan[1], scan[1] < 22 * math.pi / 12)]
        right_scan = scan[..., np.logical_and(2 * math.pi / 12 < scan[1], scan[1] < 10 * math.pi / 12)]
        left_angle, *tail = np.polyfit(*pol2cart(left_scan[0], left_scan[1]), 1)
        right_angle, *tail = np.polyfit(*pol2cart(right_scan[0], right_scan[1]), 1)
        if left_ref and right_ref:
            slope = statistics.mean((left_angle, right_angle))
        elif left_ref:
            slope = left_angle
        else:
            slope = right_angle
        return math.atan(slope)

    def do_action(self, action):
        action.set_status(status)
        action.start()
        while not action.complete:
            print(action.target, action.estimate_progress())

    def align_span(self, scan, angle_offset):
        return scan[0][get_closest_point(scan[1], angle_offset)]

    def align_angle(self, scan, ref=(0, 1)):
        slope = self.get_angle(scan, ref) * 0.05
        action = self.mob.rotate(math.atan(slope))
        return action



def get_closest_point(array, value):
    return np.argmin(np.abs(array - value))


def pol2cart(rho, phi) -> (np.array, np.array):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return x, y

if __name__ == "__main__":
    main("render" in sys.argv, "debug" in sys.argv)
