# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 10:53:03 2021

@author: lucas
"""
# importing libraries
from PyQt5 import QtWidgets as QW 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import * 
import sys
import serial
import time
import serial.tools.list_ports
import time
 
 
class Arduino():
    def __init__(self):
        self.functional = False
        self.shutter_one_open = False
        self.shutter_two_open = False
        self.shutter_three_open = False
        # self.connect()
 
    def __del__(self):
        self.disconnect()
        
    def askIfPortIsCorrect(self, port): #port which is being asked must by closed!
        is_correct = False
        try:
            ser = serial.Serial(port, baudrate=9600, timeout=0.1)
            ser.write(b"OO\n")
            ser.flush()
            # time.sleep(0.5)
            tmp = str(ser.readline())
            ser.close()
            is_correct = True
            print(tmp,'\n')
            if("SHUTTERDRIVER" in tmp):
                is_correct = True
                print('ok')
        except:
            return False
        return is_correct       

    def connect(self):
        if(self.functional == True):
            self.disconnect()
        found = False
        try:
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                print(port, desc, hwid)
            for port, desc, hwid in sorted(ports):
                if(self.askIfPortIsCorrect(port)):
                    if  "2341" in hwid:
                        found = True
                        self.port = port
                        self.hwid = hwid
                        print("Found Arduino {}: {} [{}]".format(port, desc, hwid))  
                        self.ser = serial.Serial(port, timeout=0.1)  # open serial port
                        # break
            if(found == False):
                print("Error! Can't find Arduino module to control shutters!")
        except:
            self.functional = False
            return False
        self.functional = found
        return found
    
    def disconnect(self):
        self.closeShutter(1)
        self.closeShutter(2)
        try:
            self.ser.close()
        except:
            self.functional = False
        self.functional = False
        self.ser = None

    def sendCommand(self, command):
        val = False
        try:
            self.ser.write(command)
            self.ser.flush()
            # time.sleep(0.1)
            while(self.ser.in_waiting > 0):
                val = self.ser.readline()
        except:
            self.functional = False
            return False
        return int(val)
        
    def closeShutter(self, shutter_no): #maybe add "fast version" of this function?
        if(self.functional == False):
            return False
        elif(shutter_no == 1):
            val = self.sendCommand(b'OFF1\n')
            if val == 0:
                self.shutter_one_open = False             
        elif(shutter_no == 2):
            val = self.sendCommand(b'OFF2\n')
            if val == 0:
                self.shutter_two_open = False
        elif(shutter_no == 3):
            val = self.sendCommand(b'OFF3\n')
            if val == 0:
                self.shutter_three_open = False
        else:
            return False
        
    def openShutter(self, shutter_no):
        if(self.functional == False):
            return False
        elif(shutter_no == 1):
            val = self.sendCommand(b'ON1\n')
            if val == 90:
                self.shutter_one_open = True
        elif(shutter_no == 2):
            val = self.sendCommand(b'ON2\n')
            if val == 90:
                self.shutter_two_open = True
        elif(shutter_no == 3):
            val = self.sendCommand(b'ON3\n')
            if val == 90:
                self.shutter_three_open = True
        else:
            return False


class VLayout(QW.QVBoxLayout):
    def __init__(self, parent=None):
        super(VLayout, self).__init__(parent)
        self.added_widgets = []
    
    def addSeveralWidgets(self, lista):
        for i in lista:
            if type(i) is list:
                self.addWidget(i[0], *i[1:])
            else:
                self.addWidget(i)
    
    def addWidget(self, a0, *args):
        super().addWidget(a0, *args)
        self.added_widgets.append(a0)
        
    def hide_all(self):
        for i in self.added_widgets:
            i.setVisible(False)
    
    def show_all(self):
        for i in self.added_widgets:
            i.show()


class HLayout(QW.QHBoxLayout):
    def __init__(self, parent=None):
        super(HLayout, self).__init__(parent)
        self.added_widgets = []
    
    def addSeveralWidgets(self, lista):
        for i in lista:
            if type(i) is list:
                self.addWidget(i[0], *i[1:])
            else:
                self.addWidget(i)
    
    def addWidget(self, a0, *args):
        super().addWidget(a0, *args)
        self.added_widgets.append(a0)
        
    def hide_all(self):
        for i in self.added_widgets:
            i.setVisible(False)
    
    def show_all(self):
        for i in self.added_widgets:
            i.show()



class spinBox(QW.QWidget):
    def __init__(self, label, mini, maxi, step=1, tooltip=None, parent=None):
        super(spinBox, self).__init__(parent)
        self.layout = HLayout(self)
        self.label =  QW.QLabel(label)
        self.spin = QW.QSpinBox()
        self.spin.setMinimum(mini)
        self.spin.setMaximum(maxi)
        self.spin.setSingleStep(step) 
        self.layout.addWidget(self.spin)
        self.layout.addWidget(self.label)
        if tooltip is not None:
            QW.QToolTip.setFont(QFont('SansSerif', 10))
            self.setToolTip(tooltip)
            self.spin.setToolTip(tooltip)
   
    @property
    def value(self):
        return self.spin.value()
    
    @value.setter
    def value(self, value):
        return self.spin.setValue(value)
    
    def valueChangedConnect(self, fucnt):
        self.spin.valueChanged.connect(fucnt)


class GenericWorker(QObject):

    start = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        super(GenericWorker, self).__init__()
#        logthread('GenericWorker.__init__')
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start.connect(self.run)
        self.isRunning=False
    
    start = pyqtSignal(str)
    @pyqtSlot()
    def run(self):
        print('start')
        self.isRunning=True
        self.function()
        self.finished.emit()
        self.isRunning=False


class modeWidget(QW.QWidget):
    """"
    Similar to a combo box; but allows to enter some parameters
    """
    def __init__(self, actions, tooltip=None, parent=None): 
        super(modeWidget, self).__init__(parent)
        self.layout = QW.QHBoxLayout(self)
        self.mode = comboBox(actions=actions)
        self.input = QW.QLineEdit() 
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.mode)
        if tooltip is not None:
            QW.QToolTip.setFont(QFont('SansSerif', 10))
            self.setToolTip(tooltip)    
            self.input.setToolTip(tooltip)
    
    @property
    def currentMode(self):
        return self.mode.currentText()
    
    @property
    def inputValue(self):
         text = self.input.text() 
         numeric = False
         try:
             float(text)
             numeric = True
         except:
             return text
         finally:
             if numeric:
                 if text.isdigit():
                     return int(text)
                 else:
                     return float(text)
             else:
                 pass


class comboBox(QW.QComboBox):
    def __init__(self, actions, parent=None):
        super(comboBox, self).__init__(parent)
        for i in actions:
            self.addItem(i)


class ProgressBar(QW.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.progressBar = QW.QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        

class Slider(QW.QSlider):
    def __init__(self, minimum, maximum, initial_value,
                 orientation, parent=None):      
        super().__init__(orientation)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(initial_value)
        self._eneable_drag = True
        
    def setEnable(self, value: bool):
        self._eneable_drag = value
    
    def sliderMoved(self):
        if self._eneable_drag:
            super().sliderMoved()
        else:
            pass
            
        
class SequenceExplrorer(QW.QWidget):
    def __init__(self, sequence, names: list, parent=None):   
       super().__init__(parent)
       self.sequence = sequence
       self.number_shutters = len(names)
       self.layout = VLayout(self)
       layout = VLayout(self)
       hlayout = HLayout(self)
       self.status = [QW.QCheckBox(names[i] + ' status')
                      for i in range(self.number_shutters)]
       for i in  range(self.number_shutters):
           self.status[i].setCheckState(2)
           layout.addWidget(self.status[i])
       self.step_number = QW.QLabel('Step number 1')
       self.time_display = QW.QLabel('Duration: 0')
       self.slider = Slider(1, self.number_shutters, 1, Qt.Horizontal)
       self.slider.valueChanged.connect(self.moveSlider)
       layout2 = VLayout(self)
       hlayout.addLayout(layout)
       layout2.addWidget(self.step_number)
       layout2.addWidget(self.time_display)
       layout2.setContentsMargins(20, 0, 0 , 0)
       layout.setContentsMargins(0, 0, 0 , 10)
       self.progress = ProgressBar()
       layout2.addWidget(self.progress)
       # layout2.setAlignment(Qt.AlignTop)
       self.progress.setVisible(False)
       hlayout.addLayout(layout2)
       self.layout.addLayout(hlayout)
       self.layout.addWidget(self.slider)
       self.checkSequenceLength()
       self._running = False    

    def moveSlider(self):
        value  = self.slider.value()
        single_step = self.sequence[value][:-1]
        self.setStatusValues(single_step)
        time = self.sequence[value][-1]
        self.step_number.setText(f'Step number: {value}')
        self.time_display.setText(f'duration: {time} s')

    def setSequence(self, sequence):
        self.sequence = sequence
        self.slider.setMaximum(len(sequence))
        self.moveSlider()
    
    def setStatusValues(self, status):
        for ii, check in enumerate(self.status):
            if status[ii]:
                check.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : lightgreen;}")
            else:
                check.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : red;}")
    
    def checkSequenceLength(self):
        if len(self.sequence) == 0:
            self.setVisible(False)


class CThread(QThread):
    valueChanged = pyqtSignal(float)
    def __init__(self,values):
        super().__init__()
        self.stop_fill = False
        self.time_steps = values
        self.completed = False
        self.running_time = 0
        for i in self.time_steps:
            # print('step', i)
            self.running_time += i
        # print(self.time_steps, 'hola')

    def run(self):

        init = time.time()
        # time.sleep(0.5)
        while not self.stop_fill and self.completed < self.running_time:
            self.completed = (time.time() - init)
            self.sleep(0.5) # value set  by try and error
            self.valueChanged.emit(self.completed)
                # print(self.completed)


class SequenceWidget(QW.QWidget):
    def __init__(self,arduino,  number_shutters=2, names=None, parent=None):   
        super().__init__(parent)
        self.layout = VLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.arduino = arduino
        hlayout = HLayout(self)
        layout = VLayout(self)
        layout2 = VLayout(self)
        if names is None:
            names = ["shutter {i}" for i in range(number_shutters)]
        self.n_shutter = [QW.QCheckBox(names[i]) for i in range(number_shutters)]
        for i in  range(number_shutters):
            self.n_shutter[i].setCheckState(2)
            layout.addWidget(self.n_shutter[i])
        # layout.addWidget(QW.QLabel(''))
        tip = 'Time for a single sequence step'
        self.sequence_params = modeWidget(['Seconds', 'Minutes'], tip)
        layout2.addWidget(self.sequence_params)
        button_add = QW.QPushButton("Add to sequence")
        button_add.clicked.connect(self.addPointToSequence)
        button_new = QW.QPushButton("Clear sequence")
        button_new.clicked.connect(self.newSequence)
        button_explorer = QW.QPushButton("Explore sequence")
        button_explorer.clicked.connect(self.exploreSequence)
        layout2.addWidget(button_add)
        layout2.addWidget(button_new)
        hlayout.addLayout(layout)
        hlayout.addLayout(layout2)
        self.layout.addLayout(hlayout)
        self.steps = QW.QLabel('number steps: 0')
        run = QW.QPushButton("Run sequence")
        run.clicked.connect(self.runSequence)
        self.layout.addWidget(button_explorer)
        self.layout.addWidget(run)
        self.layout.addWidget(self.steps)
        self.sequence = {}
        self.number_steps = 0
        self.explorer = SequenceExplrorer( self.sequence, names)
        self.layout.addWidget(self.explorer)
        self._stop_running = True
        self.stop_button =  QW.QPushButton("Stop sequence")
        self.stop_button.clicked.connect(self._stop)
        self.layout.addWidget(self.stop_button)
        self.stop_button.setVisible(False)
        
        self.recording_thread = QThread()
        self.recording_thread.start(QThread.TimeCriticalPriority)
        self.init_time = 0
        self._rate_fill_bar = 10
        
    def addPointToSequence(self):
        if self._stop_running:
            states = self.checkBoxesState()
            time = self.sequence_params.inputValue 
            if type(time) is  float or type(time) is int:
                if self.sequence_params.currentMode == 'Minutes':
                    time *= 60
                states.append(time)
                self.sequence[self.number_steps+1] = states
                self.number_steps += 1
                self._setNumberStep()
                # print(self.sequence)
                succes =True
            else:
                msg = 'Introduce a valid number for time'
                mesage = QW.QMessageBox()
                mesage.setWindowTitle('Error message')
                mesage.setText(msg)
                mesage.exec()
                succes = False
            if succes:
                self.explorer.setSequence(self.sequence)
        else:
            msg = 'Wait until running the sequence is finished'
            mesage = QW.QMessageBox()
            mesage.setWindowTitle('Error message')
            mesage.setText(msg)
            mesage.exec()

    def checkBoxesState(self):
        states = [True if i.checkState() == 2 else False for i in self.n_shutter]
        return states
    
    def newSequence(self):
        self._sequenceFinished()
        self.sequence = {}
        self.number_steps = 0
        self._setNumberStep()
        self.explorer.setVisible(False)
    
    def exploreSequence(self):
        if len(self.sequence) >= 1:
            self.explorer.show()
            self.explorer.moveSlider()
        else:
            msg = 'Please create a sequence first'
            mesage = QW.QMessageBox()
            mesage.setWindowTitle('Error message')
            mesage.setText(msg)
            mesage.exec()
            
    def runSequence(self):
        if len(self.sequence) >= 1:
            self.explorer._running = True
            self._stop_running = False
            self.stop_button.show()
            self.explorer.slider.setEnable(False)
            self.explorer.progress.show()
            self.my_worker = GenericWorker(self._run)
            self.my_worker.moveToThread(self.recording_thread)
            self.my_worker.start.emit("hello")  
            self.my_worker.finished.connect(self._sequenceFinished)
            times = self._getTime()
            # self.explorer.show()
            # self.progressBar.setMaximum(0)
            self.bar_tread = CThread(times)
            self.bar_tread.valueChanged.connect(self._updateProgressBar)
            self.bar_tread.start()
            self.explorer.show()
    
            
        else:
            msg = 'Please create a sequence first'
            mesage = QW.QMessageBox()
            mesage.setWindowTitle('Error message')
            mesage.setText(msg)
            mesage.exec()
    
    def _setProgressBar(self, value):
        self.explorer.progress.progressBar.setMaximum(value)
        self.init_time = time.time()
    
    def _updateProgressBar(self, value):
        value = (time.time() - self.init_time)*self._rate_fill_bar
        self.explorer.progress.progressBar.setValue(value)
        
    def _setNumberStep(self):
        setps = len(self.sequence)
        self.steps.setText(f'number steps: {setps}')
    
    def _getTime(self):
        times = []
        for i in range(len(self.sequence)):
            times.append(self.sequence[i+1][-1])
        return times
    
    def _run(self):
        i = 0
        self.explorer.moveSlider()
        while i < len(self.sequence):
            print(i)
            self.explorer.slider.setValue(i+1)
            self.explorer.moveSlider()
            
            if self._stop_running:
                print('stop')
                break
            self._executeStep(self.sequence[i+1])
            i += 1
            
    def _stop(self):
        self._stop_running = True
        self.bar_tread.stop_fill = True
        
    def _executeStep(self, step):
        # step = self.sequence(i)
        shutters = step[:-1]
        time_step = step[-1]
        self.explorer.moveSlider()
        self._setProgressBar(time_step*self._rate_fill_bar)
        for ii, i in enumerate(shutters):
            if i:
                self.openShutter(ii+1)
            else:
                self.closeShutter(ii+1)
        for i in range(time_step):
            if self._stop_running:
                pass
            else:
                time.sleep(1)
                
    def openShutter(self, number):
        self.arduino.openShutter(number)
        # self.statusShutter(number)
    
    def closeShutter(self, number):
        self.arduino.closeShutter(number)
        # self.statusShutter(number)
        
    def _sequenceFinished(self):
        self._stop()
        self.explorer.slider.setEnable(True)
        self.stop_button.setVisible(False)
        n_shutters = len(self.n_shutter)
        for ii in range(n_shutters):
                self.closeShutter(ii+1)
        self.explorer.setStatusValues([False for i in range(n_shutters)])
        time.sleep(0.5)
        self.explorer.setVisible(False)
        self.explorer._running = False
        self.explorer.progress.setVisible(False)
    

class ShuttersWidget(QW.QWidget):
    def __init__(self, arduino, number_shutters=2, tooltip=None, auto=False, 
                 parent=None):
        super().__init__(parent)

        self.layout = VLayout(self)
        self.arduino = arduino
        self.button_open = QW.QPushButton("Open Shutter")
        self.button_close = QW.QPushButton("Close shutter")

        self.button_open.clicked.connect(self.openShutter)
        self.button_close.clicked.connect(self.closeShutter)
        self.shutter = spinBox("shutter number", 1, number_shutters,
                               tooltip=tooltip)
        self.shutter.valueChangedConnect(self.statusShutter)
        self.status = QW.QCheckBox('Shutter status')
        self.layout.addWidget(self.button_open)
        self.layout.addWidget(self.button_close)
        self.layout.addWidget(self.shutter)
        self.layout.addWidget(self.status)
        self.layout.addLayout(self.layout)
        self.statusShutter(self.shutter.value)
        self.disable_auto_shutter = QW.QCheckBox('Disable automatic shutters')
        self.disable_auto_shutter.setCheckState(2)
        if auto:
            self.disable_auto_shutter.setCheckState(0)
            self.layout.addWidget(self.disable_auto_shutter)
    
    @property
    def autoOn(self):
        if self.disable_auto_shutter.checkState() == 2:
            return False
        else:
            return True
    
    def openShutter(self):
        self.arduino.openShutter(self.shutter.value)
        self.statusShutter(self.shutter.value)
    
    def closeShutter(self):
        self.arduino.closeShutter(self.shutter.value)
        self.statusShutter(self.shutter.value)
    
    def statusShutter(self, value):
        if value == 1:
            if self.arduino.shutter_one_open:
                self.status.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : lightgreen;}")
            else:
                self.status.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : red;}")
        if value == 2:
            if self.arduino.shutter_two_open:
                self.status.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : lightgreen;}")
            else:
                self.status.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : red;}")
                
        if value == 3:
            if self.arduino.shutter_three_open:
                self.status.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : lightgreen;}")
            else:
                self.status.setStyleSheet("QCheckBox::indicator"
                                          "{background-color : red;}")
    
    def _hide(self):
        self.layout.hide_all()
    
    def _show(self):
        self.layout.show_all()
        self.checkConnect()
             
    
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
        tip ="<nobr>Shutter 1: <b>488 nm laser</b></nobr><br/>" \
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
        self.sequence_widget = SequenceWidget(self.arduino, self.number_shutters, 
                                              names, self)
        
        self.layout.addWidget(self.sequence_widget)
        self.layout.addWidget(self.shutter_widget)
        self.label_not_connected =  QW.QLabel("shutters are disconnected")
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
                msg = "Error! Can't find Arduino module to control shutters!."\
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
  
# #         
            
  
  
  
# create pyqt5 app
App = QW.QApplication(sys.argv)
  
# create the instance of our Window
window = Window()
window.show()
  
# start the app
sys.exit(App.exec())