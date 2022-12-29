import serial
import numpy as np
import sys
import ctypes

####graph###
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

##excel
import pandas as pd

from PyQt5.QtCore import (
    QObject,
    QThreadPool, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot,
    QTimer
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
    QGridLayout,
    QTabWidget,
    QListWidget,
    QStyle
    
)

from class_Dati import (
    DatiSerial,
    WorkerKilled,
    DatiSignals,
    convert
)
from BTPY_class import(
    BT_search
)

'''
ax_sq = np.square(ax)
ay_sq = np.square(ay)
az_sq = np.square(az)

a = np.sqrt(ax_sq + ay_sq + az_sq)
l = len(a)
print("Acceleration array:", a)
print("The length of the array is:", l)

thr = 7 #soglia settata basandomi sul grafico. i picchi inizio passo e fine passo raggiungono 8g.
count = 0
for i in range(0, l):
    if a[i] >= thr:
        count += 1
steps = str(count /2)
'''
#print("number of peaks:", count)
#print("number of steps:", steps)

#classe Datastructure
class DataStructure:
    def __init__(self,X,Y,Z,acc,time,passi):
        self.X=X
        self.Y=Y
        self.Z=Z
        self.acc=acc
        self.temp_time=time
        self.temp_steps=passi
        self.minX=[]
        self.minY=[]
        self.minZ=[]
        self.maxX=[]
        self.maxY=[]
        self.maxZ=[]
        self.varX=[]
        self.varY=[]
        self.varZ=[]
        self.minAcc=[]
        self.maxAcc=[]
        self.varAcc=[]
        self.timesave=[]
        self.stepsave=[]
    
    def CreateData(self):
        self.minX.append(min(self.X))
        self.minY.append(min(self.Y))
        self.minZ.append(min(self.Z))
        self.maxX.append(max(self.X))
        self.maxY.append(max(self.Y))
        self.maxZ.append(max(self.Z))
        self.varX.append(np.var(self.X))
        self.varY.append(np.var(self.Y))
        self.varZ.append(np.var(self.Z))
        self.minAcc.append(min(self.acc))
        self.maxAcc.append(max(self.acc))
        self.varAcc.append(np.var(self.cc))



#classe lista
class List_Acquisitions(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()

        self.setLayout(layout)
        self.listwidget = QListWidget()
        self.listwidget.insertItem(0, "Excel1_example")
        self.listwidget.insertItem(1, "Excel2_example")
        self.listwidget.insertItem(2, "Excel3_example")
        self.listwidget.insertItem(3, "Excel4_example")
        self.listwidget.insertItem(4, "Excel5_example")
        # self.listwidget.setMaximumSize(50, 50)
        # self.listwidget.setMaximumSize(100, 100)
        self.listwidget.clicked.connect(self.clicked)
        layout.addWidget(self.listwidget)

    def clicked(self, qmodelindex):
        item = self.listwidget.currentItem()
        print(item.text())

class SaveDialog(QDialog):
    def __init__(self,text):
        self.maintext=str(text)
        self.MainTextlabel=QLabel(self.maintext)
        self.si=QPushButton("Yes")
        self.no=QPushButton("No")
        #self.flag=False
        self.i_icon=QStyle.standardIcon.SP_FileDialogInfoView

        
        hlayout=QHBoxLayout()
        hlayout.addItem(self.i_icon)
        hlayout.addWidget(self.si)
        hlayout.addWidget(self.no)


        vlayout=QVBoxLayout()
        vlayout.addWidget(self.MainTextlabel)
        vlayout.addWidget(hlayout)

        self.setLayout(vlayout)
        self.setWindowTitle("SaveData")

        if self.si.pressed:
            return True
        if self.no.pressed:
            return False


class MainW(QMainWindow):
    def __init__(self):
        super(MainW,self).__init__()
        #vairable for data stream
        self.X=[]
        self.Y=[]
        self.Z=[]
        self.time=[]
        self.provatimer=0
        self.portname=''
        self.totalsignal=[]
        self.passi=None

        #variable for data analysis
        self.DataStrc=DataStructure(self.X,self.Y,self.Z,self.totalsignal,self.provatimer,self.passi)
        
        #self parameters
        '''
        self.minX=None
        self.minY=None
        self.minZ=None
        self.maxX=None
        self.maxY=None
        self.maxZ=None
        self.varX=None
        self.varY=None
        self.varZ=None
        self.minAcc=None
        self.maxAcc=None
        self.varAcc=None
        '''
      
        #self.FlagFirstAbort=0
        
        
        #####Graph#####
        pen = pg.mkPen(color=(255, 0, 0))
        self.graphWidget = pg.PlotWidget()
        self.graphWidget
        self.graphWidget = PlotWidget(pen=pen)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Acceleration measurement")
        #Graph: Add axis labels
        styles = {'color': 'k', 'font-size': '15px'}
        self.graphWidget.setLabel('left', 'Acceleration [g]', **styles)
        self.graphWidget.setLabel('bottom', 'Time [sec]', **styles)
        self.graphWidget.addLegend()

        ####steps labels
        self.label_steps = QLabel()
        self.label_steps_text = QLabel('The number of Steps is:', self)
        self.label_steps.resize(170, 40)
        self.label_steps_text.resize(50, 40)
        


        ####timer####
        self.timerstring=QLabel("Time: ")
        self.timerstring.resize(50, 40)
        self.timerstring.move(560,25)
        self.timelabel=QLabel()
        self.timelabel.resize(50, 40)
        self.timelabel.move(560, 25)

        self.timer =QTimer()
        self.timer.timeout.connect(self.showTimer)
        self.start = False
        self.count = 0
        self.firststart=True

        

        ####excel###
        self.n_ex=0
        
        #title main window
        self.setWindowTitle("MainWindow")
        
        #defining button
        self.startAcq=QPushButton("Start Acquisition")
        self.startAcq.setDisabled(True)
        self.stopAcq=QPushButton("Stop Acquisition")
        self.stopAcq.setDisabled(True)
        self.ShowData=QPushButton("SaveData")
        self.ShowData.setDisabled(True)
        
        #define list
        self.lista=List_Acquisitions()

        #define runnable for data stream
        self.Dati=DatiSerial(self.portname,'Ready')
        
        #thread
        self.ThreadDati=QThreadPool()
        
        #define searchCOM widget
        self.searchWdiget=BT_search('Ready')
        
        #define signals searchCOM
        self.searchWdiget.signalport.portname.connect(self.SetPort)
        
        #define functions buttons
        self.startAcq.pressed.connect(self.StartAcquisition)
        self.stopAcq.pressed.connect(self.AbortAcquisition)
        self.ShowData.pressed.connect(self.ShowVectData)
        
        #define signals datastream
        self.Dati.signals.service_string.connect(self.SignalThreadStr)
        self.Dati.signals.dati.connect(self.SignalDati)
        
            
        

        ######DEFINE GUI LAYOUT######
        self.initGUI()

    
        
    
    def StartAcquisition(self):
            self.ResetXYZ()

            self.graphWidget.clear()
            self.Dati=DatiSerial(str(self.portname),'Ready')
            self.Dati.signals.service_string.connect(self.SignalThreadStr)
            self.Dati.signals.dati.connect(self.SignalDati)
            
            
            self.FlagStart=True
            self.ThreadDati=QThreadPool()

            self.ThreadDati.start(self.Dati)
            
            self.Dati.is_killed=False
            print("iskilled:"+str(self.Dati.is_killed))
            self.startAcq.setDisabled(True)
            self.label_steps.setText(str('0'))
            
    def ResetXYZ(self):
        self.X=[]
        self.Y=[]
        self.Z=[]
    
    def AbortAcquisition(self):
        self.DataStrc=DataStructure(self.X,self.Y,self.Z,self.totalsignal,self.provatimer,self.passi)
        self.saveDialog=SaveDialog('Do you want to save the acquisition?')
        self.saveDialog.exec_()
        if self.saveDialog:
            self.DataStrc.CreateData()

                
        self.Dati.Abort()
        #self.Dati.is_killed=True
        
        #print(self.Dati.PortName)
        print("iskilled:"+str(self.Dati.is_killed))
        if not self.Dati.serialPort.is_open:
            self.startAcq.setDisabled(False)
        self.resetTimer()
        #self.FlagFirstAbort=1
        
        

    def SignalThreadStr(self,stringa):
        print(str(stringa))
    
    def SignalDati(self,x,y,z):
        self.X=x
        self.Y=y
        self.Z=z
        
        
        
        if len(self.X) and len(self.Y) and len(self.Z):
            l=len(self.Z)

        self.draw(self.X,self.Y,self.Z)
        if self.firststart:    
            self.startTimer()
            self.firststart=False

        print("x:{}\r\ny:{}\r\nz:{}".format(self.X[l-1],self.Y[l-1],self.Z[l-1]))

    def draw(self,X,Y,Z):
        """!
        @brief Draw the plots.
    
        """
        ax_sq = np.square(X)
        ay_sq = np.square(Y)
        az_sq = np.square(Z)
        acc = np.sqrt(ax_sq + ay_sq + az_sq)
        self.totalsignal=acc

        l=len(acc)
        length=l-1
        l = np.arange(0, length+1, 1)
        
        self.graphWidget.plot(l,acc)
        steps=self.ThresholdCount(acc,l)
        self.passi=steps
        self.label_steps.setText(steps)


    def ThresholdCount(self,a,l):
        thr = 300 #soglia settata basandomi sul grafico. i picchi inizio passo e fine passo raggiungono 8g.
        count = 0
        for i in l:
            if a[i] >= thr:
                count += 1
        steps = str(int(count /4))
        return steps
    
    #SHOW DATAS
    def ShowVectData(self):

        #function to create data stracture#
        #self.CreateData(self.X,self.Y,self.Z,self.totalsignal)
        



        ####excel####

        self.ExcelSave(self.DataStrc)
        ''' pass inside the function self parameters
        self.ExcelSave(self.minX,
        self.minY,
        self.minZ,
        self.maxX,
        self.maxY,
        self.maxZ,
        self.varX,
        self.varY,
        self.varZ,
        self.minAcc,
        self.maxAcc,
        self.varAcc,
        self.provatimer,
        self.passi)
        '''

        
        
    
    #EXCEL FUNCTION 
    def ExcelSave(self,data):
        
        #data dictionary for self parameter
        '''
        data={ 'minX':minX,
            'minY':minY,
            'minZ':minZ,
            'maxX':maxX,
            'maxY':maxY,
            'maxZ':maxZ,
            'minAcc':minAcc,
            'maxAcc':maxAcc,
            'varAcc':varAcc,
            'tempo':tempo,
            'passi':passi}
        '''

        data={ 'minX':data.minX,
            'minY':data.minY,
            'minZ':data.minZ,
            'maxX':data.maxX,
            'maxY':data.maxY,
            'maxZ':data.maxZ,
            'varX':data.varX,
            'varY':data.varY,
            'varZ':data.varZ,
            'minAcc':data.minAcc,
            'maxAcc':data.maxAcc,
            'varAcc':data.varAcc,
            'tempo':tempo,
            'passi':passi}
        

        df=pd.DataFrame(data=data)
        
        df.to_excel("Acquisition_{}.xlsx".format(self.n_ex))
        self.n_ex+=1

    #function to create structure data#
    def CreateData(self,X,Y,Z,acc):
        self.minX=min(X)
        self.minY=min(Y)
        self.minZ=min(Z)
        self.maxX=max(X)
        self.maxY=max(Y)
        self.maxZ=max(Z)
        self.varX=np.var(X)
        self.varY=np.var(Y)
        self.varZ=np.var(Z)
        self.minAcc=min(acc)
        self.maxAcc=max(acc)
        self.varAcc=np.var(acc)






    #SETTING PORT FROM SEARCHCOM
    def SetPort(self,Port):
        self.portname=str(Port)
        print(self.portname)
        
        self.startAcq.setDisabled(False)
        self.stopAcq.setDisabled(False)
        self.ShowData.setDisabled(False)

    ####Timer Functions###
    def stopTimer(self):
        self.timer.stop()
        self.start = False
        self.start_btn.setDisabled(False)

    def showTimer(self):
        if self.start:
            self.count += 0.1

        if self.start:
            text_timer = str(round(self.count, 2)) + ' s'
            self.timelabel.setText(text_timer)

    def startTimer(self):
        self.start = True
        self.timer.start(100)
        #self.start_btn.setDisabled(True)

    def resetTimer(self):
        self.provatimer=self.count
        self.count = 0
        #text_timer = str(self.count) + ' s'
        #self.timelabel.setText(text_timer)
        self.start = False
        self.firststart=True
        #self.start_btn.setDisabled(False)
        

    def initGUI(self):

        WindowWid=QWidget()
        mainlayout=QGridLayout()

        #layout for buttons
        AcqButtonlayH=QHBoxLayout()
        AcqButtonlayH.addWidget(self.startAcq)
        AcqButtonlayH.addWidget(self.stopAcq)
        AcqButtonlayV=QVBoxLayout()
        AcqButtonlayV.addLayout(AcqButtonlayH)
        AcqButtonlayV.addWidget(self.ShowData)

        #layoulabels steps
        layoutlabel=QHBoxLayout()
        layoutlabel.addWidget(self.label_steps_text)
        layoutlabel.addWidget(self.label_steps)

        #layoutlabels timer
        layoutlabel_timer=QHBoxLayout()
        layoutlabel_timer.addWidget(self.timerstring)
        layoutlabel_timer.addWidget(self.timelabel)

        #sx tab main window
        sx_lay_w=QWidget()
        
        tabAcquisition=QWidget()
        tabAcquisition.layout=QVBoxLayout()
        tabAcquisition.layout.addLayout(AcqButtonlayV)
        tabAcquisition.layout.addWidget(self.searchWdiget)
        tabAcquisition.layout.addLayout(layoutlabel)
        tabAcquisition.layout.addLayout(layoutlabel_timer)

        tabAcquisition.setLayout(tabAcquisition.layout)

        tablist=QWidget()
        tablist.layout=QVBoxLayout()
        tablist.layout.addWidget(self.lista)
        tablist.setLayout(tablist.layout)


        tabsx=QTabWidget()
        tabsx.addTab(tabAcquisition,'Acquisition')
        tabsx.addTab(tablist,'Excel files')
        tabsx.setMaximumWidth(400)
        tabsx.resize(250,600)
        '''
        tabsx.setMaximumSize(250,600)
        
        tabsx.setMinimumSize(250, 250)
        '''

        sx_lay_w.layout=QVBoxLayout()
        sx_lay_w.layout.addWidget(tabsx)
        sx_lay_w.setLayout(sx_lay_w.layout)
        


        


        #dx tab
        dx_lay_w=QWidget()
        

        dx_HL=QVBoxLayout()
        
        dx_HL.addWidget(self.graphWidget)
        dx_lay_w.setLayout(dx_HL)

        #mainlayout
        mainlayout.addWidget(sx_lay_w,0,0)
        mainlayout.addWidget(dx_lay_w,0,1)
        WindowWid.setLayout(mainlayout)

        
        #Vecchia Gui layout
        '''
        #Vecchia Gui layout
        hlay=QHBoxLayout()
        hlay.addWidget(self.graphWidget)
        hlay.addWidget(self.startAcq)
        hlay.addWidget(self.stopAcq)
        hlay.addWidget(self.searchWdiget)
        vlay=QVBoxLayout()
        vlay.addLayout(hlay)
        vlay.addWidget(self.ShowData)
        Wid.setLayout(vlay)
        '''

        self.setCentralWidget(WindowWid)





if __name__ == '__main__':
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([])
    # works too.
    app = QApplication(sys.argv)
    
    # Create a Qt widget, which will be our window.
    
    w = MainW()
    w.show() # IMPORTANT!!!!! Windows are hidden by default.
    
    # Start the event loop.
    
    '''
    bt=BT_search()
    bt.show()
    '''
    
    sys.exit(app.exec_())



        
