import json
import math
import types

import numpy as np
from PIL import Image
from breezyslam.algorithms import RMHCSlam
from breezyslam.components import Laser

from utils.conversion import Conversion
from utils.data_structures import Point3


class Base(object):
    def __init__(self, position=Point3(), cid: str = None):
        self.components = {}
        self.position = position
        self.laser = Laser(360, 5.5, 360, 6000)

        with open('config.json', 'r') as f:
            self.config = json.load(f)

        self.slam_object = RMHCSlam(self.laser, self.config['map characteristics']['map size pixels'],
                                    self.config['map characteristics']['map size meters'], map_quality=30,
                                    sigma_xy_mm=200, sigma_theta_degrees=40,
                                    max_search_iter=500, init_x=self.position.x, init_y=self.position.y,
                                    init_r=math.degrees(self.position.r), hole_width_mm=40)
        # self.slam_object = RMHCSlam(self.laser, 960, 2.438, map_quality=10, sigma_xy_mm=100, sigma_theta_degrees=20, max_search_iter=1000, init_x=self.position.x / 960, init_y=self.position.y / 960, init_r=math.degrees(self.position.r), hole_width_mm=100)
        self.trajectory = []
        self.lidar_map = []
        self.reduced_map = []
        self.count = 0
        self.conversion = Conversion()

    def set_position(self, point: Point3):
        self.position = point

    def get_position(self):
        return self.position

    def export_gif(self):
        print('saving gif. ' + str(len(self.lidar_map)))
        clip = mp.ImageSequenceClip(self.lidar_map, fps=30)
        clip.write_gif('lidar_map.gif', fps=30, program='imageio')
        clip2 = mp.ImageSequenceClip(self.reduced_map, fps=30)
        clip2.write_gif('reduced_map.gif', fps=30, program='imageio')
        return

    def save_map(self):
        # print('saving nav map')

        # Create a byte array to receive the computed maps
        map_bytes = bytearray(960 * 960)
        # Get final map
        self.slam_object.getmap(map_bytes)

        # Put trajectory into map as black pixels
        for coords in self.trajectory:
            x_mm, y_mm = coords

            x_pix = self.conversion.mm2pix(x_mm)
            y_pix = self.conversion.mm2pix(y_mm)

            map_bytes[y_pix * 960 + x_pix] = 0

        mb = np.array(map_bytes)
        mb = np.reshape(mb, (960, 960))
        # print(mb)

        # Save map and trajectory as PNG file
        image = np.asarray(Image.frombuffer('L', (960, 960), map_bytes, 'raw', 'L', 0, 1))
        # image.save('test_image_nav.png')
        self.lidar_map.append(image)

        # convert to b/w
        mb[mb >= 127] = 255
        mb[mb < 127] = 0
        self.reduced_map.append(mb)
        print('map saved')

    def get_map(self):
        map_bytes = bytearray(960 * 960)
        self.slam_object.getmap(map_bytes)
        mb = np.array(map_bytes)
        mb = np.resize(mb, (960, 960))
        return mb

    def slam(self):
        print("SLAM Initialized")
        while True:
            lidar, estimated_velocity = yield
            self.slam_object.update(lidar)
            #print("Getting Position")
            self.position.x, self.position.y, self.position.r = self.slam_object.getpos()
            self.position.r = math.radians(self.position.r)
            self.trajectory.append((self.position.x, self.position.y))
            #print('slam pos', self.position, 'estimates', estimated_velocity)

    def add_component(self, name: str, func: types.FunctionType):
        self.components[name] = func
        for component in self.components.values():
            component.send(None)

    def run_components(self, lidar_data, estimated_velocity):
        for key, component in self.components.items():
            try:
                component.send((lidar_data, estimated_velocity))
            except StopIteration:
                self.components.pop(key)

class Navigation(Base):
    pass
