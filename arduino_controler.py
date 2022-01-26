import serial
import serial.tools.list_ports


class Arduino:
    """
    The class that send signals to the arduino
    """
    def __init__(self):
        self.functional = False
        self.shutter_one_open = False
        self.shutter_two_open = False
        self.shutter_three_open = False
        # self.connect()

    def __del__(self):
        self.disconnect()

    def askIfPortIsCorrect(self, port):  # port which is being asked must by closed!
        is_correct = False
        try:
            ser = serial.Serial(port, baudrate=9600, timeout=0.1)
            ser.write(b"OO\n")
            ser.flush()
            # time.sleep(0.5)
            tmp = str(ser.readline())
            ser.close()
            is_correct = True
            print(tmp, '\n')
            if "SHUTTERDRIVER" in tmp:
                is_correct = True
                print('ok')
        except:
            return False
        return is_correct

    def connect(self):
        if self.functional == True:
            self.disconnect()
        found = False
        try:
            ports = serial.tools.list_ports.comports()
            for port, desc, hwid in sorted(ports):
                print(port, desc, hwid)
            for port, desc, hwid in sorted(ports):
                if self.askIfPortIsCorrect(port):
                    if  "2341" in hwid:
                        found = True
                        self.port = port
                        self.hwid = hwid
                        print("Found Arduino {}: {} [{}]".format(port, desc, hwid))
                        self.ser = serial.Serial(port, timeout=0.1)  # open serial port
                        # break
            if found == False:
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
            while self.ser.in_waiting > 0:
                val = self.ser.readline()
        except:
            self.functional = False
            return False
        return int(val)

    def closeShutter(self, shutter_no):  # maybe add "fast version" of this function?
        if self.functional == False:
            return False
        elif shutter_no == 1:
            val = self.sendCommand(b'OFF1\n')
            if val == 0:
                self.shutter_one_open = False
        elif shutter_no == 2:
            val = self.sendCommand(b'OFF2\n')
            if val == 0:
                self.shutter_two_open = False
        elif shutter_no == 3:
            val = self.sendCommand(b'OFF3\n')
            if val == 0:
                self.shutter_three_open = False
        else:
            return False

    def openShutter(self, shutter_no):
        if self.functional == False:
            return False
        elif shutter_no == 1:
            val = self.sendCommand(b'ON1\n')
            if val == 90:
                self.shutter_one_open = True
        elif shutter_no == 2:
            val = self.sendCommand(b'ON2\n')
            if val == 90:
                self.shutter_two_open = True
        elif shutter_no == 3:
            val = self.sendCommand(b'ON3\n')
            if val == 90:
                self.shutter_three_open = True
        else:
            return False