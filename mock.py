import navigation_platform
import mobility_platform.mobility
import recovery_platform.recovery
import status_io.client
import simulate.controller
import math
import time


def mock():
    print("mocking")
    # nav = navigation_platform.navigation.Base()
    # nav_control = navigation_platform.controller.Base(nav)
    # rec = recovery_platform.recovery.Base()
    io = status_io.client.IOHandler()
    io.start()

    # generate map
    controller = simulate.controller.Controller()
    controller.init_grid()

    # io commands
    # io.send_data(('grid-colors', controller.grid.get_pygame_grid())) // sends grid to server
    # io.send_data(('robot-pos', (px, py, r))) // positions robot at px, py with rotation r on server (r in radians)

    # send the map to the server
    io.send_data(('grid-colors', controller.grid.get_pygame_grid()))

    px, py, r = 480, 480, math.radians(180)
    io.send_data(('robot-pos', (px, py, r)))

    # if aquire:
    # nav_control.add_component(rec.aquire_align)
    # do mobility_platform events
    # magical_fsm
