# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 20:38:51 2021

@author: wesley.eller

CommandView presents a birds eye view of the current COMM status. It needs to be passed the Unit and Net configuration and history file 
used by the main UI.
"""

from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QScrollArea, QLineEdit, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QGroupBox
from PyQt5.QtCore import Qt, QTimer
import pickle
import datetime
import pdb

class CommandView(QMainWindow):
    
    def __init__(self, historyFileName):
        super().__init__()
        self.historyFileName = historyFileName[0].split('.')[0]+'.hist'
        self.initUI()
        
    def initUI(self):
        self.resize(800, 800)
        self.updateUnit = False
        
        with open(self.historyFileName, 'rb') as inFile:
                self.historyData = pickle.load(inFile)

        MainLayout = QHBoxLayout()
        
        #Add the list of all nets to the left side
        self.ScrollNetListLayout = QScrollArea()
        self.NetListLayoutWidget = QWidget()
        self.NetListLayout = QVBoxLayout()
        self.NetListLayoutWidget.setLayout(self.NetListLayout)
        self.ScrollNetListLayout.setWidget(self.NetListLayoutWidget)
        self.NetListLayoutWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.ScrollNetListLayout.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.ScrollNetListLayout.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ScrollNetListLayout.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollNetListLayout.setWidgetResizable(True)
        #Loop through first unit to get list of nets
        firstUnit = next(iter(self.historyData))
        NetHeader = QLabel("All Nets")
        NetHeader.setStyleSheet("\
                                font-size:25px;\
        ")
        self.NetListLayout.addWidget(NetHeader)
        for Net in self.historyData[firstUnit]:
            self.NetListLayout.addWidget(QLabel(Net))
            
        #Finish setting up the scrolling area where we will view the data
        self.ScrollDataViewLayout = QScrollArea()
        #self.ScrollDataViewLayout.setFixedHeight(1200)
        self.ScrollDataViewLayout.setStyleSheet("\
                                               padding:5px;\
                                               spacing:5px;\
                                               margin:1px;\
                                               border-style:solid;\
                                               border-width:1px;\
                                               ")
        self.DataViewWidget = QWidget()
        self.DataViewLayout = QGridLayout()
        self.DataViewWidget.setLayout(self.DataViewLayout)
        self.ScrollDataViewLayout.setWidget(self.DataViewWidget)
        self.ScrollDataViewLayout.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ScrollDataViewLayout.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollDataViewLayout.setWidgetResizable(True)
        #Build the Overview. Max 4 blocks right to left.
        #Each block has the unit name, a spot for the POSREP, 
        #the comm status, which is the status of the best net, which net that 
        #is, and the time of last contact. If there is more then one net, it 
        #give this information for up to three nets.
        colIndex = 0
        rowIndex = 0
        self.overviewDataDict = {}
        now = datetime.datetime.now()
        for Unit in self.historyData:
            #Add a button group for the unit which will show the data
            unitBtnGroup = QGroupBox()
            #unitBtnGroup.setTitle(Unit)
            unitBtnGroup.setFixedHeight(250)
            unitBtnGroupLayout = QGridLayout()
            
            #Figure out the current net and last time
            firstFlag = True
            currentNet = 'No Contact'
            currentTime = 'No Contact'
            for Net in self.historyData[Unit]:
                if len(self.historyData[Unit][Net]) == 0:
                    continue
                minTimeDiff = now - self.historyData[Unit][Net][-1]
                if not firstFlag:
                    if minTimeDiff.seconds < currentTimeDiff.seconds:
                        currentNet = Net
                        currentTimeDiff = minTimeDiff
                        currentTime = self.historyData[Unit][Net][-1].strftime('%H%M')
                        currentTimeStamp = self.historyData[Unit][Net][-1]
                else:
                    firstFlag = False
                    currentNet = Net
                    currentTimeDiff = minTimeDiff
                    currentTime = self.historyData[Unit][Net][-1].strftime('%H%M')
                    currentTimeStamp = self.historyData[Unit][Net][-1]
            
            #QGridLayout addWidget(Widget, row, column, rowspan, columnspan)
            UnitTitle = QLabel(Unit)
            unitBtnGroupLayout.addWidget(UnitTitle, 0, 0, 1, 2)
            unitBtnGroupLayout.addWidget(QLabel('Last Net:'), 1, 0)
            NetLabel = QLabel(currentNet)
            unitBtnGroupLayout.addWidget(NetLabel, 1,1)
            unitBtnGroupLayout.addWidget(QLabel('Contact Time:'), 2, 0 )
            TimeLabel = QLabel(currentTime)
            unitBtnGroupLayout.addWidget(TimeLabel, 2, 1 )
            PosRep = QLineEdit('PosRep')
            unitBtnGroupLayout.addWidget(PosRep, 3, 0, 1, 2 )
            unitBtnGroup.setLayout(unitBtnGroupLayout)
            
            #Add the styling depending on the status
            if currentTimeDiff.seconds > 20:
                unitBtnGroup.setStyleSheet("\
                        background-color: rgba(255, 0, 0, 150);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        padding: 5px;\
                        font-size:20px;\
                        ")
            elif currentTimeDiff.seconds > 10:
                unitBtnGroup.setStyleSheet("\
                        background-color: rgba(255, 255, 0, 150);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        padding: 5px;\
                        font-size:20px;\
                        ")
            else:
                unitBtnGroup.setStyleSheet("\
                        background-color: rgba(0, 255, 0, 150);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        padding: 5px;\
                        font-size:20px;\
                        ")
                    
            #Add all of them to the overview dict for later editing
            self.overviewDataDict[Unit]={'BtnGroup':unitBtnGroup, 'CurrentTimeStamp': currentTimeStamp, 'UnitTitle' : UnitTitle, 'NetLabel': NetLabel, 'TimeLabel':TimeLabel, 'PosRep':PosRep}
            #Figure out where in the grid this should go
            if colIndex == 4:
                colIndex = 0
                rowIndex = rowIndex + 1
                
            self.DataViewLayout.addWidget(unitBtnGroup, rowIndex, colIndex)
            colIndex = colIndex + 1
            
        
        #Add the net list and overview to the main layout
        MainLayout.addWidget(self.ScrollNetListLayout)
        MainLayout.addWidget(self.ScrollDataViewLayout)
        
        #Set up the update function
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateStatusMethod)
        self.updateTimer.setInterval(10*1000) #interval is set in milliseconds. Run the update every second while debugging, update to a minute later
        self.updateTimer.start()
        
        #Open the window and display the UI
        self.CentralWidget = QWidget()
        self.CentralWidget.setLayout(MainLayout)
        self.setCentralWidget(self.CentralWidget)
        self.setWindowTitle('Command View')
        self.showMaximized()
        
        
    def updateStatusMethod(self):
        #if a unit to update is given, just update that.
        if self.updateUnit is not False: 
            Unit = self.updateUnit
            lastTime = self.updateTime
            lastNet = self.updateNet
            now = datetime.datetime.now()
            lastTimeDiff = now - lastTime
            print('Last net contacted on was '+lastNet)
            #find the overview for this unit
            unitOverviewHandle = self.overviewDataDict[Unit]['BtnGroup']
            self.overviewDataDict[Unit]['NetLabel'].setText(lastNet)
            self.overviewDataDict[Unit]['TimeLabel'].setText(lastTime.strftime("%H%M"))
            self.overviewDataDict[Unit]['CurrentTimeStamp'] = lastTime
            unitOverviewHandle.setStyleSheet("\
                    background-color: rgba(0, 255, 0, 150);\
                    border-radius: 8px;\
                    border-style: solid;\
                    border-width: 1px;\
                    padding: 5px;\
                    font-size:20px;\
                    ")
            
        #Otherwise check for units which are no longer green.
        else:
            #Loop through every unit
            now = datetime.datetime.now()
            for Unit in self.overviewDataDict:
                #Check the current Net and timestamp for updates
                Net = self.overviewDataDict[Unit]['NetLabel'].text()
                if Net is 'No Contact':
                    continue
                lastTimeDiff =now - self.overviewDataDict[Unit]['CurrentTimeStamp']
                unitOverviewHandle = self.overviewDataDict[Unit]['BtnGroup']
                if lastTimeDiff.seconds > 20:
                    unitOverviewHandle.setStyleSheet("\
                            background-color: rgba(255, 0, 0, 150);\
                            border-radius: 8px;\
                            border-style: solid;\
                            border-width: 1px;\
                            padding: 5px;\
                            font-size:20px;\
                            ")
                elif lastTimeDiff.seconds > 10:
                    unitOverviewHandle.setStyleSheet("\
                            background-color: rgba(255, 255, 0, 150);\
                            border-radius: 8px;\
                            border-style: solid;\
                            border-width: 1px;\
                            padding: 5px;\
                            font-size:20px;\
                            ")
                else:
                    unitOverviewHandle.setStyleSheet("\
                            background-color: rgba(0, 255, 0, 150);\
                            border-radius: 8px;\
                            border-style: solid;\
                            border-width: 1px;\
                            padding: 5px;\
                            font-size:20px;\
                            ")
                