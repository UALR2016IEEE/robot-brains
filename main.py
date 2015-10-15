import sys


def main():
    pass


if __name__ == "__main__":
    args = sys.argv
    print('args', args)
    if len(args) > 0:
        if 'mock' in args:
            import mock
            mock.mock()
        else:
            main()
