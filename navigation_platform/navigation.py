import math
import types

import numpy as np
from breezyslam.algorithms import RMHCSlam
from breezyslam.components import Laser

from utils.data_structures import Point3


class Base(object):
    def __init__(self, position=Point3(), cid: str = None):
        self.components = {}
        self.position = position
        self.laser = Laser(360, 5.5, 360, 6000)
        self.slam_object = RMHCSlam(self.laser, 960, 2.438, map_quality=40, sigma_xy_mm=200, sigma_theta_degrees=40,
                                    max_search_iter=500, init_x=self.position.x / 960, init_y=self.position.y / 960,
                                    init_r=math.degrees(self.position.r), hole_width_mm=100)
        # self.slam_object = RMHCSlam(self.laser, 960, 2.438, map_quality=10, sigma_xy_mm=100, sigma_theta_degrees=20, max_search_iter=1000, init_x=self.position.x / 960, init_y=self.position.y / 960, init_r=math.degrees(self.position.r), hole_width_mm=100)
        self.trajectory = []

    def set_position(self, point: Point3):
        self.position = point

    def get_position(self):
        return self.position

    def save_map(self):
        from PIL import Image

        print('saving nav map')

        # Create a byte array to receive the computed maps
        map_bytes = bytearray(960 * 960)
        # Get final map
        self.slam_object.getmap(map_bytes)

        # Put trajectory into map as black pixels
        for coords in self.trajectory:
            x_mm, y_mm = coords

            x_pix = self.mm2pix(x_mm)
            y_pix = self.mm2pix(y_mm)

            map_bytes[y_pix * 960 + x_pix] = 0

        # Save map and trajectory as PNG file
        image = Image.frombuffer('L', (960, 960), map_bytes, 'raw', 'L', 0, 1)
        image.save('test_image_nav.png')

    def slam(self):
        while True:
            lidar, estimated_velocity = yield
            self.slam_object.update(lidar, estimated_velocity)
            self.position.x, self.position.y, self.position.r = self.slam_object.getpos()
            self.position.r = math.radians(self.position.r)
            self.trajectory.append((self.position.x, self.position.y))
            # convert back from mm to tenths of an inch (grid units)
            self.position.x /= 2.54
            self.position.y /= 2.54
            print('slam pos', self.position, 'estimates', estimated_velocity)

    def add_component(self, name: str, func: types.FunctionType):
        self.components[name] = func(self)
        for component in self.components.values():
            component.send(None)

    def run_components(self, lidar_data, estimated_velocity):
        for key, component in self.components.items():
            try:
                component.send((lidar_data, estimated_velocity))
            except StopIteration:
                self.components.pop(key)

    @staticmethod
    def mm2pix(mm):
        return int(mm / (2.438 * 1000. / 960))


class Navigation(Base):
    def __init__(self, cid: str = None):
        if cid:
            self.connect(cid)

    def connect(self, cid: str = None):
        pass
