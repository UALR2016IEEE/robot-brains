import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import math
import multiprocessing


class Plot(multiprocessing.Process):
    def __init__(self, grid, condition):
        np.set_printoptions(threshold=99999, linewidth=99999, precision=3, suppress=True)
        multiprocessing.Process.__init__(self)
        self.queue = multiprocessing.Queue()
        self.daemon = True
        self.condition = condition
        self.grid = grid
        self.samples = []
        self.imGrid = np.ndarray(shape=grid.shape, dtype=np.uint32)

        self.initGrid()
        process = multiprocessing.Process(target=self.run, args=())
        process.daemon = True  # Daemonize process
        process.start()

    def initGrid(self):
        self.imGrid[self.grid == 0] = 0xff008000
        self.imGrid[self.grid == 1] = 0xff000000
        self.imGrid[self.grid == 2] = 0xff0000A0
        self.imGrid[self.grid == 3] = 0xffA52A2A
        self.imGrid[self.grid == 4] = 0xff0000FF
        self.imGrid[self.grid == 5] = 0xff800080
        self.imGrid[self.grid == 6] = 0xffFF0000
        self.imGrid[self.grid == 7] = 0xffFFFF00
        self.imGrid[self.grid == 10] = 0xffFFFF00
        self.imGrid[self.grid == 11] = 0xffFF0000
        self.imGrid[self.grid == 12] = 0xffC0C0C0

    def run(self):
        print('Grid process running.')
        while True:
            val = self.queue.get()
            print('Plot thread val', val)
            if val is None:  # If you send `None`, the thread will exit.
                return
            if val[0] == 'hits':
                self.samples = self.plotHits(val[1])

    def saveMap(self):
        cmap = mpl.colors.ListedColormap(['green', 'black', 'navy', 'brown', 'blue', 'purple', 'red', 'yellow', 'red', 'yellow', 'yellow', 'red', 'lightgray'])
        plt.clf()
        plt.imshow(self.grid, interpolation="none", cmap=cmap)
        self.__saveImage("tmp.png", plt.gcf())

    def getMap(self):
        return self.imGrid

    def getSamples(self):
        return self.samples

    def addToQueue(self, val):
        self.queue.put(val)

    @staticmethod
    def __saveImage(fileName, fig=None):
        fig.set_size_inches(10, 10)
        a = fig.gca()
        a.set_frame_on(False)
        a.set_xticks([])
        a.set_yticks([])
        plt.axis('off')
        fig.savefig(fileName, transparent=True, bbox_inches='tight', pad_inches=0, dpi=200)

    def plotHits(self, hits):
        cmap = mpl.colors.ListedColormap(['white', 'lightgray', 'red'])
        hits = np.array(hits)
        maxDist = int(np.amax(hits, 0)[0])
        graph = np.zeros(shape=(maxDist * 2 + 1, maxDist * 2 + 1))

        intervals = int(maxDist / 10)

        # draw concentric target circles
        for i in range(1, intervals + 1):
            xx, yy = np.mgrid[:maxDist * 2 + 1, :maxDist * 2 + 1]
            circle = (xx - maxDist) ** 2 + (yy - maxDist) ** 2
            donut = np.logical_and(circle < ((i * 5) ** 2 + (i * 5)), circle > ((i * 5) ** 2 - (i * 5)))
            graph[donut == 1] = 1

        # draw vertical / horizontal rules
        graph[:, maxDist] = 1
        graph[maxDist, :] = 1

        for hit in hits:
            cy, cx = int((math.sin(hit[1]) * hit[0]) + maxDist), int((math.cos(hit[1]) * hit[0]) + maxDist)
            graph[cy][cx] = 2
            
        return graph

