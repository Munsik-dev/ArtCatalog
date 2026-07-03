import sys 
from PyQt5  import QtCore, QtGui, QtWidgets
from beta3 import *
from AddWindow import *


class AddWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.ui = Ui_Adding()
        self.ui.setupUi(self)

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self,parent)
        self.ui = Ui_ArtCatalog()
        self.ui.setupUi(self)
        self.add_window = None
        self.ui.pushButton.clicked.connect(self.open_add_window)
    
    def open_add_window(self):
        if self.add_window is None:
            self.add_window = AddWindow()
            self.add_window.show()
        else:
            self.add_window.show()
        self.add_window.raise_()
        self.add_window.activateWindow()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())