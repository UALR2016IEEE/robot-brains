import asyncio
import math
import statistics
import multiprocessing
import time

import numpy as np

from utils.data_structures_threadsafe import Point3 as Safe_Point3

import hardware


class Base(multiprocessing.Process):
    def __init__(self, navigation: type, sim_controller, stat_lock, render=False):
        self.nav = navigation
        self.sim_controller = sim_controller
        self.pos = multiprocessing.Queue()
        self.cpos = Safe_Point3()
        self.stat_lock = stat_lock

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

        for lidar_data in lidar.scanner():
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
            self, target=self.hardware_nav_interface, args=
            (
                self.nav,
                self.pos,
                None,
                self.halt,
                self.components,
                self.actions,
                render,
                self.stat_lock
            )
        )

    @staticmethod
    def hardware_nav_interface(nav: type, position_queue: multiprocessing.Queue, sim_controller,
                      halt: multiprocessing.Event, components: multiprocessing.Queue, actions: multiprocessing.Queue,
                      render: bool, stat_lock):
        from status_platform import status
        status.lock = stat_lock

        lidar = hardware.RPi_Lidar(sim_controller, "/dev/ttyAMA0")
        lidar.set_motor_duty(100)
        initial_position = Locator(lidar).locate()
        print('initial pos', initial_position.mm2pix())
        navigator = nav(position=initial_position)
        action = None
        navigator.set_position(initial_position)
        no_action = False
        scan_time = time.time()
        last_xy = Safe_Point3()

        while not components.empty():
            component = components.get()
            print("adding ", component)
            navigator.add_component(*component)
        try:
            for scan_counter, lidar_data in enumerate(lidar.scanner()):
                if scan_counter < 20:
                    print(scan_counter)
                    continue
                if halt.is_set():
                    break

                while not components.empty():
                    component = components.get()
                    print("adding ", component)
                    navigator.add_component(*component)

                if not actions.empty() and action is None:
                    print('getting action!')
                    action = actions.get()
                    action.set_status(status)
                    print('staring action!')
                    action.start()

                if action is not None:
                    x_y = action.estimate_progress()
                    dt = time.time() - scan_time
                    delta_dxy = Safe_Point3(*(new - old for new, old in zip(x_y[None], last_xy[None])))
                    delta_mag = delta_dxy.magnitude()
                    estimates = (delta_mag, 0, dt)
                    print(estimates)
                    last_xy = x_y
                    scan_time = time.time()
                    if action.complete:
                        action = None
                else:
                    estimates = Safe_Point3()
                navigator.run_components(lidar_data, estimates)
                position = navigator.get_position()
                # current_position[None] = position[None]
                position_queue.put(position)
                # print('saving map')
                if scan_counter > 120:
                    break
            navigator.save_map()
        except Exception as e:
            lidar.set_motor_duty(0)
            raise e


class Locator:
    def __init__(self, lidar):
        self.lidar = lidar

    def locate(self):
        scan = self.get_x_scans(6)
        angle_offset = self.align_angle(scan)
        right_offset = self.align_span(scan, (math.pi / 2) + angle_offset)
        rear_offset = self.align_span(scan , (math.pi) + angle_offset)
        return Safe_Point3((2.438 * 1000) - right_offset, rear_offset, angle_offset)

    def align_span(self, scan, angle_offset):
        return scan[0][self.get_closest_point(scan[1], angle_offset)]

    def align_angle(self, scan):
        right_scan = scan[..., np.logical_and(5 * math.pi / 12 < scan[1], scan[1] < 7 * math.pi / 12)]
        right_angle, *tail = np.polyfit(*self.pol2cart(right_scan[0], right_scan[1]), 1)
        return right_angle



    def get_x_scans(self, x):
        scanner = self.lidar.scanner()
        scan_agg = next(scanner)
        for id, scan in zip(range(x-1), scanner):
            scan_agg = np.concatenate((scan, scan_agg), axis=1)
        return scan_agg[..., scan_agg[0] != 0]

    @staticmethod
    def get_closest_point(array, value):
        return np.argmin(np.abs(array - value))

    @staticmethod
    def pol2cart(rho, phi) -> (np.array, np.array):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return x, y

