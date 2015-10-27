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


def mm2pix(mm):
    return int(mm / (2.4384 * 2000. / 960))


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

        from breezyslam.algorithms import RMHC_SLAM
        from breezyslam.components import Laser
        from PIL import Image

        io = status_io.client.IOHandler()
        io.start('localhost', 9998)

        # generate map
        sim_controller = simulate.controller.Controller(position)
        sim_controller.init_grid()

        # send the map to the server
        io.send_data(('grid-colors', sim_controller.grid.get_pygame_grid()))
        io.send_data(('robot-pos', position))

        lidar = hardware.lidar.Base(sim_controller)

        laser = Laser(360, 5.5, 360, 6000, 70)

        mapbytes = bytearray(960 * 960)

        slam = RMHC_SLAM(laser, 960, 2.4384 * 2)

        trajectory = []

        for i in range(625):
            if not io.halt:
                position.y += 1
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (2.54, 0, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(45):
            if not io.halt:
                position.r -= math.radians(2)
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (0, -2, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(250):
            if not io.halt:
                position.x -= 1
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (2.54, 0, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(45):
            if not io.halt:
                position.r += math.radians(2)
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (0, 2, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(125):
            if not io.halt:
                position.y += 1
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (2.54, 0, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(45):
            if not io.halt:
                position.r -= math.radians(2)
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (0, -2, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        for i in range(125):
            if not io.halt:
                position.x -= 1
                scan = lidar.scan(position)
                slam.update((scan[:, 0] * 2.54).tolist(), (2.54, 0, 0.1))
                x, y, theta = slam.getpos()
                trajectory.append((x, y))
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        io.stop()

        # Create a byte array to receive the computed maps
        mapbytes = bytearray(960 * 960)

        # Get final map
        slam.getmap(mapbytes)

        # Put trajectory into map as black pixels
        for coords in trajectory:
            x_mm, y_mm = coords

            x_pix = mm2pix(x_mm)
            y_pix = mm2pix(y_mm)

            mapbytes[y_pix * 960 + x_pix] = 0

        # Save map and trajectory as PNG file
        image = Image.frombuffer('L', (960, 960), mapbytes, 'raw', 'L', 0, 1)
        image = image.rotate(270)

        image.save('test_image.png')

        # io commands
        # io.send_data(('grid-colors', controller.grid.get_position.ygame_grid())) // sends grid to server
        # io.send_data(('robot-pos', (position))) // positions robot at position.x, position.y with rotation position.r on server (position.r in radians)
        #
        # position = 480, 480, math.radians(180)
        # io.send_data(('robot-pos', (position)))

    else:
        print('mode unsupported')
