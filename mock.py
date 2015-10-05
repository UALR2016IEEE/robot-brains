__author__ = 'StaticVOiDance'

import navigation_platform
import mobility_platform
import recovery_platform

def mock():
    nav = navigation_platform._BaseNavigation()
    nav_control = navigation_platform._BaseController(nav)
    rec = recovery_platform._Base()
    if aquire:
        nav_control.add_component(rec.aquire_align)
    do mobility_platform events
    magical_fsm


