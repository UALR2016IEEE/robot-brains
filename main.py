__author__ = 'StaticVOiDance'
import sys

def main():
    pass


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 0:
        if args[0] == 'mock':
            import mock
            mock.mock()
        else:
            main()


