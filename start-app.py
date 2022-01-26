#!/usr/bin/env python3

from qt_application import Window
import sys
from PyQt5 import QtWidgets as QW


if __name__ == '__main__':
    App = QW.QApplication(sys.argv)

    # create the instance of our Window
    window = Window()
    window.show()

    # start the app
    sys.exit(App.exec())

