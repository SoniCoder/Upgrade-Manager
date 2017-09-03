from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ActionScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)
    def sizeHint(self):
        return QSize(400,300)
class ConsoleTE(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
        # self.move(20, 0)
        # self.resize(1240,300)
        # policy = self.sizePolicy()
    # 
        # print(self.sizeAdjustPolicy())
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # self.setAlignment(Qt.AlignCenter)
        pal = QPalette()
        bgc = QColor(0, 0, 0)
        pal.setColor(QPalette.Base, bgc)
        textc = QColor(255, 255, 255)
        pal.setColor(QPalette.Text, textc)
        self.setPalette(pal)
        self.setReadOnly(True)
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont("fonts/UbuntuMono-R.ttf")
        families = font_db.applicationFontFamilies(font_id)[0]
        font = QFont(families, 10)
        self.setFont(font)

class ConnectionScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)
        dblbl = QLabel("Target Database",self)
        dblbl.move(20, 20)
        self.dbserver = QLineEdit(self)
        self.dbserver.move(150, 20)
        self.dbserver.setFixedWidth(200)
        self.dbserver.setReadOnly(True)
        portlbl = QLabel("Port",self)
        portlbl.move(20, 60)

        self.port = QLineEdit(self)
        self.port.move(150, 60)
        self.port.setFixedWidth(200)
        self.port.setReadOnly(True)

        sidlbl = QLabel("SID",self)
        sidlbl.move(20, 100)
        self.sid = QLineEdit(self)
        self.sid.move(150, 100)
        self.sid.setFixedWidth(200)
        self.sid.setReadOnly(True)

        servicelbl = QLabel("Service",self)
        servicelbl.move(20, 140)

        self.service = QLineEdit(self)
        self.service.move(150, 140)
        self.service.setFixedWidth(200)
        self.service.setReadOnly(True)

        self.conbtn = QPushButton("Connect", self)
        self.conbtn.move(20,220)
    def sizeHint(self):
        return QSize(400,300)

class DisplayScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)
        imgLbl = QLabel(self)
        self.layout.addWidget(imgLbl)
        pixmap = QPixmap('images/logoBIGscaled.jpg')
        imgLbl.setPixmap(pixmap)
    def sizeHint(self):
        return QSize(640,600)

class QVLine(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class QHLine(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)