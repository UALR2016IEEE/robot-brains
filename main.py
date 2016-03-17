import sys

import numpy as np
import json

from navigation_platform.controller import Controller as NavControl
from navigation_platform.navigation import Navigation as Navigation
from mobility_platform.mobility import Mobility
from controller import Controller


def main(render):
    with open('config.json', 'r') as f:
        config = json.load(f)

    nav = NavControl(Navigation, None, render)
    #nav.start()
    mob = Mobility(profile=config['robot characteristics'])
    controller = Controller(nav, mob)
    controller.start()


if __name__ == "__main__":
    args = sys.argv
    print('args', args)

    np.set_printoptions(threshold=99999999, linewidth=9999999, suppress=True)

    if len(args) > 0:

        arg_mock = 'mock' in args
        arg_render = 'render' in args

        if arg_mock:
            import mock

            mock.mock(render=arg_render)
        else:
            main(arg_render)
