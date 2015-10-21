import numpy as np
import math
import random
from utils.data_structures import Point2, Point3


class Base:
    def __init__(self, controller):

        # set 'sensor' angular range, angular resolution, blackout areas, and nonblocking items
        self.angle_range = math.radians(360)
        self.resolution = math.radians(1)
        self.obscured = [(math.radians(40), math.radians(50)), (math.radians(130), math.radians(140)), (math.radians(220), math.radians(230)), (math.radians(310), math.radians(320))]
        self.non_blocking = [0, 12]  # refer to grid element id's : set 0 (floor) and 12 (start-box) to be non-blocking elements

        # controller provides the simulated map
        self.controller = controller
        self.map = np.ndarray(shape=(960, 960))

        # load the simulated map
        self._load_map()

    def _load_map(self):
        self.map = self.controller.get_grid_data()

    def scan(self, position) -> np.ndarray:
        """
        :param position: point3 for y, x, r values
        :return: np.ndarray of hits
        """
        # calculate how many measurements to take
        snaps = int(self.angle_range / self.resolution)

        # get a slightly randomized initial position.r
        cr = self.wrap(position.r - self.angle_range / 2.0 + random.random() * self.resolution, 0.0, 2.0 * math.pi)

        # preallocate results array
        hits = np.ndarray(shape=(snaps, 3))

        # generate rays array
        rays = np.ndarray(shape=(snaps, 3))
        rays[:, 0] = position.y
        rays[:, 1] = position.x
        rays[:, 2] = np.linspace(cr, cr + self.angle_range, snaps)

        # while there are hits, increment the ones that haven't hit something nonblocking yet
        not_hit = np.in1d(self.map[rays[:, 0].astype(int), rays[:, 1].astype(int)], self.non_blocking)
        while np.any(not_hit):
            rays[not_hit, 0] -= 2.0 * np.sin(rays[not_hit, 2])  # since origin is upper-left corner instead of lower-left corner, y has to be flipped
            rays[not_hit, 1] += 2.0 * np.cos(rays[not_hit, 2])  # but cheat a bit and use 2.0 * delta to make things a bit faster
            not_hit = np.in1d(self.map[rays[:, 0].astype(int), rays[:, 1].astype(int)], self.non_blocking)

        # map results to hits array
        hits[:, 0] = np.sqrt(np.square((rays[:, 1] - position.x)) + np.square((rays[:, 0] - position.y)))
        hits[:, 1] = (rays[:, 2] - position.r) % (2 * np.pi)
        hits[:, 2] = 1.0  # all the data is perfect - yay

        # remove the obscured areas
        for item in self.obscured:
            hits = hits[np.logical_or(hits[:, 1] < item[0], hits[:, 1] > item[1])]

        return hits

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

