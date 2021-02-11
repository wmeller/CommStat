"""
CommStat Tracker is an app for 3D Bn, 3D Mar made by Lt Wesley Eller and Lt Caleb Cimmarrusti for tracking key communications
status' on a tactical Getac computer.
"""
"""
Dev Notes:
    1/28/2021: This makes a layout with Unit and net columns/rows, no functionality. No menus.
    2/7/2021: Signals are connected to buttons. Added button groups, which is both more visually organized and allows the button methods
    to see the unit/net they are connected to more simply by using the title of the group. Loading from a csv file is implemented, but it
    still pulls from a default file and none of the menu functions are implemented.
    2/8/2021: Time update updates visible time on button and saves out to hard file. Saving to hard file implemented. Asks for config file on opening.
    uses a default config if nothing or bad data is found. Input file is very brittle, needs to be worked on. History works, but it's a janky UI.
    Undo works. Time updates work. Scrolling and resizing work. Export to csv works, no configuration options on that right now. None of the configuration
    works right now, you can't add or delete anything except time entries via the new time and undo buttons. I don't think anyone is going to
    want to edit in the app though, the exported csv files are way easier. One can always clear the data and just start over too.
    2/9/2021: Status changes as a function of time. There are some debug variables left in, and the timer is set to 1 second right now. The
    command view is called, but the class is not built yet.
    2/11/2021: All features work for V1.0 except POSREP permanence. It gets cleared when you close the window.
"""
import sys, os.path
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QScrollArea, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QGroupBox, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from CommandView import CommandView
import datetime
import csv
import pickle
import pdb

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #Main Layout creation, this is the sandbox
        print("Main layout creation")
        self.CentralWindow = QWidget()
        MainLayout = QVBoxLayout()
        #Toolbar with buttons for Add, Save, Export, View, Configure
        ToolbarLayout = QHBoxLayout()
        SaveButton = QPushButton("Save As", self)
        ExportButton = QPushButton("Export", self)
        ViewButton = QPushButton("Command View", self)
        ConfigureButton = QPushButton("Configure", self)
        self.menuBar()
        self.statusBar()

        print("Add the toolbar")
        SaveButton.clicked.connect(self.SaveMethod)
        ExportButton.clicked.connect(self.ExportMethod)
        ViewButton.clicked.connect(self.ViewMethod)
        ConfigureButton.clicked.connect(self.ConfigureMethod)

        ToolbarLayout.addWidget(SaveButton)
        ToolbarLayout.addWidget(ExportButton)
        ToolbarLayout.addWidget(ViewButton)
        ToolbarLayout.addWidget(ConfigureButton)
        MainLayout.addLayout(ToolbarLayout)

        #Start setting up the scrolling area where we will view the data
        self.DataViewScrollArea = QScrollArea()
        self.DataViewWidget = QWidget()
        self.DataViewScrollArea.setWidget(self.DataViewWidget)

        #Start main data dict, or import it from file
        #Debug, uncomment later
        #self.selFileName= QFileDialog.getOpenFileName(self, "Select a configuration csv file", '*.csv')
        self.selFileName= ['config.csv']
        print(self.selFileName)

        if self.selFileName[0] is ' ':
            print('No file selected')
            self.saveName = 'default'
            if not os.path.exists('default.csv'):
                with open('default.csv', 'w', newline='') as outFile:
                    defWriter = csv.writer(outFile)
                    defWriter.writerow(['Unit','India','Kilo', 'Lima'])
                    defWriter.writerow(['Net','TAC1', 'TAC2', 'CMD1'])
        elif not self.selFileName[0].endswith( 'csv' ):
            print('Wrong type of file selected')
            self.saveName = 'default'
            if not os.path.exists('default.csv'):
                with open('default.csv', 'w', newline='') as outFile:
                    defWriter = csv.writer(outFile, delimiter=',')
                    defWriter.writerow(['Unit','India','Kilo', 'Lima'])
                    defWriter.writerow(['Net','TAC1', 'TAC2', 'CMD1'])
        else:
            print('loading configuration files')
            self.saveName = self.selFileName[0].split('/')[-1].split('.')[0]
            print(self.saveName)
        #Set up the configuration for the files
        self.historyFileName = self.saveName+'.hist'
        if os.path.exists(self.historyFileName):
            print('found it!')
            newHistory = False
            with open(self.historyFileName, 'rb') as inFile:
                self.historyData = pickle.load(inFile)
        else:
            self.historyData = dict()
            newHistory = True

        #Grid to display data for units by net
        self.CommStatViewLayout = QGridLayout()
        self.DataViewWidget.setLayout(self.CommStatViewLayout)
        self.DataGroupList = []
        print("Add the net layouts")
        RowPos = 1
        ColPos = 2
        #get the net and unit configuration from a spreadsheet in the same folder. In the future, allow searching. Start with a blank config
        print("Load configuration")
        with open(self.saveName+'.csv', newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        #Clean up the list
        '''
        In the future, this should be it's own module which opens the selected file and intelligently searches for the data.
        Multiple file types should be allowed.
        The data should not necessarily have to be in a certain order.
        row order or column order should be allowed.
        The config file is requested at start up. new ones can be loaded later
        spaces in unit and net names should be removed.
        Any repeats should be removed
        '''
        if data[0][0].lower() == 'unit':
            UnitList = data[0][1:]
        else:
            UnitList = data[0]
        UnitList = [l for l in UnitList if l != ''] #this removes all the blank entries, added as an artifact of the read process
        if data[1][0].lower() == 'net':
            NetList = data[1][1:]
        else:
            NetList = data[1]
        NetList = [l for l in NetList if l != '']
        print('Config loaded')
        print(UnitList)
        print(NetList)
        #Loop through the unit and net list and build the UI
        for Net in NetList:
            print(Net)
            NetLabel = QLabel(Net)
            NetLabel.setStyleSheet("font-size: 20px")
            self.CommStatViewLayout.addWidget(NetLabel, RowPos, ColPos)
            ColPos += 1
        for Unit in UnitList:
            RowPos += 1
            ColPos = 1
            if Unit not in self.historyData:
                self.historyData[Unit]=dict()
            UnitLabel = QLabel(Unit)
            UnitLabel.setStyleSheet("font-size: 20px")
            self.CommStatViewLayout.addWidget(UnitLabel, RowPos, ColPos)
            for Net in NetList:
                if Net not in self.historyData[Unit]:
                    self.historyData[Unit][Net] = []
                    print('Added '+Unit+', '+Net)
                ColPos += 1
                #Check that the config file is loaded, has data, and is not empty
                if (not newHistory) and (Unit in self.historyData) and (Net in self.historyData[Unit]) and (len(self.historyData[Unit][Net])>0):
                    timeBtnText = 'Last: '+ self.historyData[Unit][Net][-1].strftime("%H%M")
                else:
                    timeBtnText = 'Last: None'
                timeButton = QPushButton(timeBtnText, self)
                timeButton.clicked.connect(self.UpdateTimeMethod)
                timeButton.setStyleSheet("\
                        background-color: rgba(171, 220, 255, 100);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        font-size: 15px;\
                        height: 30px;\
                        padding: 5px;\
                        spacing: 5px;\
                        ")
                historyButton = QPushButton('History')
                historyButton.clicked.connect(self.HistoryMethod)
                historyButton.setStyleSheet("\
                        background-color: rgba(171, 220, 255, 100);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        ")
                undoButton = QPushButton('Undo Last')
                undoButton.clicked.connect(self.UndoMethod)
                undoButton.setStyleSheet("\
                        background-color: rgba(171, 220, 255, 100);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        ")
                NetGroup = QGroupBox(Unit+" "+Net)
                BtnGroupLayout = QVBoxLayout()
                NetGroup.setStyleSheet("\
                                       border-radius: 8px;\
                                       border-style: solid;\
                                       border-width: 1px;\
                                       padding: 5px;\
                                       ")
                BtnGroupLayout.addWidget(timeButton)
                BtnGroupLayout.addWidget(historyButton)
                BtnGroupLayout.addWidget(undoButton)
                NetGroup.setLayout(BtnGroupLayout)
                self.DataGroupList.append(NetGroup)
                self.CommStatViewLayout.addWidget(NetGroup)

        #Save the history dict to the same name as the config file
        with open(self.historyFileName, 'wb') as outFile:
            pickle.dump(self.historyData, outFile, protocol=pickle.HIGHEST_PROTOCOL)

        #Finish setting up the scrolling area where we will view the data
        self.DataViewScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.DataViewScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.DataViewScrollArea.setWidgetResizable(True)
        MainLayout.addWidget(self.DataViewScrollArea)

        #Set up the update function
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateStatusMethod)
        self.updateTimer.setInterval(1*1000) #interval is set in milliseconds. Run the update every second while debugging, update to a minute later
        self.updateTimer.start()

        #Open the window and display the UI
        self.CentralWindow.setLayout(MainLayout)
        self.setCentralWidget(self.CentralWindow)
        self.setWindowTitle('Comm Stat Tracker')
        self.showMaximized()

    def UndoMethod(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        #Check if there is any old data
        Unit = sender.parent().title().split(' ')[0]
        Net = sender.parent().title().split(' ')[1]
        if len(self.historyData[Unit][Net])>1:
            #If there is data, grab the second to last entry as the new main entry
            lastEntry = self.historyData[Unit][Net][-2]
        else:
            lastEntry = 'None'
        #Drop the last entry. This works even if the set is empty
        self.historyData[Unit][Net] = self.historyData[Unit][Net][0:-1]
        #find the time button
        for child in sender.parent().children():
            try:
                if 'Last' in child.text():
                    child.setText("Last: "+lastEntry)
            except:
                pass
        with open(self.historyFileName, 'wb') as outFile:
            pickle.dump(self.historyData, outFile, protocol=pickle.HIGHEST_PROTOCOL)
        print('Sucessfully undid last stamp')
        if hasattr(self, 'CommandViewWindow'):
            if self.CommandViewWindow.isVisible():
                self.CommandViewWindow.updateUnit = Unit
                self.CommandViewWindow.updateTime = newTime
                self.CommandViewWindow.updateNet = Net
                self.CommandViewWindow.updateStatusMethod()
                self.CommandViewWindow.updateUnit = False

    def HistoryMethod(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        Unit = sender.parent().title().split(' ')[0]
        Net = sender.parent().title().split(' ')[1]
        #Message box with history
        self.msgBox = QMessageBox()
        self.msgBox.setWindowTitle('History')
        self.msgBox.setText('Open the detailed text for history')
        self.msgBox.setDetailedText( Unit+' ' + Net + ' History:\n'+'\n'.join([i.strftime('%m%d %H%M') for i in self.historyData['Kilo']['TAC1']]))
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.exec()

    def SaveMethod(self):
        print ('You hit a save button!!')
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')

    def ExportMethod(self):
        print ('You hit a export button!!')
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        #In the future, use a popup to set which format out the user wants to use.
        #For now, just use CSV which Excel or notepad can open to avoid any compatibility issues
        #set the filename
        outFileName = self.saveName + '_export_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.csv'
        with open(outFileName, 'w', newline='') as outFile:
            defWriter = csv.writer(outFile)
            for Unit in self.historyData:
                for Net in self.historyData[Unit]:
                    data = [i.strftime("%Y%m%d-%H%M%S") for i in self.historyData[Unit][Net]]
                    defWriter.writerow([Unit]+[Net]+data)
        print("succesfully exported file "+outFileName)
        self.msgBox = QMessageBox()
        self.msgBox.setWindowTitle('Sucess!')
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setText("succesfully exported file "+outFileName)
        self.msgBox.setStandardButtons(QMessageBox.Ok)
        self.msgBox.exec()

    def ViewMethod(self):
        print ('You hit a view button!!')
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        self.CommandViewWindow = CommandView(self.selFileName)
        #self.CommandViewWindow.closeEvent(self.closeCommandViewMethod)
        self.CommandViewWindow.show()

    def closeCommandViewMethod(self, event):
        print('Closed Command View')
        self.CommandViewWindow.event.accept()

    def ConfigureMethod(self):
        print ('You hit a configure button!!')
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        fileName = QFileDialog.getOpenFileName(self, "Select a configuration csv file")
        print(fileName)

    def UpdateTimeMethod(self):
        sender = self.sender()
        newTime = datetime.datetime.now()
        newText = 'Last: '+newTime.strftime("%H%M")
        Unit = sender.parent().title().split(' ')[0]
        Net = sender.parent().title().split(' ')[1]
        #Save the history and update the hard file
        self.historyData[Unit][Net].append(newTime)
        with open(self.historyFileName, 'wb') as outFile:
            pickle.dump(self.historyData, outFile, protocol=pickle.HIGHEST_PROTOCOL)
        sender.setText(newText)
        if hasattr(self, 'CommandViewWindow'):
            if self.CommandViewWindow.isVisible():
                self.CommandViewWindow.updateUnit = Unit
                self.CommandViewWindow.updateTime = newTime
                self.CommandViewWindow.updateNet = Net
                self.CommandViewWindow.updateStatusMethod()
                self.CommandViewWindow.updateUnit = False

    def updateStatusMethod(self):
        currentTime = datetime.datetime.now()
        for group in self.DataGroupList:
            Unit, Net = group.title().split(' ')
            if len(self.historyData[Unit][Net]) > 0:
                #IF there are any entries, check the time stamp. If there are no entries, just say so and move on.
                timeDif = currentTime - self.historyData[Unit][Net][-1]
            else:
                continue
            if timeDif.seconds > 2:
                group.setStyleSheet("\
                        background-color: rgba(255, 0, 0, 150);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        padding: 5px;\
                        ")
            elif timeDif.seconds > 1:
                group.setStyleSheet("\
                        background-color: rgba(255, 255, 0, 150);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        padding: 5px;\
                        ")
            else:
                group.setStyleSheet("\
                        background-color: rgba(0, 255, 0, 150);\
                        border-radius: 8px;\
                        border-style: solid;\
                        border-width: 1px;\
                        padding: 5px;\
                        ")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    #Start the application
    sys.exit(app.exec_())
