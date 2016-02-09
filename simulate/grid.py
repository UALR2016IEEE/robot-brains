import random

import numpy as np


class Grid(object):
    def __init__(self):
        self.data = []
        self.colors = []
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
        self.object_colors = {
            'FLOOR': (255, 255, 255),
            'WALL': (0, 0, 0),
            'RIVER': (0, 0, 255),
            'OBSTACLE_BROWN': (165, 42, 42),
            'OBSTACLE_BLUE': (0, 191, 255),
            'OBSTACLE_PURPLE': (128, 0, 128),
            'VICTIM_RED': (255, 0, 0),
            'VICTIM_YELLOW': (255, 255, 0),
            'RESCUE_YELLOW': (255, 255, 0),
            'RESCUE_RED': (255, 0, 0),
            'START': (0, 255, 0)
        }

        self.init_grid()

    def init_grid(self):
        self.data = np.loadtxt("simulate/field.csv", delimiter=",")
        self.colors = np.zeros(shape=(96, 96, 3))

        # Choose victims - colorsLeft are left top/bottom colors, colorsRight are right top/bottom colors [0 = red, 1 = yellow]
        vColorsCity = random.randint(0, 1)
        vColorsOffroad = random.randint(0, 1)

        # Choose offroad positions - whether victims are top/bottom [0 = top, 1 = bottom]
        vOffroadPositions = sorted([0, 1], key=lambda k: random.random())
        vObstaclePositions = random.randint(0, 1), random.randint(0, 1)

        # set colors of city victims
        if vColorsCity:
            self.data[self.data == 60] = self.objects['VICTIM_YELLOW']
            self.data[self.data == 70] = self.objects['VICTIM_RED']
        else:
            self.data[self.data == 60] = self.objects['VICTIM_RED']
            self.data[self.data == 70] = self.objects['VICTIM_YELLOW']

        # select offroad victim positions - blank the extra two
        if vOffroadPositions[0]:
            y, x = np.argwhere(self.data == 80)[0]
            self.data[y][x] = self.objects['FLOOR']
        else:
            y, x = np.argwhere(self.data == 80)[1]
            self.data[y][x] = self.objects['FLOOR']

        if vOffroadPositions[1]:
            y, x = np.argwhere(self.data == 90)[0]
            self.data[y][x] = self.objects['FLOOR']
        else:
            y, x = np.argwhere(self.data == 90)[1]
            self.data[y][x] = self.objects['FLOOR']

        # set color of offroad victims
        if vColorsOffroad:
            self.data[self.data == 80] = self.objects['VICTIM_YELLOW']
            self.data[self.data == 90] = self.objects['VICTIM_RED']
        else:
            self.data[self.data == 80] = self.objects['VICTIM_RED']
            self.data[self.data == 90] = self.objects['VICTIM_YELLOW']

        # select obstacle positions - blank the extra two
        if vObstaclePositions[0]:
            y, x = np.argwhere(self.data == 4)[0]
            self.data[y:y + 4, x:x + 4] = self.objects['FLOOR']
        else:
            y, x = np.argwhere(self.data == 4)[16]
            self.data[y:y + 4, x:x + 4] = self.objects['FLOOR']

        # select obstacle positions - blank the extra two
        if vObstaclePositions[1]:
            y, x = np.argwhere(self.data == 5)[0]
            self.data[y:y + 4, x:x + 4] = self.objects['FLOOR']
        else:
            y, x = np.argwhere(self.data == 5)[4]
            self.data[y:y + 4, x:x + 4] = self.objects['FLOOR']

        for key, value in self.object_colors.items():
            self.colors[self.data == self.objects[key]] = value

        # now that the 'base' is done, repeat to scale up
        self.data = np.repeat(self.data, 10, axis=0)
        self.data = np.repeat(self.data, 10, axis=1)
        self.colors = np.repeat(self.colors, 10, axis=0)
        self.colors = np.repeat(self.colors, 10, axis=1)

    def get_pygame_grid(self):
        return np.transpose(self.colors, (1, 0, 2))
