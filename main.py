import argparse
import grid
import plot
import sys
import gui
from PySide import QtGui
import multiprocessing


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
        condition = multiprocessing.Condition()
        g = grid.Grid(condition)
        p = plot.Plot(g.getGrid(), condition)

        gu = gui.Gui(grid=g, plot=p, condition=condition)

        sys.exit(app.exec_())

    if args.server:
        print("Hosting web server at http://localhost:8080")

if __name__ == "__main__":
    main()
