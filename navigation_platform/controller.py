import asyncio
import multiprocessing
import time
from utils.data_structures_threadsafe import Point3 as Safe_Point3

import hardware


class Base(multiprocessing.Process):
    def __init__(self, navigation: type, sim_controller, render=False):
        self.nav = navigation
        self.sim_controller = sim_controller
        self.pos = multiprocessing.Queue()
        self.cpos = Safe_Point3()

        self.halt = multiprocessing.Event()
        self.components = multiprocessing.Queue()
        self.actions = multiprocessing.Queue()
        self.nav_process = self.create_nav_process(render)
        self.current_action = None
        self.pos_lock = multiprocessing.Lock()

    def create_nav_process(self, render=False):
        return multiprocessing.Process.__init__(
            self, target=self.nav_interface, args=
            (
                self.nav,
                self.sim_controller.position,
                self.pos,
                self.sim_controller,
                self.halt,
                self.components,
                self.actions,
                render
            )
        )

    def start(self):
        super(Base, self).start()
        self.add_component('SLAM', self.nav.slam)

    def stop(self):
        self.halt.set()

    @staticmethod
    def nav_interface(nav: type, initial_position, position_queue: multiprocessing.Queue, sim_controller,
                      halt: multiprocessing.Event, components: multiprocessing.Queue, actions: multiprocessing.Queue,
                      render: bool):
        print('initial pos', initial_position.mm2pix())
        navigator = nav(position=initial_position)
        lidar = hardware.Lidar(sim_controller, "/dev/ttyAMA0")
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

        for lidar_data in lidar.get_scan():
            if halt.is_set():
                break
            while not components.empty():
                navigator.add_component(*components.get())

            if render:
                io.send_data(('robot-pos', navigator.get_position()))
                io.send_data(('lidar-points', (navigator.get_position(), lidar_data)))

            if not actions.empty() and action is None:
                print('getting action!')
                action = actions.get()
                print('got action!')
            if action is None:
                # dxy, dr, dt
                estimates = 0, 0, 0
                if not no_action:
                    no_action = True
                    print('no action', navigator.get_position())
                    navigator.export_gif()
                    halt.set()
            else:
                if not action.started:
                    print('staring action!')
                    action.start()
                estimates = action.estimate_progress()
                if action.complete:
                    action = None
            # print('running components')
            navigator.run_components(lidar_data, estimates)
            position = navigator.get_position()
            # current_position[None] = position[None]
            position_queue.put(position)
            # print('saving map')
            navigator.save_map()

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
        pos = Safe_Point3()
        pos[None] = self.cpos[None]
        return pos

    def set_action(self, action):
        print('setting action!')
        self.current_action = action
        self.actions.put(action)


class Controller(Base):
    def create_nav_process(self, render=False):
        return multiprocessing.Process.__init__(
            self, target=self.nav_interface, args=
            (
                self.nav,
                Safe_Point3(),
                self.pos,
                None,
                self.halt,
                self.components,
                self.actions,
                render
            )
        )

    @staticmethod
    def nav_interface(nav: type, initial_position, position_queue: multiprocessing.Queue, sim_controller,
                      halt: multiprocessing.Event, components: multiprocessing.Queue, actions: multiprocessing.Queue,
                      render: bool):
        print('initial pos', initial_position.mm2pix())
        navigator = nav(position=initial_position)
        lidar = hardware.RPi_Lidar(sim_controller, "/dev/ttyAMA0")
        action = None
        navigator.set_position(initial_position)
        no_action = False
        scan_time = time.time()
        if render:
            import status_io.client
            io = status_io.client.IOHandler()
            io.start('localhost', 9998)

            io.send_data(('full-simulation', None))
            io.send_data(('grid-colors', sim_controller.grid.get_pygame_grid()))
            io.send_data(('robot-pos', initial_position))
        lidar.set_motor_duty(90)
        try:
            for lidar_data in lidar.get_scan():
                if halt.is_set():
                    break
                while not components.empty():
                    navigator.add_component(*components.get())

                if render:
                    io.send_data(('robot-pos', navigator.get_position()))
                    io.send_data(('lidar-points', (navigator.get_position(), lidar_data)))

                if not actions.empty() and action is None:
                    print('getting action!')
                    action = actions.get()

                if action is not None:
                    if not action.started:
                        print('staring action!')
                        action.start()
                    dx_dy = action.estimate_progress()
                    dt = time.time() - scan_time
                    estimates = (dx_dy, 0, dt)
                    scan_time = time.time()
                    if action.complete:
                        action = None

                else:
                    estimates = Safe_Point3()
                # print('running components')
                navigator.run_components(lidar_data, estimates)
                position = navigator.get_position()
                # current_position[None] = position[None]
                position_queue.put(position)
                # print('saving map')
        except Exception as e:
            lidar.set_motor_duty(0)
            raise e
