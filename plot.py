import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import math


class Plot:
    def __init__(self, grid):
        np.set_printoptions(threshold=99999, linewidth=99999, precision=3, suppress=True)
        self.grid = grid

    def saveMap(self):
        cmap = mpl.colors.ListedColormap(['green', 'black', 'navy', 'brown', 'blue', 'purple', 'red', 'yellow', 'red', 'yellow', 'yellow', 'red', 'lightgray'])
        plt.clf()
        plt.imshow(self.grid, interpolation="none", cmap=cmap)
        self.__saveImage("tmp.png", plt.gcf())

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

        print('Intervals', intervals)

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

        plt.imshow(graph, interpolation="none", cmap=cmap)
        self.__saveImage("tmp2.png", plt.gcf())
