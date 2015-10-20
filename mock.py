import navigation_platform
import mobility_platform.mobility
import recovery_platform.recovery
import hardware.lidar
import status_io.client
import simulate.controller
import math
import time


def mock():
    print("mocking")
    # nav = navigation_platform.navigation.Base()
    # nav_control = navigation_platform.controller.Base(nav)
    # rec = recovery_platform.recovery.Base()

    px, py, r = 440, 100, math.radians(270)

    io = status_io.client.IOHandler()
    io.start()

    # generate map
    controller = simulate.controller.Controller()
    controller.init_grid()

    # send the map to the server
    io.send_data(('grid-colors', controller.grid.get_pygame_grid()))
    io.send_data(('robot-pos', (px, py, r)))

    lidar = hardware.lidar.Base(controller)

    st = time.time()

    for i in range(625):
        if not io.halt.value:
            py += 1
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
        # while time.time() - st < 0.1:
        #     pass
        # st = time.time()

    for i in range(45):
        if not io.halt.value:
            r -= math.radians(2)
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
            while time.time() - st < 0.1:
                pass
            st = time.time()

    for i in range(250):
        if not io.halt.value:
            px -= 1
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
            # while time.time() - st < 0.1:
            #     pass
            # st = time.time()

    for i in range(45):
        if not io.halt.value:
            r += math.radians(2)
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
            while time.time() - st < 0.1:
                pass
            st = time.time()

    for i in range(125):
        if not io.halt.value:
            py += 1
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
            # while time.time() - st < 0.1:
            #     pass
            # st = time.time()

    for i in range(45):
        if not io.halt.value:
            r -= math.radians(2)
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
            while time.time() - st < 0.1:
                pass
            st = time.time()

    for i in range(125):
        if not io.halt.value:
            px -= 1
            scan = lidar.scan(py, px, r)
            io.send_data(('robot-pos', (px, py, r)))
            io.send_data(('lidar-points', (px, py, r, scan)))
            # while time.time() - st < 0.1:
            #     pass
            # st = time.time()

    io.stop()

    # io commands
    # io.send_data(('grid-colors', controller.grid.get_pygame_grid())) // sends grid to server
    # io.send_data(('robot-pos', (px, py, r))) // positions robot at px, py with rotation r on server (r in radians)



    # px, py, r = 480, 480, math.radians(180)
    # io.send_data(('robot-pos', (px, py, r)))

    # if aquire:
    # nav_control.add_component(rec.aquire_align)
    # do mobility_platform events
    # magical_fsm
