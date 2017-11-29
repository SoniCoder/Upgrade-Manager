from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from augmentedWidgets import *

class ActionScreen(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)
    def sizeHint(self):
        pass
        return QSize(400,300)

class ErrorTE(QTextEdit):
    def __init__(self, parent = None):
        QTextEdit.__init__(self, parent)
        pal = QPalette()
        bgc = QColor(22, 54, 102)
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
        self.append("Error Console:")
        self.append("")



class ComponentTable(QTableWidget):
    def __init__(self, parent = None):
        QTableWidget.__init__(self, parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cols = 3
    def resizeEvent(self, event):
        self.setColumnWidth(0, event.size().width()/self.cols)
        self.setColumnWidth(1, event.size().width()/self.cols)
        self.setColumnWidth(2, event.size().width()/self.cols)

class ConsoleTE(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)
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
        # font_db = QFontDatabase()
        # font_id = font_db.addApplicationFont("fonts/UbuntuMono-R.ttf")
        # families = font_db.applicationFontFamilies(font_id)[0]
        # font = QFont(families, 10)
        # self.setFont(font)

        self.outerlayout = QVBoxLayout(self)

        scroll = QScrollArea(self)
        self.outerlayout.addWidget(scroll)  
        scroll.setWidgetResizable(True)

        scrollContent = QWidget(scroll)

        p = scrollContent.palette()
        bgcol = QColor(22, 54, 102)
        p.setColor(scrollContent.backgroundRole(), bgcol)
        
        scrollContent.setPalette(p)
        scrollContent.setAutoFillBackground(True)

        self.layout = QVBoxLayout(scrollContent)
        scrollContent.setLayout(self.layout)

        scroll.setWidget(scrollContent)



        self.imgLbl = JDALogoLabel(self)
        self.layout.addWidget(self.imgLbl)
        pixmap = QPixmap('images/logoBIGscaled.jpg')
        self.imgLbl.setPixmap(pixmap)

        self.progress = ProgressScreen(self)
        self.layout.addWidget(self.progress)
        self.progress.hide()

        self.tview = TableViewScreen(self)
        self.layout.addWidget(self.tview)
        self.tview.hide()

        self.errorView = ErrorTableScreen(self)
        self.layout.addWidget(self.errorView)
        self.errorView.hide()

        self.currentWidget = self.imgLbl

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.outerlayout.setContentsMargins(0, 0, 0, 0)

    def updateScreen(self,scr):
        self.currentWidget.hide()
        scr.show()
        self.currentWidget = scr

class ErrorTableScreen(QTableWidget):
    def __init__(self,parent=None):
        QTableWidget.__init__(self, parent)
        # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setColumnCount(2)
        header = "Mark Fixed;Error Description"
        self.setHorizontalHeaderLabels(header.split(";"))
        self.rowc = 0
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        
    def addError(self, text):
        self.rowc += 1
        self.setRowCount(self.rowc)
        self.setItem(self.rowc - 1, 1, QTableWidgetItem(text))
        self.setCellWidget(self.rowc - 1, 0, QCenteredCheckBox())
        self.resizeColumnsToContents()

class JDALogoLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self)
        self.setScaledContents( True )
        self.setSizePolicy( QSizePolicy.Ignored, QSizePolicy.Ignored )

class TableViewScreen(QTableWidget):
    def __init__(self,parent=None):
        QTableWidget.__init__(self)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cols = 2

    def setData(self, lst, header):
        rows = len(lst)
        self.setRowCount(rows)
        collbls = header.split(";")
        cols = len(collbls)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(collbls)
        curRow = 0
        for row in lst:
            for col_i in range(len(row)):
                self.setItem(curRow,col_i, QTableWidgetItem(row[col_i]))
            curRow += 1
        self.cols = cols
        # print("Firing Resize Event, cols:", self.cols)
        # self.resize(self.geometry().width(), self.geometry().height())
        # print("Resize Event Fired", self.cols)
        for c_i in range(self.cols):
            self.setColumnWidth(c_i, self.geometry().width()/self.cols)

    def resizeEvent(self, event):
        for c_i in range(self.cols):
            self.setColumnWidth(c_i, event.size().width()/self.cols)

class FULLProgressBar(QProgressBar):
    def __init__(self, parent = None):
        QProgressBar.__init__(self, parent)
        self.thisLayout = QHBoxLayout(self)
        self.middleLabel = QCenteredLabel(self)
        self.thisLayout.addWidget(self.middleLabel)        
        self.thisLayout.setContentsMargins(0, 0, 0, 0)
        self.completed = 0
        self.maxTasks = 0
    def updateCompleted(self, n):
        self.completed = n
        self.updateStatus()
    def updateStatus(self):
        percent = None
        if self.maxTasks == 0:
            percent = 0
        else:
            percent = int(100*(self.completed/self.maxTasks))
        self.setValue(percent)
        self.middleLabel.setText("Completed Tasks %d of %d"%(self.completed, self.maxTasks))
    def setMaxTasks(self, n):
        self.maxTasks = n
        self.updateStatus()
class ProgressScreen(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self)
        self.layout = HBOXNOMG(self)

        self.sno = QWidget()
        self.layout.addWidget(self.sno)
        self.snoLayout = VBOXNOEXMG(self.sno)
        self.snoLayout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(QVLine())
        self.snoHeading = QCenteredLabel("S. No.")
        self.snoLayout.addWidget(self.snoHeading)
        self.snoLayout.addWidget(QHLine())
        self.snoHeading.setObjectName("Headingsno")

        self.phaseSide = QWidget()
        self.layout.addWidget(self.phaseSide)
        self.phaseLayout = VBOXNOEXMG(self.phaseSide)
        self.phaseLayout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(QVLine())
        self.phaseHeading = QCenteredLabel("Phase")
        self.phaseLayout.addWidget(self.phaseHeading)
        self.phaseLayout.addWidget(QHLine())
        self.phaseHeading.setObjectName("Headingphase")


        self.leftSide = QWidget()
        self.layout.addWidget(self.leftSide)
        self.leftLayout = VBOXNOEXMG(self.leftSide)
        self.leftLayout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(QVLine())
        self.leftHeading = QCenteredLabel("Task Type")
        self.leftLayout.addWidget(self.leftHeading)
        self.leftLayout.addWidget(QHLine())
        self.leftHeading.setObjectName("HeadingLeft")

        self.middleSide = QWidget()
        self.layout.addWidget(self.middleSide)
        self.middleLayout = VBOXNOEXMG(self.middleSide)
        self.middleLayout.setAlignment(Qt.AlignTop)
        self.middleHeading = QCenteredLabel("Action")
        self.middleLayout.addWidget(self.middleHeading)
        self.middleLayout.addWidget(QHLine())
        self.middleHeading.setObjectName("HeadingMiddle")

        self.layout.addWidget(QVLine())
        self.rightSide = QWidget()
        self.rightLayout = VBOXNOEXMG(self.rightSide)
        self.rightLayout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.rightSide)
        self.leftList = []
        self.rightList = []
        self.middleList = []
        self.rightHeading = QCenteredLabel("Status")
        self.rightHeading.setObjectName("HeadingRight")
        self.rightLayout.addWidget(self.rightHeading)
        self.rightLayout.addWidget(QHLine())
        
        self.setStyleSheet('#HeadingMiddle, #HeadingLeft, #HeadingRight, #Headingsno, #Headingphase { font-weight: bold; } QLabel { color: white; }')

class TaskMonitor(QWidget):
    def __init__(self, parent= None):
        QWidget.__init__(self, parent)
        self.hide()
        self.thisLayout = VBOXNOEXMG(self)
        self.thisLayout.setAlignment(Qt.AlignTop)
        self.errorBox = ErrorTE(self)
        self.thisLayout.addWidget(self.errorBox)

