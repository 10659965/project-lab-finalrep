import serial
import numpy as np
import sys
import ctypes
import time

from PyQt5.QtCore import (
    QObject,
    QThreadPool, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QWidget,
    QDialog,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    
)
class WorkerKilled(Exception):
    pass

def convert(int):
            b = 0
            for i in range(0, 10, 1):
                bit = int & 1 << i
                if not bit:
                    b = b | (1 << i)
            b = b+1
            int = b * -1
            return int

class DatiSignals(QObject):

    deviceport=pyqtSignal(str)
    dati=pyqtSignal(list,list,list)
    service_string=pyqtSignal(str)
    conn_status=pyqtSignal(str)



class DatiSerial(QRunnable):
    def __init__(self,portname,chcompare):
        super().__init__()
        '''
        header = 160
        tail = 192
        byte_to_receiv = 194
        '''
        self.serialPort = serial.Serial()
        self.chcompare=str(chcompare)
        self.PortName=str(portname)
        self.acc_vect = []
        self.X = []
        self.Y = []
        self.Z = []
        self.is_killed=False
        self.FlagConnection=False


        self.signals=DatiSignals()

    def Abort(self):
        self.is_killed=True
        self.serialPort.write('b'.encode('utf-8'))
        #self.serialPort.close()
        self.FlagConnection=False
        time.sleep(0.01)

     
    
        

    @pyqtSlot()
    def run(self):
            
        header = 160
        tail = 192
        byte_to_receiv = 194
        sData = []
        stringInit=''
        #print("run")
        self.signals.service_string.emit("run")

            
        try:
            #while(1):
                if self.FlagConnection==False:
                    self.serialPort = serial.Serial(port = self.PortName, baudrate=115200,bytesize=8, timeout=None, stopbits=serial.STOPBITS_ONE)
                    self.checkStringInit()
                    self.FlagConnection=True
                

                #self.signals.service_string.emit("connection estabilished")
                if(self.serialPort.is_open):
                        
                    #self.signals.service_string.emit("something in")
                    sData = self.serialPort.read(194)
                    #print(sData)
                    byte =[]
                        

                    if (sData[0] == header and sData[193] == tail and len(sData) == byte_to_receiv):
                        #print("new valid set of data")
                        byte = [sData[i:i + 2] for i in range(1, len(sData) - 2, 2)]
                        #print(byte)
                    else:
                        self.signals.service_string.emit("condition not satisfied")

                    vect = []

                    for value in byte:
                        sign = value[1] & 0b10000000
                        a = (value[0] | value[1] << 8) >> 6
                        if sign:
                            a = convert(a)
                        vect.append(a)

                    for i in range (0,len(vect),3):
                        self.X.append(vect[i])
                        self.Y.append(vect[i+1])
                        self.Z.append(vect[i+2])

                    if self.is_killed==True:
                        #self.signals.service_string.emit("killed(?)")
                        raise WorkerKilled

                    self.acc_vect.append(vect)
                    self.signals.service_string.emit("vector ready")
                    self.signals.dati.emit(self.X,self.Y,self.Z)
                    #self.signals.service_string.emit("terminated")
                    
                    # Print the contents of the serial data
                    #l = len(self.Z)
                    #print(self.Z[l-3:l])
                    #print(l)
                        
                    
                    
                        

                    time.sleep(0.05)
                    self.run()
                    
                        
                        


        except WorkerKilled:
            self.signals.service_string.emit("killed")
            self.serialPort.close()
            time.sleep(0.05)

    def checkStringInit(self):
        stringInit=str(self.serialPort.read(7))
        self.signals.service_string.emit(stringInit)
        if self.chcompare in stringInit:
            self.serialPort.write('a'.encode('utf-8'))
            self.signals.service_string.emit("WROTE") 
             
                
    

