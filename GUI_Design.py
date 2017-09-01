from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ConsoleTE(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        self.move(20, 0)
        self.resize(1240,300)
        pal = QPalette()
        bgc = QColor(0, 0, 0)
        pal.setColor(QPalette.Base, bgc)
        textc = QColor(255, 255, 255)
        pal.setColor(QPalette.Text, textc)
        self.setPalette(pal)
        self.setDisabled(True)
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont("fonts/UbuntuMono-R.ttf")
        families = font_db.applicationFontFamilies(font_id)[0]
        font = QFont(families, 10)
        self.setFont(font)

class ConnectionScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        dblbl = QLabel("Target Database",self)
        dblbl.move(20, 40)
        self.dbserver = QLineEdit(self)
        self.dbserver.move(150, 40)
        self.dbserver.setFixedWidth(200)
        self.dbserver.setEnabled(False)
        portlbl = QLabel("Port",self)
        portlbl.move(20, 80)

        self.port = QLineEdit(self)
        self.port.move(150, 80)
        self.port.setFixedWidth(200)
        self.port.setEnabled(False)

        sidlbl = QLabel("SID",self)
        sidlbl.move(20, 120)
        self.sid = QLineEdit(self)
        self.sid.move(150, 120)
        self.sid.setFixedWidth(200)
        self.sid.setEnabled(False)

        servicelbl = QLabel("Service",self)
        servicelbl.move(20, 160)

        self.service = QLineEdit(self)
        self.service.move(150, 160)
        self.service.setFixedWidth(200)
        self.service.setEnabled(False)

        self.conbtn = QPushButton("Connect", self)
        self.conbtn.move(20,240)
