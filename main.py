import sys

import numpy as np


def main():
    pass


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
            main()
