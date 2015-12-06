import json
from mobility_platform.mobility import Base as Mobility
from navigation_platform.controller import Base as NavControl
from navigation_platform.navigation import Base as Navigation
from controller import Controller
import hardware.lidar
import status_io.client
import simulate.controller
import math
from utils.data_structures import Point3


# grid is 960 x 960 (96 inches, 2438 mm)
def mm2pix(mm):
    return int(mm / (2.5 * 1000. / 960))


def mock(render=False):
    mode = 'ltest'
    print('mocking mode', mode)

    position = Point3(100, 440, math.radians(270))

    if mode == 'ltest':
        if render:
            io = status_io.client.IOHandler()
            io.start('localhost', 9998)

        # generate map
        sim_controller = simulate.controller.Controller(position)
        sim_controller.init_grid()

        # tell the renderer that we want to render a lidar test
        if render:
            io.send_data(('lidar-test', None))

        # get a lidar object with the simulated grid
        lidar = hardware.lidar.Base(sim_controller)

        for i in range(625):
            position.y += 1
            # scan returns a list of points in [[scan distances], [scan angle], [scan quality]]
            scan = lidar.scan(position)
            if render:
                # send the test points to the renderer for rendering
                io.send_data(('lidar-test-points', scan))

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
        from PIL import Image

        if render:
            io = status_io.client.IOHandler()
            io.start('localhost', 9998)

        # generate map
        sim_controller = simulate.controller.Controller(position)
        sim_controller.init_grid()

        # send the map to the server
        if render:
            io.send_data(('full-simulation', None))
            io.send_data(('grid-colors', sim_controller.grid.get_pygame_grid()))
            io.send_data(('robot-pos', position))

        lidar = hardware.lidar.Base(sim_controller)
        laser = lidar.get_laser()
        slam = RMHC_SLAM(laser, 960, 2.5, map_quality=10, sigma_xy_mm=100, sigma_theta_degrees=20, max_search_iter=1000, init_x=position.x / 960, init_y=position.y / 960, init_r=90, hole_width_mm=100)

        trajectory = []

        print('step 1/7')

        for i in range(625):
            position.y += 1
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (2.54, 0, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        print('step 2/7')

        for i in range(45):
            position.r -= math.radians(2)
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (0, -2, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        print('step 3/7')

        for i in range(250):
            position.x -= 1
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (2.54, 0, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        print('step 4/7')

        for i in range(45):
            position.r += math.radians(2)
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (0, 2, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        print('step 5/7')

        for i in range(125):
            position.y += 1
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (2.54, 0, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        print('step 6/7')

        for i in range(45):
            position.r -= math.radians(2)
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (0, -2, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        print('step 7/7')

        for i in range(125):
            position.x -= 1
            scan = lidar.scan(position)
            slam.update((scan[0, :]).tolist(), (2.54, 0, 0.1))
            x, y, theta = slam.getpos()
            print('x', x / 2.54, '\ty', y / 2.54, '\ttheta', theta, '\tpos', position)
            trajectory.append((x, y))
            if render:
                io.send_data(('robot-pos', position))
                io.send_data(('lidar-points', (position, scan)))

        if render:
            io.stop()

        print('saving map to image')

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

        image.save('test_image_mock.png')

        # io commands
        # io.send_data(('grid-colors', controller.grid.get_position.ygame_grid())) // sends grid to server
        # io.send_data(('robot-pos', (position))) // positions robot at position.x, position.y with rotation position.r on server (position.r in radians)
        #
        # position = 480, 480, math.radians(180)
        # io.send_data(('robot-pos', (position)))

    else:
        print('mode unsupported')
