import sys
from collections import deque
import serial.tools.list_ports
import csv
from datetime import datetime

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPixmap, QFont
from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QComboBox, QProgressBar,
    QFrame, QAbstractItemView, QTableWidget, QTableWidgetItem
)
import pyqtgraph as pg

# Import your telemetry class
from telemetry import XBeeReceiver


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(900)
        self.setFixedWidth(1500)
        self.setWindowTitle('Team Avinya - Ground Station Software')

        # --- Logo ---
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap('AVINYA_LOGO.png'))
        self.logo.setGeometry(QtCore.QRect(695, 10, 150, 150))
        self.logo.setScaledContents(True)
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("border: 2px solid rgb(179, 226, 229);")
        self.logo.setMask(self.logo.pixmap().mask())

        # --- Axis View ---
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(1189, 180, 300, 300)
        self.imageLabel.setPixmap(QPixmap("AVINYA_LOGO.png"))
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setStyleSheet("background-color: white")
        self.imageLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.imageLabel.show()

        # --- Map View ---
        self.imageLabel = QLabel(self)
        self.imageLabel.setGeometry(1189, 524, 300, 300)
        self.imageLabel.setPixmap(QPixmap("CANSAT_LOGO.png"))
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setStyleSheet("background-color: white")
        self.imageLabel.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.imageLabel.show()

        # --- Background ---
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(50, 61, 65))
        self.setPalette(p)

        # --- State Variables ---
        self.receiver = None
        self.poll_timer = None
        self._last_processed_idx = 0
        self._pkt_counter = 0

        # Rolling buffers for plotting
        self.max_points = 300
        self.buf_t = deque(maxlen=self.max_points)
        self.buf_alt = deque(maxlen=self.max_points)
        self.buf_temp = deque(maxlen=self.max_points)
        self.buf_pres = deque(maxlen=self.max_points)
        self.buf_airs = deque(maxlen=self.max_points)
        self.buf_volt = deque(maxlen=self.max_points)
        self.buf_part = deque(maxlen=self.max_points)

        # --- CSV Logging Setup ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f"telemetry_log_{timestamp}.csv"
        self.csv_file = open(self.csv_filename, mode='w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            "TEAM_ID", "MISSION_TIME", "PACKET_COUNT", "ALTITUDE", "PRESSURE", "TEMPERATURE",
            "VOLTAGE", "GPS_TIME", "GPS_LAT", "GPS_LON", "GPS_ALT", "GPS_SATS",
            "AIR_SPEED", "PARTICLE_COUNT", "PITCH", "ROLL", "YAW"
        ])
        self.csv_file.flush()
        print(f"[LOG] Telemetry CSV file created: {self.csv_filename}")

        self.initUI()

    # ---------------- UI ----------------
    def initUI(self):
        # --- Command Buttons ---
        self.simulationButton = QPushButton('Calibrate', self)
        self.simulationButton.setGeometry(QtCore.QRect(315, 15, 100, 30))
        self.simulationButton.clicked.connect(self.simulationButtonFunction)

        self.enableButton = QPushButton('Enable', self)
        self.enableButton.setGeometry(QtCore.QRect(315, 45, 100, 30))
        self.enableButton.clicked.connect(self.enableButtonFunction)

        self.disableButton = QPushButton('Disable', self)
        self.disableButton.setGeometry(QtCore.QRect(315, 75, 100, 30))
        self.disableButton.clicked.connect(self.disableButtonFunction)

        self.simButton = QPushButton('Simulation', self)
        self.simButton.setGeometry(QtCore.QRect(315, 105, 100, 30))
        self.simButton.clicked.connect(self.simulationButtonFunction)

        # --- Dynamic COM port detection ---
        self.comSelector = QComboBox(self)
        self.comSelector.setGeometry(QtCore.QRect(100, 45, 120, 35))
        self.populatePorts()
        self.comSelector.currentTextChanged.connect(self.currentComChanged)

        self.refreshPortsButton = QPushButton('↻', self)
        self.refreshPortsButton.setGeometry(QtCore.QRect(225, 45, 30, 30))
        self.refreshPortsButton.clicked.connect(self.refreshPorts)

        self.baudrateSelector = QComboBox(self)
        self.baudrateSelector.setGeometry(QtCore.QRect(260, 45, 100, 35))
        self.baudrateSelector.addItems(['9600', '115200', '230400', '460800', '921600'])
        self.baudrateSelector.setCurrentText('115200')
        self.baudrateSelector.currentTextChanged.connect(self.currentBaudrateChanged)

        # --- Connect / Disconnect ---
        self.connectButton = QPushButton('Connect', self)
        self.connectButton.setGeometry(QtCore.QRect(100, 85, 100, 30))
        self.connectButton.clicked.connect(self.connectButtonFunction)

        self.disconnectButton = QPushButton('Disconnect', self)
        self.disconnectButton.setGeometry(QtCore.QRect(200, 85, 100, 30))
        self.disconnectButton.clicked.connect(self.disconnectButtonFunction)

        # --- Progress ---
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(QtCore.QRect(870, 50, 250, 30))
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        self.progressBarLabel = QLabel("Mission Progress", self)
        self.progressBarLabel.setFont(QFont('Arial', 15))
        self.progressBarLabel.setGeometry(QtCore.QRect(800, 17, 200, 35))
        self.progressBarLabel.setStyleSheet("color: rgb(179, 226, 229);")

        self.progressPercentLabel = QLabel("0%", self)
        self.progressPercentLabel.setFont(QFont('Arial', 15))
        self.progressPercentLabel.setGeometry(QtCore.QRect(1050, 27, 100, 20))
        self.progressPercentLabel.setStyleSheet("color: rgb(179, 226, 229);")

        # --- Telemetry Table ---
        self.telemetryTable = QTableWidget(self)
        self.telemetryTable.setGeometry(QtCore.QRect(20, 680, 1159, 200))
        self.telemetryTable.setColumnCount(17)
        self.telemetryTable.setRowCount(0)
        self.telemetryTable.setHorizontalHeaderLabels([
            "Team ID", "Mission Time", "Packet Count", "Altitude", "Pressure",
            "Temp", "Volt", "GPS TIME", "GPS Latitude", "GPS Longtitude",
            "GPS Altitude", "GPS SATs", "Air Speed", "Particle Count",
            "Pitch", "Roll", "Yaw"
        ])
        self.telemetryTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.telemetryTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.telemetryTable.setAlternatingRowColors(True)
        self.telemetryTable.setShowGrid(True)
        self.telemetryTable.scrollToBottom()

        self.telemetryTableButton = QPushButton('Clear Table', self)
        self.telemetryTableButton.setGeometry(QtCore.QRect(1180, 855, 100, 30))
        self.telemetryTableButton.clicked.connect(self.cleanTelemetryTableButtonFunction)

        # --- Dynamic labels ---
        self.altitudeText = QLabel("Altitude: - m", self)
        self.altitudeText.setGeometry(QtCore.QRect(910, 88, 150, 20))
        self.altitudeText.setFont(QFont('Arial', 13))
        self.altitudeText.setStyleSheet("background-color: white")

        self.timeText = QLabel("Mission Time: 00:00:00", self)
        self.timeText.setGeometry(QtCore.QRect(460, 45, 270, 30))
        self.timeText.setFont(QFont('Arial', 15))
        self.timeText.setAlignment(Qt.AlignCenter)
        self.timeText.setStyleSheet("background-color: white")

        self.pitchRollYawText = QLabel("Pitch: -    Roll: -    Yaw: -", self)
        self.pitchRollYawText.setGeometry(QtCore.QRect(1189, 830, 300, 20))
        self.pitchRollYawText.setFont(QFont('Arial', 12))
        self.pitchRollYawText.setAlignment(Qt.AlignCenter)
        self.pitchRollYawText.setStyleSheet("background-color: white")

        self.latitudeLongitudeAltitudeSatsText = QLabel("Lat: -    Long: -    Alt: -", self)
        self.latitudeLongitudeAltitudeSatsText.setGeometry(QtCore.QRect(1060, 485, 470, 20))
        self.latitudeLongitudeAltitudeSatsText.setFont(QFont('Arial', 11))
        self.latitudeLongitudeAltitudeSatsText.setAlignment(Qt.AlignCenter)
        self.latitudeLongitudeAltitudeSatsText.setStyleSheet("background-color: white")

        # --- Plots ---
        self.AltiudePlot = self.makePlot(50, 180, "Altitude", "m")
        self.curve_alt = self.AltiudePlot.plot([], [], pen='r')

        self.TempraturePlot = self.makePlot(400, 180, "Temperature", "°C")
        self.curve_temp = self.TempraturePlot.plot([], [], pen='r')

        self.PressurePlot = self.makePlot(750, 180, "Pressure", "Pa")
        self.curve_pres = self.PressurePlot.plot([], [], pen='r')

        self.AirSpeedPlot = self.makePlot(50, 430, "Air Speed", "m/s")
        self.curve_airs = self.AirSpeedPlot.plot([], [], pen='r')

        self.VoltagePlot = self.makePlot(400, 430, "Voltage", "V")
        self.curve_volt = self.VoltagePlot.plot([], [], pen='r')

        self.ParticleCountPlot = self.makePlot(750, 430, "Particle Count", "")
        self.curve_part = self.ParticleCountPlot.plot([], [], pen='r')

        self.show()

    # --- Helper: make plots ---
    def makePlot(self, x, y, title, unit):
        w = pg.PlotWidget(self)
        w.setGeometry(QtCore.QRect(x, y, 280, 200))
        w.setBackground('w')
        w.showGrid(x=True, y=True)
        w.setLabel('left', title, units=unit)
        w.setLabel('bottom', 'Time', units='s')
        return w

    # --- COM port helpers ---
    def populatePorts(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if not ports:
            ports = ["(No ports found)"]
        self.comSelector.addItems(ports)

    def refreshPorts(self):
        self.comSelector.clear()
        self.populatePorts()

    # --- Button handlers ---
    def enableButtonFunction(self): print("Enable clicked")
    def disableButtonFunction(self): print("Disable clicked")
    def simulationButtonFunction(self): print("Simulation clicked")
    def cleanTelemetryTableButtonFunction(self): self.telemetryTable.setRowCount(0)

    # --- Connection Management ---
    def connectButtonFunction(self):
        try:
            port = self.comSelector.currentText()
            baud = int(self.baudrateSelector.currentText())
            print(f"connectButtonFunction -> Opening {port} @ {baud}")

            if "(No ports found)" in port:
                print("[GUI] No valid COM port selected.")
                return

            self.disconnectButtonFunction()
            self.receiver = XBeeReceiver(port, baud)
            self.receiver.start()
            print("[GUI] Start command sent — now listening for telemetry...")

            self._last_processed_idx = 0
            self._pkt_counter = 0
            for buf in [self.buf_t, self.buf_alt, self.buf_temp, self.buf_pres,
                        self.buf_airs, self.buf_volt, self.buf_part]:
                buf.clear()

            self.poll_timer = QTimer(self)
            self.poll_timer.timeout.connect(self.poll_xbee)
            self.poll_timer.start(50)

            self.progressBar.setValue(30)
            self.progressPercentLabel.setText("30%")

        except Exception as e:
            print(f"[GUI] Connect failed: {e}")

    def disconnectButtonFunction(self):
        print("disconnectButtonFunction")
        if self.poll_timer:
            self.poll_timer.stop()
            self.poll_timer = None
        if self.receiver:
            try:
                self.receiver.stop()
            except Exception as e:
                print(f"[GUI] Error stopping receiver: {e}")
        self.receiver = None
        self.progressBar.setValue(0)
        self.progressPercentLabel.setText("0%")

    # --- Poll & update ---
    def poll_xbee(self):
        if not self.receiver:
            return

        pkts = self.receiver.data_packets
        while self._last_processed_idx < len(pkts):
            raw = pkts[self._last_processed_idx]
            self._last_processed_idx += 1
            try:
                text = raw.decode('utf-8', errors='ignore').strip() if isinstance(raw, (bytes, bytearray)) else str(raw).strip()
                if not text:
                    continue
                data = self.parse_packet(text)
                if not data:
                    continue

                self._pkt_counter += 1
                self.update_table(data)
                self.update_labels(data)
                self.update_plots(data)
                self.write_csv_row(data)  # ✅ log to CSV here

            except Exception as e:
                print(f"[GUI] Packet parse error: {e}")

    # --- Write telemetry to CSV ---
    def write_csv_row(self, d):
        try:
            self.csv_writer.writerow([
                d["team_id"], d["mission_time"], d["packet_count"],
                f"{d['altitude']:.2f}", f"{d['pressure']:.2f}", f"{d['temp']:.2f}",
                f"{d['volt']:.2f}", d["gps_time"], f"{d['gps_lat']:.6f}",
                f"{d['gps_lon']:.6f}", f"{d['gps_alt']:.2f}", d["gps_sats"],
                f"{d['air_speed']:.2f}", f"{d['particle']:.2f}",
                f"{d['pitch']:.3f}", f"{d['roll']:.3f}", f"{d['yaw']:.3f}"
            ])
            self.csv_file.flush()
        except Exception as e:
            print(f"[LOG] CSV write error: {e}")

    # --- Close safely ---
    def closeEvent(self, event: QtGui.QCloseEvent):
        try:
            self.disconnectButtonFunction()
            if hasattr(self, "csv_file") and not self.csv_file.closed:
                self.csv_file.close()
                print(f"[LOG] CSV file saved: {self.csv_filename}")
        finally:
            event.accept()
