from .grid import Grid


class Controller:
    def __init__(self):
        self.grid = Grid()

    def init_grid(self):
        self.grid.init_grid()

    def get_grid_data(self):
        return self.grid.data

    def get_grid_colors(self):
        return self.grid.colors
