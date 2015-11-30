import asyncio
import queue
import struct

import numpy as np
import math
import random

import serial
import time

from utils.data_structures import Point3
import breezyslam.components
import hardware.constants as const


class Base:
    def __init__(self, controller, hw_addr=None):
        self._lidar = None
        self.build_lidar(controller, hw_addr)

    def build_lidar(self, controller, hw_addr):
        self.build_simultor(controller)

    def build_simultor(self, sim_controller):
        # set sensor properties
        self.angle_range = math.radians(360)
        self.resolution = math.radians(1)
        self.frequency = 5.5

        # set sensor obscure ranges : [(obscure_center, obscure_range_from_center)]
        self.obscured = []
        # for item in [(45, 7), (135, 7), (225, 7), (315, 7)]:
        #     self.obscured.append((self.wrap(math.radians(item[0]) - math.radians(item[1]), 0, 2.0 * math.pi), self.wrap(math.radians(item[0]) + math.radians(item[1]), 0, 2.0 * math.pi)))
        for item in [(60, 7), (180, 7), (300, 7)]:
            self.obscured.append((self.wrap(math.radians(item[0]) - math.radians(item[1]), 0, 2.0 * math.pi), self.wrap(math.radians(item[0]) + math.radians(item[1]), 0, 2.0 * math.pi)))

        self.non_blocking = [0, 12]  # refer to grid element ids : set 0 (floor) and 12 (start-box) to be non-blocking elements

        # controller provides the simulated map
        self.sim_controller = sim_controller
        self.map = np.ndarray(shape=(960, 960))

        # load the simulated map
        self._load_map()

    def _load_map(self):
        self.map = self.sim_controller.get_grid_data()

    def get_laser(self):
        # laser properties - scan_size, scan_rate_hz, detection_angle_degrees, distance_no_detection_mm
        return breezyslam.components.Laser(360, 5.5, 360, 6000)

    def scan(self, position: Point3) -> np.ndarray:
        """
        :param position: Point3 for y, x, r values
        :return: np.ndarray of hits
        """
        # calculate how many measurements to take
        snaps = int(self.angle_range / self.resolution)

        # get a slightly randomized initial position.r
        cr = self.wrap(position.r - self.angle_range / 2.0 + random.random() * self.resolution, 0.0, 2.0 * math.pi)
        # cr = self.wrap(position.r - self.angle_range / 2.0 + self.resolution, 0.0, 2.0 * math.pi)  # for testing, always returns same starting ray position

        # generate rays array
        rays = np.ndarray(shape=(snaps, 3))
        rays[:, 0] = position.y
        rays[:, 1] = position.x
        rays[:, 2] = np.linspace(cr, cr + self.angle_range, snaps) % (2.0 * np.pi)

        # preallocate results array
        hits = np.ndarray(shape=(rays.shape[0], 3))

        # calculate ray deltas
        delta_x = np.cos(rays[:, 2])
        delta_y = np.sin(rays[:, 2])

        # while there are misses, increment the ones that haven't hit something blocking yet
        not_hit = np.in1d(self.map[rays[:, 0].astype(int), rays[:, 1].astype(int)], self.non_blocking)
        while np.any(not_hit):
            rays[not_hit, 0] -= delta_y[not_hit]  # since origin is upper-left corner instead of lower-left corner, y has to be flipped
            rays[not_hit, 1] += delta_x[not_hit]  # but cheat a bit and use 2.0 * delta to make things a bit faster
            not_hit = np.in1d(self.map[rays[:, 0].astype(int), rays[:, 1].astype(int)], self.non_blocking)

        # map results to hits array
        hits[:, 0] = np.sqrt(np.square((rays[:, 1] - position.x)) + np.square((rays[:, 0] - position.y)))
        hits[:, 1] = (rays[:, 2] - position.r)
        hits[:, 2] = 1.0  # all the data is perfect - yay

        # make sure the angles are properly bounded
        while np.any(hits[hits[:, 1] > 2.0 * math.pi, 1]):
            hits[hits[:, 1] > 2.0 * math.pi, 1] -= 2.0 * math.pi

        while np.any(hits[hits[:, 1] < 0, 1]):
            hits[hits[:, 1] < 0, 1] += 2.0 * math.pi

        # better idea - set obscuring rays to distance=0
        for item in self.obscured:
            lower_angle = item[0]
            upper_angle = item[1]
            if lower_angle < upper_angle:
                # zero the rays between the lines
                cut = np.logical_and(hits[:, 1] > lower_angle, hits[:, 1] < upper_angle)
            else:
                # else obscured area crosses 0, zero the rays below the lower line and above the upper line
                cut = np.logical_or(hits[:, 1] < upper_angle, hits[:, 1] > lower_angle)
            hits[cut, 0] = 0

        return hits[::-1, :]

    @staticmethod
    def wrap(number, floor, ceiling):
        """
        :param number: any number
        :param floor: lower bound
        :param ceiling: upper bound
        :return: number between lower and upper bound
        """
        while number < floor:
            number += ceiling
        while number > ceiling:
            number -= ceiling
        return number

    def __await__(self):
        def closure():
            while True:
                yield from asyncio.sleep(1 / 5.5)


class Lidar(Base):
    def write(self, cmd):
        self._lidar.write(self.attach_header(cmd))

    def read(self, size):
        return self._lidar.read(size)

    def read_header(self):
        header = self.read(7)
        assert len(header) == 7
        header1, header2, payload_len_w_m, r_type = struct.unpack("<BBIB", header)
        assert header1 == 0xA5
        assert header2 == 0x5A
        payload_len = payload_len_w_m & 0x3FFFFFFF
        r_mode = (payload_len_w_m &     0xC0000000) >> 30
        return payload_len, r_mode, r_type

    @staticmethod
    def attach_header(cmd):
        return struct.pack('<BB', 0xA5, cmd)

    def reset(self):
        self.write(const.Commands.Reset)
        time.sleep(0.001)

    def self_test(self):
        self.write(const.Commands.Health)
        health_len, r_mode, r_type = self.read_header()
        payload = self.read(health_len)
        assert health_len == 3
        assert r_mode == const.Modes.Single
        assert r_type == 0x06
        health, ecode = struct.unpack("<BH", payload)
        return health == 0

    def get_info(self):
        self.write(const.Commands.Info)
        info_len, r_mode, r_type = self.read_header()
        payload = self.read(info_len)
        assert info_len == 20
        assert r_type == 4
        model, firware_minor, firmware_major, hardware, serial = struct.unpack("<BBBB16p", payload)
        return model, firware_minor, firmware_major, hardware, serial


    def build_lidar(self, controller, hw_addr):
        self.connect(hw_addr)

    def connect(self, hw_addr: str):
        self._lidar = serial.Serial(hw_addr,
                                           baudrate=115200,
                                           timeout=20)

    def disconnect(self):
        self._lidar.close()

    def __del__(self):
        self.disconnect()
