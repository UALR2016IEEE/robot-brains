import types
from utils import Point2


class Base:
    def __init__(self, cid: str=None):
        self.components = {}

    def get_pos(self) -> Point2:
        point = Point2()
        return point

    @property
    def position(self):
        return self.get_pos()

    def set_pos(self, point: Point2):
        pass

    def add_component(self, name: str, func: types.FunctionType):
        self.components[name] = func()

    def run_components(self, lidar_data):
        for key, component in self.components.items():
            if component.send(lidar_data):
                self.components.pop(key)


class Navigation(Base):
    def __init__(self, cid: str=None):
        if cid:
            self.connect(cid)

    def connect(self, cid: str=None):
        pass
