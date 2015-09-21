from PySide import QtGui, QtCore


class Gui(QtGui.QWidget):
    def __init__(self, grid=None):
        super(Gui, self).__init__()
        self.grid = grid
        self.gridImg = False
        self.initUI()

    def initUI(self):
        if self.grid is not None:
            qImg = QtGui.QImage(self.grid.flatten(), self.grid.shape[1], self.grid.shape[0], QtGui.QImage.Format_RGB32)
            self.gridImg = QtGui.QPixmap.fromImage(qImg)
            self.gridImg = self.gridImg.scaled(1000, 1000, QtCore.Qt.KeepAspectRatio)

        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle('Output')
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.grid is not None:
            self.drawGrid(event, qp)
        qp.end()

    def drawGrid(self, event, qp):
        qp.drawPixmap(0, 0, self.gridImg)
