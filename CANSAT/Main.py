import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from MainGUI import GUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec())
