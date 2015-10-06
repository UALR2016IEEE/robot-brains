import navigation_platform
import mobility_platform.mobility
import recovery_platform.recovery


def mock():
    nav = navigation_platform.navigation.Base()
    nav_control = navigation_platform.controller.Base(nav)
    rec = recovery_platform.recovery.Base()
    # if aquire:
    # nav_control.add_component(rec.aquire_align)
    # do mobility_platform events
    # magical_fsm


