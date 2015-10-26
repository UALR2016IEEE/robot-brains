import types
from utils.data_structures import Point3


class Base:
    def __init__(self, cid: str=None):
        self.components = {}
        self.position = Point3()

    def set_position(self, point: Point3):
        self.position = point

    def get_position(self):
        return self.position

    @staticmethod
    def slam(self):
        while True:
            lidar, estimated_position = yield
            self.position.x = estimated_position.x
            self.position.y = estimated_position.y
            self.position.r = estimated_position.r

    def add_component(self, name: str, func: types.FunctionType):
        self.components[name] = func(self)
        for component in self.components.values():
            component.send(None)

    def run_components(self, lidar_data, estimated_position):
        for key, component in self.components.items():
            try:
                component.send((lidar_data, estimated_position))
            except StopIteration:
                self.components.pop(key)


class Navigation(Base):
    def __init__(self, cid: str=None):
        if cid:
            self.connect(cid)

    def connect(self, cid: str=None):
        pass
