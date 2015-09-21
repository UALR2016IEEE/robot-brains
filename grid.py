import math
import random
import numpy as np


class Grid:
    def __init__(self, mock=False):
        self.mock = mock
        self.grid = []
        self.objects = {
            'FLOOR': 0,
            'WALL': 1,
            'RIVER': 2,
            'OBSTACLE_BROWN': 3,
            'OBSTACLE_BLUE': 4,
            'OBSTACLE_PURPLE': 5,
            'VICTIM_RED': 6,
            'VICTIM_YELLOW': 7,
            'RESCUE_YELLOW': 10,
            'RESCUE_RED': 11,
            'START': 12
        }

        if self.mock:
            self.grid = np.loadtxt("field.csv", delimiter=",")

            # Choose victims - colorsLeft are left top/bottom colors, colorsRight are right top/bottom colors [0 = red, 1 = yellow]
            vColorsCity = random.randint(0, 1)
            vColorsOffroad = random.randint(0, 1)

            # Choose offroad positions - whether victims are top/bottom [0 = top, 1 = bottom]
            vOffroadPositions = sorted([0, 1], key=lambda k: random.random())
            vObstaclePositions = random.randint(0, 1), random.randint(0, 1)

            # set colors of city victims
            if vColorsCity:
                self.grid[self.grid == 60] = self.objects['VICTIM_YELLOW']
                self.grid[self.grid == 70] = self.objects['VICTIM_RED']
            else:
                self.grid[self.grid == 60] = self.objects['VICTIM_RED']
                self.grid[self.grid == 70] = self.objects['VICTIM_YELLOW']

            # select offroad victim positions - blank the extra two
            if vOffroadPositions[0]:
                y, x = np.argwhere(self.grid == 80)[0]
                self.grid[y][x] = self.objects['FLOOR']
            else:
                y, x = np.argwhere(self.grid == 80)[1]
                self.grid[y][x] = self.objects['FLOOR']

            if vOffroadPositions[1]:
                y, x = np.argwhere(self.grid == 90)[0]
                self.grid[y][x] = self.objects['FLOOR']
            else:
                y, x = np.argwhere(self.grid == 90)[1]
                self.grid[y][x] = self.objects['FLOOR']

            # set color of offroad victims
            if vColorsOffroad:
                self.grid[self.grid == 80] = self.objects['VICTIM_YELLOW']
                self.grid[self.grid == 90] = self.objects['VICTIM_RED']
            else:
                self.grid[self.grid == 80] = self.objects['VICTIM_RED']
                self.grid[self.grid == 90] = self.objects['VICTIM_YELLOW']

            # select obstacle positions - blank the extra two
            if vObstaclePositions[0]:
                y, x = np.argwhere(self.grid == 4)[0]
                self.grid[y:y + 4, x:x + 4] = self.objects['FLOOR']
            else:
                y, x = np.argwhere(self.grid == 4)[16]
                self.grid[y:y + 4, x:x + 4] = self.objects['FLOOR']

            # select obstacle positions - blank the extra two
            if vObstaclePositions[1]:
                y, x = np.argwhere(self.grid == 5)[0]
                self.grid[y:y + 4, x:x + 4] = self.objects['FLOOR']
            else:
                y, x = np.argwhere(self.grid == 5)[4]
                self.grid[y:y + 4, x:x + 4] = self.objects['FLOOR']

    def getGrid(self):
        return self.grid

    def getRadialDistances(self, py, px, angle, angleRange, resolution, display=False):
        snaps = int(angleRange / resolution)
        currentAngle = self.wrap(angle - angleRange / 2.0 + random.random() * resolution, 0.0, 2.0 * math.pi)
        hits = []

        for snap in range(snaps):
            distance = 0.0
            cy, cx = py, px

            while self.grid[cy][cx] == 0:
                distance += 0.1
                cy, cx = self.getCoords(py, px, currentAngle, distance)

            hits.append([distance, currentAngle])
            currentAngle = self.wrap(currentAngle + resolution, 0.0, 2.0 * math.pi)

        return hits

    @staticmethod
    def wrap(number, floor, ceiling):
        if number < floor:
            return number + ceiling
        elif number > ceiling:
            return math.fmod(number, ceiling)
        else:
            return number

    @staticmethod
    def roundUp(number):
        return int(number) + 1

    @staticmethod
    def roundDown(number):
        return int(number)

    def getCoords(self, sy, sx, angle, distance):
        # Q1 - y rounds up, x round down
        if 0.0 <= angle < math.pi / 2.0:
            return self.roundUp(math.sin(angle) * distance) + sy, self.roundDown(math.cos(angle) * distance) + sx

        # Q2 - y rounds up, x rounds up
        if math.pi / 2.0 <= angle < math.pi:
            return self.roundUp(math.sin(angle) * distance) + sy, self.roundUp(math.cos(angle) * distance) + sx

        # Q3 - y rounds down, x rounds up
        if math.pi <= angle < math.pi * 3.0 / 2.0:
            return self.roundDown(math.sin(angle) * distance) + sy, self.roundUp(math.cos(angle) * distance) + sx

        # Q4 - y rounds down, x rounds down
        if math.pi * 3.0 / 2.0 <= angle < math.pi * 2.0:
            return self.roundDown(math.sin(angle) * distance) + sy, self.roundDown(math.cos(angle) * distance) + sx
