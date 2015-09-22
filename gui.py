from PySide import QtGui, QtCore


class Gui(QtGui.QWidget):
    def __init__(self, grid=None, plot=None, condition=None):
        super(Gui, self).__init__()
        self.grid = grid
        self.plot = plot
        self.condition = condition
        self.gridImg = False
        self.initUI()

    def initUI(self):
        if self.plot is not None:
            qImg = QtGui.QImage(self.plot.getMap().flatten(), self.plot.getMap().shape[1], self.plot.getMap().shape[0], QtGui.QImage.Format_RGB32)
            self.gridImg = QtGui.QPixmap.fromImage(qImg)
            self.gridImg = self.gridImg.scaled(1000, 1000, QtCore.Qt.KeepAspectRatio)

        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle('Output')
        self.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_A:
            if self.grid is not None:
                self.grid.addToQueue('sample')
                with self.condition:
                    self.condition.wait()
                    print('samples:', self.grid.getSamples())
                    print('graph', self.plot.addToQueue(['hits', self.grid.getSamples()]))

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.grid is not None:
            self.drawGrid(event, qp)
        qp.end()

    def drawGrid(self, event, qp):
        qp.drawPixmap(0, 0, self.gridImg)
