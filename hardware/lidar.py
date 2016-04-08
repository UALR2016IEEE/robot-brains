import asyncio
import math
import random
import struct
from time import sleep
from typing import Union

import breezyslam.components
import numpy as np
import serial

import hardware.constants as const
from utils.data_structures import Point3

class Base(object):
    def __init__(self, controller, hw_addr=None):
        self._lidar = None
        self.build_lidar(controller, hw_addr)

    def build_lidar(self, controller, hw_addr):
        self.build_simulator(controller)

    def build_simulator(self, sim_controller):
        # set sensor properties
        self.angle_range = math.radians(360)
        self.resolution = math.radians(1)
        self.frequency = 5.5

        # set sensor obscure ranges : [(obscure_center, obscure_range_from_center)]
        self.obscured = []
        for item in [(45, 7), (135, 7), (225, 7), (315, 7)]:
            self.obscured.append((self.wrap(math.radians(item[0]) - math.radians(item[1]), 0, 2.0 * math.pi),
                                  self.wrap(math.radians(item[0]) + math.radians(item[1]), 0, 2.0 * math.pi)))

        # refer to grid element ids : set 0 (floor) and 12 (start-box) to be non-blocking elements
        self.non_blocking = [0, 12]

        # controller provides the simulated map
        self.sim_controller = sim_controller
        self.map = self.sim_controller.get_grid_data()

    @staticmethod
    def get_laser() -> breezyslam.components.Laser:
        """Returns the breezyslam.components.Laser that Lidar class uses
        :return: breezyslam.components.Laser: laser properties - scan_size, scan_rate_hz, detection_angle_degrees, distance_no_detection_mm
        """
        # laser properties - scan_size, scan_rate_hz, detection_angle_degrees, distance_no_detection_mm
        return breezyslam.components.Laser(360, 5.5, 360, 6000)

    def scan(self, position: Point3) -> np.ndarray:
        """Performs a scan simulation from a given point
        :param position: Point3 defining scan origin and direction
        :return: np.ndarray of scan hits
        """

        # for convenience, convert position (mm) into grid units (pix)
        p = position.mm2pix()
        px = p.x
        py = p.y
        pr = p.r

        # calculate how many measurements to take
        snaps = int(self.angle_range / self.resolution)

        # get a slightly randomized initial pr
        cr = self.wrap(pr - self.angle_range / 2.0 + random.random() * self.resolution, 0.0, 2.0 * math.pi)

        # generate rays array
        rays = np.ndarray(shape=(snaps, 3))
        rays[:, 0] = py
        rays[:, 1] = px
        rays[:, 2] = np.linspace(cr, cr + self.angle_range, snaps) % (2.0 * np.pi)

        # preallocate results array
        hits = np.ndarray(shape=(rays.shape[0], 3))

        # calculate ray deltas
        delta_x = np.cos(rays[:, 2])
        delta_y = np.sin(rays[:, 2])

        # while there are misses, increment the ones that haven't hit something blocking yet
        not_hit = np.in1d(self.map[rays[:, 0].astype(int), rays[:, 1].astype(int)], self.non_blocking)
        while np.any(not_hit):
            # since origin is upper-left corner instead of lower-left corner, y has to be flipped
            rays[not_hit, 0] -= delta_y[not_hit]
            rays[not_hit, 1] += delta_x[not_hit]
            not_hit = np.in1d(self.map[rays[:, 0].astype(int), rays[:, 1].astype(int)], self.non_blocking)

        # map results to hits array [distances must be in mm, so multiply by 2.54]
        hits[:, 0] = np.sqrt(np.square((rays[:, 1] - px)) + np.square((rays[:, 0] - py))) * 2.54
        hits[:, 1] = rays[:, 2] - pr
        hits[:, 2] = 1.0  # all the data is perfect - yay

        # make sure the angles are properly bounded
        while np.any(hits[hits[:, 1] >= 2.0 * math.pi, 1]):
            hits[hits[:, 1] > 2.0 * math.pi, 1] -= 2.0 * math.pi

        while np.any(hits[hits[:, 1] < 0, 1]):
            hits[hits[:, 1] < 0, 1] += 2.0 * math.pi

        # remove obscuring rays
        for item in self.obscured:
            lower_angle = item[0]
            upper_angle = item[1]
            if lower_angle < upper_angle:
                # zero the rays between the lines
                cut = np.logical_and(hits[:, 1] > lower_angle, hits[:, 1] < upper_angle)
            else:
                # else obscured area crosses 0, zero the rays below the lower line and above the upper line
                cut = np.logical_or(hits[:, 1] < upper_angle, hits[:, 1] > lower_angle)
            hits = hits[np.invert(cut)]

        return hits.T

    int_float = Union[int, float]

    @staticmethod
    def wrap(number: int_float, floor: int_float, ceiling: int_float) -> int_float:
        """Wraps an int or float between a floor and ceiling
        :param number: input number to wrap
        :param floor: lower wrapping bound
        :param ceiling: upper wrapping bound
        :return: float or int between lower and upper bound
        """
        range_size = ceiling - floor + 1
        if number < floor:
            number += range_size * ((floor - number) / range_size + 1)
        return floor + (number - floor) % range_size

    def __await__(self):
        def closure():
            while True:
                yield from asyncio.sleep(1 / 5.5)


class Lidar(Base):
    def write(self, cmd):
        packet = self.attach_header(cmd)
        # print("send: ", list(map(hex, packet)))
        self._lidar.write(packet)

    def read(self, size):
        packet = self._lidar.read(size)
        # print("received: ", list(map(hex, packet)))
        return packet

    def flush(self):
        self._lidar.flushInput()

    def set_target_speed(self, ang_velocity):
        pass

    async def get_current_speed(self):
        scan = await self.get_scan()
        return const.RP_SCAN_POINT_LEN/(len(scan) * const.RP_SCAN_TIME)

    def read_header(self):
        header = self.read(7)
        assert len(header) == 7
        header1, header2, payload_len_w_m, r_type = struct.unpack("<BBIB", header)
        assert header1 == 0xA5
        assert header2 == 0x5A
        payload_len = payload_len_w_m & 0x3FFFFFFF
        r_mode = (payload_len_w_m & 0xC0000000) >> 30
        return payload_len, r_mode, r_type

    @staticmethod
    def attach_header(cmd):
        return struct.pack('<BB', 0xA5, cmd)

    def reset(self):
        self.write(const.Commands.Reset)
        sleep(0.01)
        self.flush()
 
    def self_test(self):
        self.flush()
        self.write(const.Commands.Health)
        health_len, r_mode, r_type = self.read_header()
        payload = self.read(health_len)
        assert health_len == 3
        assert r_mode == const.Modes.Single
        assert r_type == 0x06
        health, ecode = struct.unpack("<BH", payload)
        return health == 0

    def get_info(self):
        self.flush()
        self.write(const.Commands.Info)
        info_len, r_mode, r_type = self.read_header()
        payload = self.read(info_len)
        assert info_len == 20
        assert r_type == 4
        model, firmware_minor, firmware_major, hardware, *sn = struct.unpack("<BBBB16s", payload)
        return model, firmware_minor, firmware_major, hardware, sn

    def stop(self):
        self.write(const.Commands.Stop_Scan)
        sleep(0.1)

    def _scanner(self, flip=False, offset=90):
        if flip:
            scan_translation = lambda angle: 360 - angle + offset
        else:
            scan_translation = lambda angle: angle + offset
        self.stop()
        self.flush()
        self.write(const.Commands.Start_Scan)
        info_len, r_mode, r_type = self.read_header()
        assert info_len == 5
        assert r_type == 0x81
        assert r_mode == 1
        for i in range(100):
            if self._lidar.inWaiting() < info_len:
                sleep(0.1)
            else:
                break
        else:
            raise TimeoutError("No data received from lidar")
        payload = self.read(info_len)
        quality, angle, distance, start = self._unpack_scan(payload)
        assert start
        angles = [angle]
        qualities = [quality]
        distances = [distance]
        try:
            while True:
                if self._lidar.inWaiting() > 4000:
                    print("LIDAR OVERFLOW WARNING")
                while self._lidar.inWaiting() < info_len:
                    pass
                payload = self.read(info_len)
                quality, angle, distance, start = self._unpack_scan(payload)
                if start:
                    yield np.array((distances, np.deg2rad(angles), qualities))
                    angles = []
                    qualities = []
                    distances = []
                else:
                    yield
                if distance > 0:
                    angles.append(scan_translation(angle) % 360)
                    distances.append(distance)
                    qualities.append(quality)
        except GeneratorExit:
            self.stop()

    def scanner(self, *args, **kwargs):
        for scan in self._scanner(*args, **kwargs):
            if scan is not None:
                yield scan

    async def get_scan_async(self):
        scanner = self.scanner()
        await asyncio.sleep(0.6)
        while True:
            data = next(scanner)
            if data:
                scanner.close()
                return data
            await asyncio.sleep(0.1)

    def get_scan(self):
        scanner = self.scanner()
        while True:
            data = next(scanner)
            if data is not None:
                scanner.close()
                yield data
                raise StopIteration()
            yield

    def _unpack_scan(self, payload):
        quality, angle, distance = struct.unpack("<BHH", payload)
        start_bit = quality & 0b1
        not_start_bit = quality & 0b10
        assert start_bit ^ not_start_bit
        quality >>= 2
        check = angle & 0b1
        assert check
        angle >>= 1
        angle /= 64
        distance /= 4
        return quality, angle, distance, start_bit

    def build_lidar(self, controller, hw_addr):
        self.connect(hw_addr)
        self.flush()

    def connect(self, hw_addr: str):
        self._lidar = serial.Serial(hw_addr,
                                    baudrate=115200,
                                    timeout=20,
                                    dsrdtr=False
                                    )
        self._lidar.setDTR(0)
        for i in range(5):
            try:
                if not self.self_test():
                    raise IOError("Could not communicate with Lidar")
            except Exception as err:
                pass
            else:
                break
        else:
            raise err

    def disconnect(self):
        self._lidar.close()

    def __del__(self):
        self.disconnect()
