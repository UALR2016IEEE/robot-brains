import numpy as np
import math
import random
from utils.data_structures import Point2, Point3


class Base:
    def __init__(self, controller):

        # set 'sensor' angular range, angular resolution, and blackout areas
        self.angle_range = math.radians(360)
        self.resolution = math.radians(1)
        self.obscured = [(math.radians(40), math.radians(50)), (math.radians(130), math.radians(140)), (math.radians(220), math.radians(230)), (math.radians(310), math.radians(320))]

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

        # preallocate results
        hits = np.ndarray(shape=(snaps, 3))

        # set 0 (floor) and 12 (start-box) to be non-blocking elements
        non_blocking = [0, 12]

        # iterate over all snaps
        for snap in range(snaps):

            # update current point
            cy, cx, cr = position.y, position.x, self.wrap(cr + self.resolution, 0.0, 2.0 * math.pi)

            # dx, dy are constant
            dy, dx = -2.0 * math.sin(cr), 2.0 * math.cos(cr)

            # until something blocking is hit, increment cx, cy with deltas
            while self.map[int(cy), int(cx)] in non_blocking:
                cy, cx = dy + cy, dx + cx

            # save the data
            hits[snap, 0] = math.sqrt((cx - position.x)**2 + (cy - position.y)**2)  # distance from initial point to hit point
            hits[snap, 1] = self.wrap(cr - position.r, 0.0, 2.0 * math.pi)  # position.r of measurement relative to front of robot
            hits[snap, 2] = 1.0  # accuracy percent value

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

