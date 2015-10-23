import navigation_platform
import mobility_platform.mobility
import recovery_platform.recovery
import hardware.lidar
import status_io.client
import simulate.controller
import math
import time
from utils.data_structures import Point3


def mock():
    print("mocking")
    # nav = navigation_platform.navigation.Base()
    # nav_control = navigation_platform.controller.Base(nav)
    # rec = recovery_platform.recovery.Base()

    position = Point3(100, 440, math.radians(270))

    io = status_io.client.IOHandler()
    io.start('localhost', 9998)

    # generate map
    controller = simulate.controller.Controller()
    controller.init_grid()

    # send the map to the server
    io.send_data(('grid-colors', controller.grid.get_pygame_grid()))
    io.send_data(('robot-pos', position))

    lidar = hardware.lidar.Base(controller)

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

    # position = 480, 480, math.radians(180)
    # io.send_data(('robot-pos', (position)))

    # if acquire:
    # nav_control.add_component(rec.acquire_align)
    # do mobility_platform events
    # magical_fsm
