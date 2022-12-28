import sys
import time
import logging
#from serial import Serial
import serial
import serial.tools.list_ports
#import libraries
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

STATO=0

BAUDRATE=115200

HEIGHT_M=300
WIDTH_M=300
class SignalSearch(QObject):
    portname=pyqtSignal(str)

class BT_search(QWidget):
    def __init__(self,str_compare):
        super().__init__()
        
        
        

        self.connectionFlag=0

        #self.setWindowTitle("Scan BT Devices")
        #self.MainWindowSize=[HEIGHT_M,WIDTH_M]
        #self.setMinimumSize(self.MainWindowSize[0],self.MainWindowSize[1])
        self.butt_bt=QPushButton("Search for device")
        self.butt_bt.setMinimumSize(100,100)
        #self.butt_bt.setMaximumSize(300,150)
        self.stato=0

        self.label_status=QLabel()
        self.listCom=[]
        self.baud=BAUDRATE
        self.s=serial.Serial()
        self.butt_bt.pressed.connect(self.ScanCom)
        self.portName=0
        

        self.chreceived=''
        self.chserial=''
        self.ch_compare=str(str_compare)

        self.signalport=SignalSearch()
        #SearcCom()
        self.visual()
        

    def ScanCom(self):
        #global STATO
        self.stato="SEARCHING"
        self.ChangeStatus(self.stato)
        listCom=[]
        
        for x in serial.tools.list_ports.comports():
            listCom.append(str(x.name))
        print(listCom)
        
        self.SearchCom(listCom)
        

    def SearchCom(self,list):
        
        #global STATO
        
        

        try:
            if self.connectionFlag ==0:
                for xc in list:
                    self.s=serial.Serial(xc,self.baud,write_timeout=0, timeout=10)
                    if self.s.is_open and self.connectionFlag==0:
                        print(xc)
                        self.chreceived=self.s.read(7)
                        print(str(self.chreceived))

                        if self.ch_compare in str(self.chreceived):
                            print("connection estabilished")
                            self.stato='CONNECTED'
                            self.ChangeStatus(self.stato+':'+xc)
                            self.connectionFlag=1
                            self.butt_bt.setDisabled(True)
                            self.portName=xc
                            self.s.close()
                            self.signalport.portname.emit(xc)

                            
                        



        except serial.SerialException:
            if self.connectionFlag==0:    
                self.displayerrorport(xc)
                self.ChangeStatus('ERROR CONNECTION')
                
            


         
    def ChangeStatus(self, status):
        self.label_status.setText(str(status))
        


    def visual(self):
        button_hlay = QHBoxLayout()
        button_hlay.addWidget(self.butt_bt)
        #self.setCentralWidget(self.butt_bt)
        button_hlay.addWidget(self.label_status)
        
        self.setLayout(button_hlay)
        
       
    
    
    
    def displayerrorport(self,xc):
        
        self.ErrorCOM=ErrorW(300,200,'ERROR PORT CONNECTION: '+xc,'ERROR')
        self.ErrorCOM.exec_()

class ErrorW(QDialog):
    def __init__(self,width,height,errorText,windowTitle):
        super(QDialog,self).__init__()
        self.width=width
        self.height=height
        self.setMinimumSize(width, height)
        self.err_text=str(errorText)
        
        
        self.win_text=str(windowTitle)
        self.Text=QLabel(self.err_text.upper())
        
        
        self.setWindowTitle(self.win_text)

        #define layout
        hlay=QHBoxLayout()
        hlay.addWidget(self.Text)
        vlay=QVBoxLayout()
        vlay.addLayout(hlay)
        self.setLayout(vlay)

#############
#  RUN APP  #
#############
'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    BT=BT_search()
    
    
    
    
    
    sys.exit(app.exec_())
'''


