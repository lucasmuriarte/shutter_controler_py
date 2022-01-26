from extra_widget import *
from arduino_controler import Arduino
from PyQt5 import QtWidgets as QW


class Window(QW.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python ")
        self.arduino = Arduino()
        # setting title
        self._main = QW.QWidget()
        self.number_shutters = 3

        self.button_connect = QW.QPushButton("Connect/Disconnect")
        self.button_secuence = QW.QPushButton("Sequence")
        self.button_secuence.clicked.connect(self._sequenceLayout)
        self.button_connect.clicked.connect(self.connectDisconnect)
        tip = "<nobr>Shutter 1: <b>488 nm laser</b></nobr><br/>" \
              " <nobr>Shutter 2: <b>405 nm laser</b></nobr><br/>" \
              " <nobr>Shutter 3: <b>976 nm laser</b></nobr><br/>"
        self.layout = QW.QVBoxLayout(self._main)
        self.layout.addWidget(self.button_connect)
        self.layout.addWidget(self.button_secuence)
        self.setCentralWidget(self._main)

        self.shutter_widget = ShuttersWidget(self.arduino,
                                             self.number_shutters,
                                             tip, True, parent=self)

        names = ['488 nm laser', '405 nm laser', '976 nm laser']
        self.sequence_widget = SequenceWidget(self.arduino,
                                              self.number_shutters,
                                              names, self)

        self.layout.addWidget(self.sequence_widget)
        self.layout.addWidget(self.shutter_widget)
        self.label_not_connected = QW.QLabel("shutters are disconnected")
        self.layout.addWidget(self.label_not_connected)
        self.shutter_widget.setVisible(False)
        self.sequence_widget.setVisible(False)
        self.checkConnect()

    def checkConnect(self):
        if self.arduino.functional:
            self.button_connect.setText("Disconnect")
            self.shutter_widget.show()
            self.shutter_widget.statusShutter(
                self.shutter_widget.shutter.value)
            self.label_not_connected.setVisible(False)
            self.button_secuence.show()
            print(self.size())
        else:
            self.button_connect.setText("Connect")
            self.shutter_widget.setVisible(False)
            self.sequence_widget.setVisible(False)
            self.button_secuence.setText('Sequence')
            self.button_secuence.setVisible(False)
            self.label_not_connected.show()

    def connectDisconnect(self):
        if self.button_connect.text() == "Disconnect":
            self.arduino.disconnect()
            self.checkConnect()
        else:
            self.arduino.connect()
            if not self.arduino.functional:
                title = "Shutters not found"
                msg = "Error! Can't find Arduino module to control shutters!." \
                      "\nTry to connect reconnec the USB connector"
                mesage = QW.QMessageBox()
                mesage.setWindowTitle(title)
                mesage.setText(msg)
                mesage.exec()
            else:
                time.sleep(0.5)
                self.checkConnect()

    def _sequenceLayout(self):
        if self.button_secuence.text() == 'Sequence':
            self._sequenceShow()
        else:
            self._sequenceHide()

    def _sequenceShow(self):
        self.button_secuence.setText('Return')
        self.shutter_widget.setVisible(False)
        self.sequence_widget.show()
        # self.resize(self.width(), self.minimumHeight())

    def _sequenceHide(self):
        self.button_secuence.setText('Sequence')
        self.sequence_widget.setVisible(False)
        self.shutter_widget.show()
        # self.label_not_connected.setVisible(False)
        self.resize(self.minimumSizeHint())
