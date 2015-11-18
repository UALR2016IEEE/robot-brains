import asyncio
import numpy as np
import math
import random
from utils.data_structures import Point3
import breezyslam.components


class Base:
    def __init__(self, sim_controller):

        # set sensor properties
        self.angle_range = math.radians(360)
        self.resolution = math.radians(1)
        self.frequency = 5.5

        # set sensor obscure ranges : [(obscure_center, obscure_range_from_center)]
        self.obscured = []
        for item in [(45, 17.5), (135, 17.5), (225, 17.5), (315, 17.5)]:
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

        # remove the rays that will be obscured
        # for item in self.obscured:
        #     # check to see if the obscured item crosses the angle-0 line
        #     if self.wrap(position.r + item[0], 0, 2.0 * math.pi) > self.wrap(position.r + item[1], 0, 2.0 * math.pi):
        #         # if obscured area crosses 0, keep the rays between the upper and lower lines
        #         rays = rays[np.logical_and(rays[:, 2] < self.wrap(position.r + item[0], 0, 2.0 * math.pi), rays[:, 2] > self.wrap(position.r + item[1], 0, 2.0 * math.pi))]
        #     else:
        #         # else keep the rays below the lower line and above the upper line
        #         rays = rays[np.logical_or(rays[:, 2] < self.wrap(position.r + item[0], 0, 2.0 * math.pi), rays[:, 2] > self.wrap(position.r + item[1], 0, 2.0 * math.pi))]

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
        hits[hits[:, 1] > 2.0 * math.pi, 1] -= 2.0 * math.pi
        hits[hits[:, 1] < 0, 1] += 2.0 * math.pi

        # better idea - set obscuring rays to distance=0
        # for item in self.obscured:
        #     lower_angle = self.wrap(position.r + item[0], 0, 2.0 * math.pi)
        #     upper_angle = self.wrap(position.r + item[1], 0, 2.0 * math.pi)
        #     if lower_angle < upper_angle:
        #         # zero the rays between the lines
        #         cut = np.logical_and(hits[:, 1] > lower_angle, hits[:, 1] < upper_angle)
        #     else:
        #         # else obscured area crosses 0, zero the rays below the lower line and above the upper line
        #         cut = np.logical_or(hits[:, 1] < lower_angle, hits[:, 1] > upper_angle)
        #
        #     hits[cut, 0] = 0

        return hits[::-1, :]

    @staticmethod
    def wrap(number, floor, ceiling):
        """
        :param number: any number
        :param floor: lower bound
        :param ceiling: upper bound
        :return: number between lower and upper bound
        """
        if number < floor:
            return number + ceiling
        elif number > ceiling:
            return math.fmod(number, ceiling)
        else:
            return number

    def __await__(self):
        def closure():
            while True:
                yield from asyncio.sleep(1 / 5.5)
