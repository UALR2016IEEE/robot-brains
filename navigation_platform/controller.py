import navigation_platform.navigation as navlib
import hardware.lidar
import multiprocessing
from utils.data_structures_threadsafe import Point3
import types


class Base(multiprocessing.Process):
    def __init__(self, navigation: types.CodeType, sim_controller):
        self.nav = navigation
        self.sim_controller = sim_controller
        self.pos = Point3()
        self.halt = multiprocessing.Event()
        self.components = multiprocessing.Queue()
        self.actions = multiprocessing.Queue()
        self.navproc = multiprocessing.Process.__init__(self, target=self.nav_interface, args=(self.nav, self.pos, self.sim_controller, self.halt, self.components, self.actions))
        self.current_action = None

    def start(self):
        self.halt.set()
        super(Base, self).start()
        self.add_component('SLAM', self.nav.slam)

    def stop(self):
        self.halt.value = True

    @staticmethod
    def nav_interface(nav: type, pos, sim_controller, halt: multiprocessing.Event, components: multiprocessing.Queue, actions: multiprocessing.Queue):
        navigator = nav()
        lidar = hardware.lidar.Base(sim_controller)
        action = None
        navigator.set_pos(pos)
        while not halt.is_set():
            while not components.empty():
                navigator.add_component(*components.get())
            while not actions.empty():
                action = actions.get()
            if action is None:
                es_pos = Point3()
            else:
                es_pos = action.estimate_position(pos)
            lidar_data = lidar.scan(es_pos)
            navigator.run_components(lidar_data)

    def get_pos(self):
        return self.pos

    def add_component(self, name, func):
        self.components.put((name, func))

    @property
    def position(self):
        return self.get_pos()

    def set_action(self, action):
        self.current_action = action
        self.actions.put(action)


class Controller:
    pass

