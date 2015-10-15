import navigation_platform
import mobility_platform.mobility
import recovery_platform.recovery
import status_io.client


def mock():
    print("mocking")
    # nav = navigation_platform.navigation.Base()
    # nav_control = navigation_platform.controller.Base(nav)
    # rec = recovery_platform.recovery.Base()
    io = status_io.client.IOHandler()
    io.start()

    for i in range(10):
        io.send_data((i, i * i))

    # if aquire:
    # nav_control.add_component(rec.aquire_align)
    # do mobility_platform events
    # magical_fsm
