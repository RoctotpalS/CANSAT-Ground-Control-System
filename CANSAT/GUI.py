import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFrame, QColorDialog, QInputDialog, QLineEdit, QComboBox, QProgressBar
from PyQt5.QtWidgets import QColorDialog, QInputDialog, QLineEdit, QComboBox, QProgressBar
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QMainWindow, QLayout, QAbstractItemView , QHeaderView, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QProxyStyle, QStyle, QProgressBar, QSizePolicy, QTableWidget, QTableWidgetItem, QAbstractScrollArea
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor, QPalette, QBrush, QPixmap, QIcon, QFont, QCursor, QStandardItemModel, QStandardItem, QIntValidator
from PyQt5 import  QtGui
from PyQt5.QtCore import Qt, QTime, QTimer, QThread, pyqtSignal
from time import sleep
# import Qcharts
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QBarSet, QBarSeries, QBarCategoryAxis, QHorizontalBarSeries
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
#import QGraphicsView
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem
from PyQt5.QtCore import QRectF, QPointF, Qt, QTime, QTimer, QThread, pyqtSignal
#import QListWidget
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
import numpy as np
from pyqtgraph import PlotWidget
from PyQt5 import QtWidgets
import pyqtgraph as pg

# import telemetryClass

class Example(QMainWindow):
    
        def __init__(self):
            super().__init__()

            self.setFixedHeight(900)
            self.setFixedWidth(1500)
            self.setWindowTitle('Team Avinya - Ground Station Software')
            
            #change background color
            self.setAutoFillBackground(True)
            p = self.palette()
            # set mat brown color
           # p.setColor(self.backgroundRole(), QColor(179, 206, 229))
            p.setColor(self.backgroundRole(), QColor(50, 61, 65))
            self.setPalette(p)

            # add logo
            self.logo = QLabel(self)
            self.logo.setPixmap(QPixmap('AVINYA_LOGO.png'))
            self.logo.setGeometry(QtCore.QRect(695, 10, 150, 150))
            self.logo.setScaledContents(True)
            self.logo.setAlignment(Qt.AlignCenter)
            # change border of logo using rgb
            self.logo.setStyleSheet("border: 2px solid rgb(179, 226, 229);")
            #change shape of logo
            self.logo.setMask(self.logo.pixmap().mask())


            self.initUI()
    
        def initUI(self):            
            # add simulation button
            self.simulationButton = QPushButton('Calibrate', self)
            self.simulationButton.setGeometry(QtCore.QRect(315, 15, 100, 30))
            self.simulationButton.clicked.connect(self.simulationButtonFunction)

            # add enable button
            self.enableButton = QPushButton('Enable', self)
            self.enableButton.setGeometry(QtCore.QRect(315, 45, 100, 30))
            self.enableButton.clicked.connect(self.enableButtonFunction)

            # add disable button
            self.disableButton = QPushButton('Disable', self)
            self.disableButton.setGeometry(QtCore.QRect(315, 75, 100, 30))
            self.disableButton.clicked.connect(self.disableButtonFunction)

            # add disconnect button
            self.disconnectButton = QPushButton('Simulation', self)
            self.disconnectButton.setGeometry(QtCore.QRect(315, 105, 100, 30))
            self.disconnectButton.clicked.connect(self.disconnectButtonFunction)

            # add connect button
            self.connectButton = QPushButton('Connect', self)
            #set style sheet
            self.connectButton.setGeometry(QtCore.QRect(100, 75, 100, 30))
            self.connectButton.clicked.connect(self.connectButtonFunction)
            # add disconnect button
            self.disconnectButton = QPushButton('Disconnect', self)
            self.disconnectButton.setGeometry(QtCore.QRect(200, 75, 100, 30))
            self.disconnectButton.clicked.connect(self.disconnectButtonFunction)

            

            # add com selector
            self.comSelector = QComboBox(self)
            self.comSelector.setGeometry(QtCore.QRect(100, 45, 100, 35))    
            self.comSelector.addItem('COM1')
            self.comSelector.addItem('COM2')
            self.comSelector.addItem('COM3')
            self.comSelector.addItem('COM4')
            self.comSelector.currentTextChanged.connect(self.currentComChanged)
            # add com label
      #      self.comLabel = QLabel(self)
      #      self.comLabel.setText("COM")
      #      self.comLabel.setGeometry(QtCore.QRect(135, 10, 100, 20))
            
            # add baud rate selector
            self.baudrateSelector = QComboBox(self)
            self.baudrateSelector.setGeometry(QtCore.QRect(200, 45, 100, 35))
            self.baudrateSelector.addItem('9600')
            self.baudrateSelector.addItem('115200')
            self.baudrateSelector.addItem('230400')
            self.baudrateSelector.addItem('460800')
            self.baudrateSelector.addItem('921600')
            self.baudrateSelector.currentTextChanged.connect(self.currentBaudrateChanged)
            # add baud rate label
      #      self.baudrateLabel = QLabel(self)
      #      self.baudrateLabel.setText("Baudrate")
      #      self.baudrateLabel.setGeometry(QtCore.QRect(220, 10, 100, 20))

            #add progress bar
            self.progressBar = QtWidgets.QProgressBar(self)
            self.progressBar.setGeometry(QtCore.QRect(870, 50, 250, 30))
            self.progressBar.setProperty("value", 24)
            self.progressBar.setObjectName("progressBar")
            self.progressBar.setValue(50)
            self.progressBar.setMaximum(100)
            self.progressBar.setMinimum(0)
            
            # add progress bar label
            self.progressBarLabel = QLabel(self)
            self.progressBarLabel.setText("Mission Progress ")
            self.progressBarLabel.setFont(QFont('Arial', 15))
            self.progressBarLabel.setGeometry(QtCore.QRect(800, 17, 200, 35))
            self.progressBarLabel.setStyleSheet("color: rgb(179, 226, 229);")
            
            # add progress percent label
            self.progressPercentLabel = QLabel(self)
            self.progressPercentLabel.setFont(QFont('Arial', 15))
            self.progressPercentLabel.setText("50%")
            self.progressPercentLabel.setGeometry(QtCore.QRect(1050, 27, 100, 20))
            self.progressPercentLabel.setStyleSheet("color: rgb(179, 226, 229);")

            # add telemetry table widget
            self.telemetryTable = QtWidgets.QTableWidget(self)
            self.telemetryTable.setGeometry(QtCore.QRect(20, 680, 1159, 200))
            self.telemetryTable.setObjectName("telemetryTable")
            self.telemetryTable.setColumnCount(17)
            self.telemetryTable.setRowCount(10)
            self.telemetryTable.setHorizontalHeaderLabels(["Team ID", "Mission Time", "Packet Count", "Altitude", "Pressure", "Temp", "Volt", "GPS TIME", "GPS Latitude", "GPS Longtitude", "GPS Altitude", "GPS SATs", "Air Speed", "Particle Count", "Pitch", "Roll", "Yaw"])
            print(self.telemetryTable.rowCount())
            self.telemetryTable.setSortingEnabled(True)
            self.telemetryTable.setCornerButtonEnabled(False)
            self.telemetryTable.setGridStyle(QtCore.Qt.SolidLine)
            self.telemetryTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.telemetryTable.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.telemetryTable.setSelectionMode(QAbstractItemView.SingleSelection)
            self.telemetryTable.setAlternatingRowColors(True)
            self.telemetryTable.setShowGrid(True)
            self.telemetryTable.setWordWrap(False)
            self.telemetryTable.setCornerButtonEnabled(False)
            
            #set table column width
            self.telemetryTable.setColumnWidth(0, 50)  # team id
            self.telemetryTable.setColumnWidth(1, 90) # mission time
            self.telemetryTable.setColumnWidth(2, 90)  # packet count
            self.telemetryTable.setColumnWidth(3, 50)  # altitude
            self.telemetryTable.setColumnWidth(4, 60)  # pressure
            self.telemetryTable.setColumnWidth(5, 50)  # temp
            self.telemetryTable.setColumnWidth(6, 50)  # volt
            self.telemetryTable.setColumnWidth(7, 70)  # gps Time
            self.telemetryTable.setColumnWidth(8, 80)  # gps latitude
            self.telemetryTable.setColumnWidth(9, 90)  # gps longtitude
            self.telemetryTable.setColumnWidth(10, 80) # gps altitude
            self.telemetryTable.setColumnWidth(11, 70) # gps sats
            self.telemetryTable.setColumnWidth(12, 70) # air speed
            self.telemetryTable.setColumnWidth(13, 85) # particle count
            self.telemetryTable.setColumnWidth(14, 45) # pitch
            self.telemetryTable.setColumnWidth(15, 45) # roll
            self.telemetryTable.setColumnWidth(16, 45) # yaw
            # set table row height
            for i in range(0, self.telemetryTable.rowCount()):
                self.telemetryTable.setRowHeight(i, 20)
    
            # add table widget button
            self.telemetryTableButton = QPushButton(self)
            self.telemetryTableButton.setText("Clear Table")
            self.telemetryTableButton.setGeometry(QtCore.QRect(1180, 855, 100, 30))
            self.telemetryTableButton.clicked.connect(self.cleanTelemetryTableButtonFunction)


            testTelemetryDatas = list()
            testTelemetryDatas.append(["5423", "00:00:00", "1", "0.3", "1023.3", "22", "7.32", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:01", "2", "0.5", "1025.5", "22", "7.21", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:02", "3", "0.3", "1023.6", "23", "7.22", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:03", "4", "0.4", "1024.1", "22", "7.2", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:04", "5", "0.1", "1021.3", "22", "7.19", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:05", "6", "-0.2", "1019.5", "23", "7.16", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:06", "7", "0.3", "1023.6", "23", "7.14", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "0", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:07", "8", "0.2", "1022.3", "23", "7.15", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "1", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:08", "9", "0.1", "1021.5", "23", "7.16", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "2", "0", "0", "0"])
            # testTelemetryDatas.append(["5423", "00:00:09", "10", "0.1", "1021.8", "22", "7.13", "00:00:00", "40.742272", "30.325883", "100", "0", "0", "4", "0", "0", "0"])
            self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:10", "11", "0.2", "1022.7", "22", "7.12", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "5", "10", "14", "28"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:11", "12", "0.3", "1023.3", "22", "7.11", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "6", "15", "12", "29"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:12", "13", "0.2", "1022.9", "22", "7.10", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "7", "13", "9", "39"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:13", "14", "0.3", "1023.3", "23", "7.11", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "7", "5", "12", "28"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:14", "15", "0.3", "1023.6", "23", "7.10", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "8", "7", "11", "25"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:15", "16", "0.2", "1022.4", "23", "7.09", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "8", "1", "12", "24"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))
            
            # testTelemetryDatas.append(["5423", "00:00:16", "17", "0.3", "1023.5", "22", "7.09", "00:00:00", "40.742272", "30.325883", "100", "9", "0", "9", "3", "6", "20"])
            # self.telemetryTable.setRowCount(len(testTelemetryDatas))

            for i in range(0, len(testTelemetryDatas)):
                for j in range(0, len(testTelemetryDatas[i])):
                    self.telemetryTable.setItem(i, j, QTableWidgetItem(testTelemetryDatas[i][j]))

            #chose a row to highlight green
            self.telemetryTable.selectRow(16)
            self.telemetryTable.setStyleSheet("QTableWidget::item:selected {background-color: YellowGreen;}")
            self.telemetryTable.setFrameStyle(QFrame.Panel | QFrame.Sunken)


            
            # axis view
            self.imageLabel = QLabel(self)
            self.imageLabel.setGeometry(1189, 180, 300, 300)
            self.imageLabel.setPixmap(QPixmap("AVINYA_LOGO.png"))
            self.imageLabel.setScaledContents(True)
            self.imageLabel.setAlignment(Qt.AlignCenter)
            self.imageLabel.setStyleSheet("background-color: white")
            self.imageLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.imageLabel.show()

            # add pitch roll yaw label
            pitchRollYawString = "Pitch: 3°    Roll: 6°    Yaw: 20°"
            self.pitchRollYawText = QLabel(self)
            self.pitchRollYawText.setGeometry(1189, 830, 300, 20)
            self.pitchRollYawText.setFont(QFont('Arial', 12))
            self.pitchRollYawText.setText(pitchRollYawString)
            self.pitchRollYawText.setAlignment(Qt.AlignCenter)
            self.pitchRollYawText.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.pitchRollYawText.setStyleSheet("background-color: white")
            self.pitchRollYawText.show()
            
            # map view
            self.imageLabel = QLabel(self)
            self.imageLabel.setGeometry(1189, 524, 300, 300)
            self.imageLabel.setPixmap(QPixmap("CANSAT_LOGO.png"))
            self.imageLabel.setScaledContents(True)
            self.imageLabel.setAlignment(Qt.AlignCenter)
            self.imageLabel.setStyleSheet("background-color: white")
            self.imageLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.imageLabel.show()

            # add latitude longitude altitude sats label
            latitudeLongitudeAltitudeSatsString = "Lat: 40.742272°    Long: 30.325883°    Alt: 121.2m"
            self.latitudeLongitudeAltitudeSatsText = QLabel(self)
            self.latitudeLongitudeAltitudeSatsText.setGeometry(1060, 485, 470, 20)
            self.latitudeLongitudeAltitudeSatsText.setFont(QFont('Arial', 11))
            self.latitudeLongitudeAltitudeSatsText.setText(latitudeLongitudeAltitudeSatsString)
            self.latitudeLongitudeAltitudeSatsText.setAlignment(Qt.AlignCenter)
            self.latitudeLongitudeAltitudeSatsText.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.latitudeLongitudeAltitudeSatsText.setStyleSheet("background-color: white")
            self.latitudeLongitudeAltitudeSatsText.show()

        
            # add time label
            timeString = "Mission Time: "
            self.timeText = QLabel(self)        
            self.timeText.setGeometry(460, 45, 270, 30)
            self.time = QTime.currentTime()
            self.timeText.setFont(QFont('Arial', 15))
            self.timeText.setText(timeString + "00:00:16")
            self.timeText.setAlignment(Qt.AlignCenter)
            self.timeText.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.timeText.setStyleSheet("background-color: white")

            # add altitude label
            altitudeString = "Altitude: 0.3 m"
            self.altitudeText = QLabel(self)
            self.altitudeText.setGeometry(910, 88, 150, 20)
            self.altitudeText.setFont(QFont('Arial', 13))
            self.altitudeText.setText(altitudeString)
            self.altitudeText.setAlignment(Qt.AlignCenter)
  #          self.altitudeText.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.altitudeText.setStyleSheet("background-color: white")
            self.altitudeText.show()

            # create table
            self.stateTable = QTableWidget(self)
            self.stateTable.setGeometry(1150, 20, 147, 90)
            self.stateTable.setColumnCount(2)
            self.stateTable.setRowCount(4)
            # not show index
            self.stateTable.verticalHeader().setVisible(False)
            self.stateTable.horizontalHeader().setVisible(False)
            self.stateTable.setItem(0, 1, QTableWidgetItem("Started"))
            self.stateTable.setItem(1, 1, QTableWidgetItem("Not Started"))
            self.stateTable.setItem(2, 1, QTableWidgetItem("Not Started"))
            self.stateTable.setItem(3, 1, QTableWidgetItem("Not Started"))
            self.stateTable.setItem(0, 0, QTableWidgetItem("Launch"))
            self.stateTable.setItem(1, 0, QTableWidgetItem("Ascent"))
            self.stateTable.setItem(2, 0, QTableWidgetItem("Descent"))
            self.stateTable.setItem(3, 0, QTableWidgetItem("Landing"))
            self.stateTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.stateTable.setShowGrid(False)
            #chose a row to highlight green
            self.stateTable.selectRow(0)
            self.stateTable.setStyleSheet("QTableWidget::item:selected {background-color: YellowGreen;}")
            self.stateTable.setFrameStyle(QFrame.Panel | QFrame.Sunken)

            self.stateTable.resizeColumnsToContents()
            self.stateTable.resizeRowsToContents()
            self.stateTable.show()

            # use pyqtgraph to plot data
            self.AltiudePlot = pg.PlotWidget(self)
            self.AltiudePlot.setGeometry(50, 180, 280, 200)
            self.AltiudePlot.setBackground('w')
            self.AltiudePlot.showGrid(x=True, y=True)
            self.AltiudePlot.setLabel('left', 'Altitude', units='m')
            self.AltiudePlot.setLabel('bottom', 'Time', units='s')
            #generate random data
            line1 = self.AltiudePlot.plot([8,9,10,11,12,13,14,15,16,17], [0.2,0.1,0.1,0.2,0.3,0.2,0.3,0.3,0.2,0.3], pen='r')
            

            # use pyqtgraph to plot data
            self.TempraturePlot = pg.PlotWidget(self)
            self.TempraturePlot.setGeometry(400, 180, 280, 200)
            self.TempraturePlot.setBackground('w')
            self.TempraturePlot.showGrid(x=True, y=True)
            self.TempraturePlot.setLabel('left', 'Temprature', units='C')
            self.TempraturePlot.setLabel('bottom', 'Time', units='s')
            #generate random data
            line2 = self.TempraturePlot.plot([8,9,10,11,12,13,14,15,16,17], [23,23,22,22,22,22,23,23,23,22], pen='r')

            # use pyqtgraph to plot data
            self.PressurePlot = pg.PlotWidget(self)
            self.PressurePlot.setGeometry(750, 180, 280, 200)
            self.PressurePlot.setBackground('w')
            self.PressurePlot.showGrid(x=True, y=True)
            self.PressurePlot.setLabel('left', 'Pressure', units='Pa')
            self.PressurePlot.setLabel('bottom', 'Time', units='s')
            #generate random data
            line3 = self.PressurePlot.plot([8,9,10,11,12,13,14,15,16,17], [1022.3,1021.5,1021.8,1022.7,1023.3,1022.9,1023.3,1023.6,1022.4,1023.5], pen='r')
            
            # use pyqtgraph to plot data
            self.AirSpeedPlot = pg.PlotWidget(self)
            self.AirSpeedPlot.setGeometry(50, 430, 280, 200)
            self.AirSpeedPlot.setBackground('w')
            self.AirSpeedPlot.showGrid(x=True, y=True)
            self.AirSpeedPlot.setLabel('left', 'Air Speed', units='m/s')
            self.AirSpeedPlot.setLabel('bottom', 'Time', units='s')
            #generate random data
            line4 = self.AirSpeedPlot.plot([8,9,10,11,12,13,14,15,16,17], [0.2,0.1,0.1,0.2,0.3,0.2,0.3,0.3,0.2,0.3], pen='r')

            # use pyqtgraph to plot data
            self.VoltagePlot = pg.PlotWidget(self)
            self.VoltagePlot.setGeometry(400, 430, 280, 200)
            self.VoltagePlot.setBackground('w')
            self.VoltagePlot.showGrid(x=True, y=True)
            self.VoltagePlot.setLabel('left', 'Voltage', units='V')
            self.VoltagePlot.setLabel('bottom', 'Time', units='s')
            #generate random data
            line6 = self.VoltagePlot.plot([8,9,10,11,12,13,14,15,16,17], [7.15,7.16,7.13,7.12,7.11,7.10,7.11,7.1,7.09,7.09], pen='r')

            # use pyqtgraph to plot data
            self.ParticleCountPlot = pg.PlotWidget(self)
            self.ParticleCountPlot.setGeometry(750, 430, 280, 200)
            self.ParticleCountPlot.setBackground('w')
            self.ParticleCountPlot.showGrid(x=True, y=True)
            self.ParticleCountPlot.setLabel('left', 'Particle Count', units='m')
            self.ParticleCountPlot.setLabel('bottom', 'Time', units='s')
            #generate random data
            line6 = self.ParticleCountPlot.plot([8,9,10,11,12,13,14,15,16,17], [1,2,4,5,6,7,7,8,8,9], pen='r')

       

            
        
            self.show()

        def enableButtonFunction(self):
            print("enableButtonFunction")     

        def disableButtonFunction(self):
            print("disableButtonFunction")
            
        def cleanTelemetryTableButtonFunction(self):
            print("cleanTelemetryTableButtonFunction")
            self.telemetryTable.clearContents()

        def currentBaudrateChanged(self):
            print(self.baudrateSelector.currentText())
            print(self.baudrateSelector.currentIndex())
        
        def currentComChanged(self):
            print(self.comSelector.currentText())
            print(self.comSelector.currentIndex())

        def connectButtonFunction(self):
            print("connectButtonFunction")
            self.progressBar.setValue(30)
            self.progressPercentLabel.setText("30%")

        def disconnectButtonFunction(self):
            print("disconnectButtonFunction")
            self.progressBar.setValue(0)
            self.progressPercentLabel.setText("0%")

        def simulationButtonFunction(self):
            print("simulationButtonFunction")


  


if __name__ == '__main__':
        
        app = QApplication(sys.argv)
        ex = Example()
        sys.exit(app.exec())



        23,345,67,465,7856,34