import argparse
import plot as plot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="run using mock sensors and map", action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-s", "--server", help="host output to web server", action="store_true")
    parser.add_argument("-p", "--plot", help="use matplotlib to show output", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        print("Using verbose output")
    if args.test:
        print("Using mock sensors and map")
    if args.server:
        print("Hosting web server at http://localhost:8080")
    if args.plot:
        print("Plotting output to matplotlib")
        p = plot.Plot()
        p.saveMap()

if __name__ == "__main__":
    main()
