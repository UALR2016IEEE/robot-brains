from utils.data_structures import Point3
from .grid import Grid


class Controller(object):
    def __init__(self, position: Point3):
        self.grid = Grid()
        self.position = position

    def init_grid(self):
        self.grid.init_grid()

    def get_grid_data(self):
        return self.grid.data

    def get_grid_colors(self):
        return self.grid.colors
