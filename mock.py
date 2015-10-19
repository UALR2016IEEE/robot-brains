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

    # send the map to the server
    io.send_data(('grid-colors', controller.grid.get_pygame_grid()))

    for i in range(0, 722, 2):
        io.send_data(('robot-pos', (480, 480, math.radians(i % 360))))
        time.sleep(0.05)

    # if aquire:
    # nav_control.add_component(rec.aquire_align)
    # do mobility_platform events
    # magical_fsm
