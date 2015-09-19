import numpy as np
import matplotlib.pyplot as plt


class Plot:
    def __init__(self):
        self.grid = np.loadtxt("field.csv", delimiter=",")

    def saveMap(self):
        plt.imshow(self.grid)
        self.__saveImage("tmp.png", plt.gcf())

    @staticmethod
    def __saveImage(fileName, fig=None):
        fig.patch.set_alpha(0)
        a = fig.gca()
        a.set_frame_on(False)
        a.set_xticks([])
        a.set_yticks([])
        plt.axis('off')
        plt.xlim(0, 95)
        plt.ylim(95, 0)
        fig.savefig(fileName, transparent=True, bbox_inches='tight', pad_inches=0)
