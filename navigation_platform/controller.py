import navigation_platform.navigation as navlib
import hardware.lidar
import multiprocessing
import asyncio


class Base(multiprocessing.Process):
    def __init__(self, navigation: type, sim_controller):
        self.nav = navigation
        self.sim_controller = sim_controller
        self.pos = multiprocessing.Queue()

        self.halt = multiprocessing.Event()
        self.components = multiprocessing.Queue()
        self.actions = multiprocessing.Queue()
        self.navproc = multiprocessing.Process.__init__(self, target=self.nav_interface, args=(self.nav, self.sim_controller.position, self.pos, self.sim_controller, self.halt, self.components, self.actions))
        self.current_action = None

    def start(self):
        super(Base, self).start()
        self.add_component('SLAM', self.nav.slam)

    def stop(self):
        self.halt.set()

    @staticmethod
    def nav_interface(nav: type, initial_position, position_queue: multiprocessing.Queue, sim_controller, halt: multiprocessing.Event, components: multiprocessing.Queue, actions: multiprocessing.Queue):
        print('initial pos', initial_position)
        navigator = nav(position=initial_position)
        lidar = hardware.lidar.Base(sim_controller)
        action = None
        navigator.set_position(initial_position)
        no_action = False
        while not halt.is_set():
            while not components.empty():
                navigator.add_component(*components.get())
            while not actions.empty():
                action = actions.get()
            if action is None:
                # dxy, dr, dt
                estimates = 0, 0, 0
                if not no_action:
                    no_action = True
                    print('no action', navigator.get_position())
                    navigator.save_map()
                    halt.set()
            else:
                if not action.started:
                    action.start()
                estimates = action.estimate(navigator.get_position())
                if action.complete:
                    action = None
            lidar_data = lidar.scan(navigator.get_position())
            navigator.run_components(lidar_data, estimates)
            position_queue.put(navigator.get_position())

    @asyncio.coroutine
    def get_pos(self):
        while True:
            if self.pos.empty():
                yield
            else:
                return self.pos.get()

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
