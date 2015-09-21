import argparse
import grid
import plot
import sys
import gui
import threading
from PySide import QtGui


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="run using mock sensors and map", action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-s", "--server", help="host output to web server", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print("Using verbose output")
    if args.test:
        print("Using mock sensors and map")

        app = QtGui.QApplication(sys.argv)

        g = grid.Grid(mock=True)
        p = plot.Plot(g.getGrid())

        gu = gui.Gui(grid=p.getMap())

        print('hitting')
        # hits = np.ndarray(shape=(0, 2))
        # for i in range(100):
        #     hits = np.concatenate((hits, g.getRadialDistances(50, 50, 0, math.radians(360), math.radians(10))))

        print('done hitting')

        sys.exit(app.exec_())

    if args.server:
        print("Hosting web server at http://localhost:8080")

if __name__ == "__main__":
    main()
