import numpy as np
import math
import random
import simulate.controller


class Base:
    def __init__(self, controller):
        self.angle_range = math.radians(360)
        self.resolution = math.radians(1)
        self.controller = controller
        self.map = np.ndarray(shape=(960, 960))
        self._load_map()

    def _load_map(self):
        self.map = self.controller.get_grid_data()

    def scan(self, py, px, angle) -> np.ndarray:
        snaps = int(self.angle_range / self.resolution)
        current_angle = self.wrap(angle - self.angle_range / 2.0 + random.random() * self.resolution, 0.0, 2.0 * math.pi)
        hits = np.ndarray(shape=(snaps, 3))

        for snap in range(snaps):
            distance = 0
            cy, cx = py, px
            
            dx = math.cos(current_angle)
            dy = math.sin(current_angle)

            while self.map[int(cy), int(cx)] == 0:
                cy, cx = dy + cy, dx + cx

            hits[snap, 0] = math.sqrt((px - cx) * (px - cx) + (py - cy) * (py - cy))
            hits[snap, 1] = current_angle
            hits[snap, 2] = 1.0
            current_angle = self.wrap(current_angle + self.resolution, 0.0, 2.0 * math.pi)

        return hits

    @staticmethod
    def wrap(number, floor, ceiling):
        if number < floor:
            return number + ceiling
        elif number > ceiling:
            return math.fmod(number, ceiling)
        else:
            return number

