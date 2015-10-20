import sys
import numpy as np


def main():
    pass


if __name__ == "__main__":
    args = sys.argv
    print('args', args)

    np.set_printoptions(threshold=99999999, linewidth=9999999, suppress=True)

    if len(args) > 0:
        if 'mock' in args:
            import mock
            mock.mock()
        else:
            main()
