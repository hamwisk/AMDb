# ui/splash.py
import os

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication

from ui.ui_splash import Ui_SplashScreen


class Splash(QMainWindow):
    def __init__(self, version_number, parent=None):
        super().__init__(parent)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)
        self.setWindowTitle("Andy's Movie Database")

        # Set the version number from the passed parameter
        self.ui.version_number.setText(str(version_number))

        # Set the window flag to stay on top
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        splash_path = os.path.expanduser("~/.local/share/amdb/assets/splash.png")
        self.ui.splash_image.setPixmap(QtGui.QPixmap(splash_path))

        self.show()
        self.center()

    def center(self):
        # Center the window on the screen
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
