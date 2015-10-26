import json

import navigation_platform
from mobility_platform.mobility import Base as Mobility
from navigation_platform.controller import Base as NavControl
from navigation_platform.navigation import Base as Navigation
from controller import Controller
import hardware.lidar
import status_io.client
import simulate.controller
import math
from utils.data_structures import Point3


def mock():
    mode = 'kori'
    print('mocking mode', mode)

    position = Point3(100, 440, math.radians(270))

    if mode == 'kori':
        with open('config.json', 'r') as f:
            config = json.load(f)

        sim_controller = simulate.controller.Controller(position)
        sim_controller.init_grid()

        nav = NavControl(Navigation, sim_controller)
        nav.start()
        mob = Mobility(profile=config['robot characteristics'])
        controller = Controller(nav, mob)
        controller.start()
        # do mobility_platform events
        # magical_fsm

    elif mode == 'zach':
        io = status_io.client.IOHandler()
        io.start('localhost', 9998)

        # generate map
        sim_controller = simulate.controller.Controller(position)
        sim_controller.init_grid()

        # send the map to the server
        io.send_data(('grid-colors', sim_controller.grid.get_pygame_grid()))
        io.send_data(('robot-pos', position))

        lidar = hardware.lidar.Base(sim_controller)

        for i in range(625):
            if not io.halt:
                position.y += 1
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(45):
            if not io.halt:
                position.r -= math.radians(2)
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(250):
            if not io.halt:
                position.x -= 1
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(45):
            if not io.halt:
                position.r += math.radians(2)
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(125):
            if not io.halt:
                position.y += 1
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(45):
            if not io.halt:
                position.r -= math.radians(2)
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(125):
            if not io.halt:
                position.x -= 1
                scan = lidar.scan(position)
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        io.stop()

        # io commands
        # io.send_data(('grid-colors', controller.grid.get_position.ygame_grid())) // sends grid to server
        # io.send_data(('robot-pos', (position))) // positions robot at position.x, position.y with rotation position.r on server (position.r in radians)
        #
        # position = 480, 480, math.radians(180)
        # io.send_data(('robot-pos', (position)))

    else:
        print('mode unsupported')
