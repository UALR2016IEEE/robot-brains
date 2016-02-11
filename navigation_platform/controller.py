import asyncio
import multiprocessing

import hardware.lidar


class Base(multiprocessing.Process):
    def __init__(self, navigation: type, sim_controller, render=False):
        self.nav = navigation
        self.sim_controller = sim_controller
        self.pos = multiprocessing.Queue()

        self.halt = multiprocessing.Event()
        self.components = multiprocessing.Queue()
        self.actions = multiprocessing.Queue()
        self.nav_process = multiprocessing.Process.__init__(self, target=self.nav_interface, args=(
            self.nav, self.sim_controller.position, self.pos, self.sim_controller, self.halt, self.components,
            self.actions, render))
        self.current_action = None

    def start(self):
        super(Base, self).start()
        self.add_component('SLAM', self.nav.slam)

    def stop(self):
        self.halt.set()

    @staticmethod
    def nav_interface(nav: type, initial_position, position_queue: multiprocessing.Queue, sim_controller,
                      halt: multiprocessing.Event, components: multiprocessing.Queue, actions: multiprocessing.Queue,
                      render: bool):
        print('initial pos', initial_position)
        navigator = nav(position=initial_position)
        lidar = hardware.lidar.Base(sim_controller)
        action = None
        navigator.set_position(initial_position)
        no_action = False

        if render:
            import status_io.client
            io = status_io.client.IOHandler()
            io.start('localhost', 9998)

            io.send_data(('full-simulation', None))
            io.send_data(('grid-colors', sim_controller.grid.get_pygame_grid()))
            io.send_data(('robot-pos', initial_position))

        while not halt.is_set():
            while not components.empty():
                navigator.add_component(*components.get())
            lidar_data = lidar.scan(navigator.get_position())

            if render:
                io.send_data(('robot-pos', navigator.get_position()))
                io.send_data(('lidar-points', (navigator.get_position(), lidar_data)))

            if not actions.empty() and action is None:
                print('getting action')
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
                    print('staring action!')
                    action.start()
                estimates = action.estimate(navigator.get_position())
                if action.complete:
                    action = None
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
        print('setting action!')
        self.current_action = action
        self.actions.put(action)


class Controller(object):
    pass
