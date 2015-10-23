import navigation_platform.navigation as navlib
import hardware.lidar
import multiprocessing
from utils.data_structures_threadsafe import Point3


class Base(multiprocessing.Process):
    def __init__(self, navigation: navlib.Base, sim_controller):
        self.nav = navigation
        self.pos = Point3()
        self.sim_controller = sim_controller
        self.halt = multiprocessing.Value(bool, False)
        self.components = multiprocessing.Queue()
        self.SLAM = multiprocessing.Process.__init__(self, target=self.nav_inf, args=(self.nav, self.pos, self.sim_controller, self.halt, self.components))

    def start(self):
        self.halt.value = False
        super(Base, self).start()

    def stop(self):
        self.halt.value = True

    @staticmethod
    def nav_inf(nav: navlib, pos, sim_controller, halt, components: multiprocessing.Queue):
        lidar = hardware.lidar.Base(sim_controller)
        while not halt:
            while not components.empty():
                nav.add_component(*components.get())
            lidar_data = lidar.scan(pos)
            nav.run_components(lidar_data)

            nav  # blah
            # slam loop

    def get_pos(self):
        return self.pos

    def add_component(self, name, func):
        self.components.put((name, func))

    @property
    def position(self):
        return self.get_pos()
