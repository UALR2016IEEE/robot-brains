__author__ = 'StaticVOiDance'

import navigation_platform.navigation as navlib
import multiprocessing
from utils import Point


class _BaseController(multiprocessing.Process):
    def __init__(self, navigation: navlib._Base):
        self.nav = navigation
        self.pos = Point()
        self.halt = multiprocessing.Value(bool, False)
        self.components = multiprocessing.Queue()
        self.SLAM = multiprocessing.Proceses.__init__(self, target=self.nav_inf,
                                                      args=(self.nav, self.pos, self.halt, self.components))

    def start(self):
        self.halt.value = False
        super(_Base, self).run()

    def stop(self):
        self.halt.value = True

    @staticmethod
    def nav_inf(nav: navlib, pos, halt, components: multiprocessing.Queue):
        lidar = Lidar()
        while not halt:
            while not components.empty():
                nav.add_component(*components.get())
            lidar_data = lidar.get_data()
            nav.run_components(lidar_data)

            nav #blah
            #slam loop

    def get_pos(self):
        return self.pos

    def add_component(self, name, func):
        self.components.put((name, func))

    @property
    def position(self):
        return self.get_pos()
