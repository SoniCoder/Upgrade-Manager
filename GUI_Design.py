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
        dblbl.setFixedWidth(200)
        self.dbserver = QLineEdit(self)
        self.dbserver.move(180, 20)
        self.dbserver.setFixedWidth(200)
        self.dbserver.setReadOnly(True)
        portlbl = QLabel("Port",self)
        portlbl.move(20, 60)

        self.port = QLineEdit(self)
        self.port.move(180, 60)
        self.port.setFixedWidth(200)
        self.port.setReadOnly(True)

        sidlbl = QLabel("SID",self)
        sidlbl.move(20, 100)
        self.sid = QLineEdit(self)
        self.sid.move(180, 100)
        self.sid.setFixedWidth(200)
        self.sid.setReadOnly(True)

        servicelbl = QLabel("Service",self)
        servicelbl.move(20, 140)

        self.service = QLineEdit(self)
        self.service.move(180, 140)
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
        self.imgLbl = QLabel(self)
        self.layout.addWidget(self.imgLbl)
        pixmap = QPixmap('images/logoBIGscaled.jpg')
        self.imgLbl.setPixmap(pixmap)

        self.testLbl = QLabel("0", self)
        self.layout.addWidget(self.testLbl)
        self.testLbl.hide()

        self.statGather = StatGatherScreen(self)
        self.layout.addWidget(self.statGather)
        self.statGather.hide()

        self.rowCount = RowCountScreen(self)
        self.layout.addWidget(self.rowCount)
        self.rowCount.hide()
        self.currentWidget = self.imgLbl

    def sizeHint(self):
        return QSize(640,700)

class RowCountScreen(QTableWidget):
    def __init__(self,parent=None):
        QTableWidget.__init__(self)
    def setData(self, lst, header):
        self.setRowCount(len(lst))
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(header.split(";"))
        self.setColumnWidth(0, self.width()/2)
        self.setColumnWidth(1, self.width()/2)
        curRow = 0
        for tb, cnt in lst:
            self.setItem(curRow,0, QTableWidgetItem(tb))
            self.setItem(curRow,1, QTableWidgetItem(cnt))
            curRow += 1

class StatGatherScreen(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self)
        self.layout = QHBoxLayout(self)
        self.leftSide = QWidget()
        self.leftLayout = QVBoxLayout(self.leftSide)
        self.leftLayout.setAlignment(Qt.AlignTop)
        self.rightSide = QWidget()
        self.rightLayout = QVBoxLayout(self.rightSide)
        self.rightLayout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.leftSide)
        self.layout.addWidget(self.rightSide)
        self.leftList = []
        self.rightList = []




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