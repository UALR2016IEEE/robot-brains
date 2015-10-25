import types
from utils import Point3


class Base:
    def __init__(self, cid: str=None):
        self.components = {}
        self.position = Point3()

    def set_pos(self, point: Point3):
        self.position = point

    def get_pos(self):
        return self.position

    @staticmethod
    def slam(self):
        while True:
            lidar, es_pos = yield
            self.position.x = es_pos.x
            self.position.y = es_pos.y
            self.position.r = es_pos.r

    def add_component(self, name: str, func: types.FunctionType):
        self.components[name] = func(self)

    def run_components(self, lidar_data):
        for key, component in self.components.items():
            try:
                component.send(lidar_data)
            except StopIteration:
                self.components.pop(key)


class Navigation(Base):
    def __init__(self, cid: str=None):
        if cid:
            self.connect(cid)

    def connect(self, cid: str=None):
        pass
