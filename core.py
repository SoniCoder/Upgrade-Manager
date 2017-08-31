import cx_Oracle
import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *
from subprocess import Popen

from config import *

def connect():
    dbpath = globals()['PROPS']['TargetServer'] + ":" + globals()['PROPS']['Port'] + "/" + globals()['PROPS']['Service']
    for username, password in globals()['SCHEMA_CREDS_KEYS']:
        print("Attempting Connection with Username %s and Password %s"%(globals()['PROPS'][username], globals()['PROPS'][password]))
        try:
            con = cx_Oracle.connect(globals()['PROPS'][username], globals()['PROPS'][password], dbpath)
            print("Connection Successful")
            con.close()
        except Exception as e:
            print("Connection Failed", e)
            return (False, e, "Connection Attempt Failed! Username:%s"%(globals()['PROPS'][username]))
    return (True, None, None)

def execute():
    p = Popen("sample.bat", cwd=os.getcwd())
    stdout, stderr = p.communicate()

def init():
    globals()['SCHEMA_CREDS_KEYS'] = [('System_Username', 'System_Password'), ('WebWORKS_Username', 'WebWORKS_Password'), ('ABPP_Username', 'ABPP_Password'), ('Monitor_Username', 'Monitor_Password'), ('JDA_SYSTEM_Username', 'JDA_SYSTEM_Password'), ('SCPO_Username', 'SCPO_Password')]


def queryComponents():
    dbpath = globals()['PROPS']['TargetServer'] + ":" + globals()['PROPS']['Port'] + "/" + globals()['PROPS']['Service']
    con = cx_Oracle.connect(globals()['PROPS']['WebWORKS_Username'], globals()['PROPS']['WebWORKS_Password'], dbpath)
    cur = con.cursor()
    cur.execute('select DISTINCT(SCHEMA_NAME) from csm_application')
    globals()['COMPONENTS'] = []
    for result in cur:
        globals()['COMPONENTS'].append(result[0])
    cur.close()
    cur = con.cursor()
    cur.execute("select VALUE from csm_schema_log where name='DATABASE_VERSION'")
    result = cur.fetchone()
    globals()['COMPVER'] = result[0]
    cur.close()
    con.close()   

    targetv_path = globals()['PROPS']['JDA_HOME'] + '\\' + 'install\\platform.version'
    f = open(targetv_path)
    line = f.readline()
    line = f.readline()
    targetVersion = line.split(':')[1].strip()
    globals()['TARGET_VERSION'] = targetVersion
    f.close()

def readProperties():
    separator = ":"
    props = {}
    
    with open('upgrade.properties') as f:

        for line in f:
            if separator in line:

                # Find the name and value by splitting the string
                name, value = line.split(separator, 1)

                # Assign key value pair to dict
                # strip() removes white space from the ends of strings
                props[name.strip()] = value.strip()

    props['JDA_HOME'] = props['JDA_HOME'].replace('-', ':')
    globals()['PROPS'] = props
    
class VersionCheckerWindow(QMainWindow):
    def __init__(self):     
        super(VersionCheckerWindow, self).__init__()
        self.setGeometry(50, 50, 400, 40*len(globals()['COMPONENTS']) + 80)
        self.setWindowTitle("Application Components Version List")
        self.setWindowIcon(QIcon('icon.png'))
        self.design()
        self.show()

    def design(self):
        vtable = QTableWidget(self)
        tableWidth = 400
        vtable.resize(tableWidth, 40*len(globals()['COMPONENTS']))
        vtable.setRowCount(len(globals()['COMPONENTS']))
        vtable.setColumnCount(3)
        vtable.setColumnWidth(0, tableWidth/3 - 6)
        vtable.setColumnWidth(1, tableWidth/3 - 6)
        vtable.setColumnWidth(2, tableWidth/3 - 6)
        vtable.setHorizontalHeaderLabels("Component;Current Version;Target Version;".split(";"))

        curRow = 0
        for i in globals()['COMPONENTS']:
            vtable.setItem(curRow,0, QTableWidgetItem(i))
            vtable.setItem(curRow,1, QTableWidgetItem(globals()['COMPVER']))
            vtable.setItem(curRow,2, QTableWidgetItem(globals()['TARGET_VERSION']))
            curRow += 1

        btn = QPushButton("Migrate", self)
        btn.move(20,self.height() - 60)

class Window(QMainWindow):
    def __init__(self):     
        super(Window, self).__init__()
        init()
        self.setGeometry(50, 50, 400, 320)
        self.setWindowTitle("Upgrade Manager")
        self.setWindowIcon(QIcon('icon.png'))
        self.design()
        self.load()
        self.show()
	
    def design(self):
        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')

        loadPropAction= QAction("&Load Property File", self)
        loadPropAction.setShortcut("Ctrl+L")
        loadPropAction.setStatusTip('Load upgrade.properties')
        loadPropAction.triggered.connect(self.readProperties)
        
        fileMenu.addAction(loadPropAction)

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

        # usernamelbl = QLabel("Username",self)
        # usernamelbl.move(20, 200)

        # self.username = QLineEdit(self)
        # self.username.move(150, 200)
        # self.username.setFixedWidth(200)
        # self.username.setEnabled(False)

        # passwordlbl = QLabel("Password",self)
        # passwordlbl.move(20, 240)

        # self.password = QLineEdit(self)
        # self.password.move(150, 240)
        # self.password.setFixedWidth(200)
        # self.password.setEnabled(False)

        conbtn = QPushButton("Connect", self)
        conbtn.clicked.connect(self.connect)
        conbtn.move(20,240)

    def connect(self):
        status = connect()

        msg = QMessageBox(self)
        msg.setWindowTitle("Connection Test")
        if status[0]:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Connection Successful")
            msg.buttonClicked.connect(self.con_success)
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Connection Failed")
            msg.setInformativeText(str(status[1]))
            msg.setDetailedText(status[2])
        msg.exec_()

    def con_success(self):
        queryComponents()
        globals()['VSCHKINST'] = VersionCheckerWindow()
        self.hide()

    def execute(self):
        execute()

    def load(self):
        self.readProperties()

    def readProperties(self):
        readProperties()
        self.dbserver.setText(globals()['PROPS']['TargetServer'])
        self.port.setText(globals()['PROPS']['Port'])
        self.sid.setText(globals()['PROPS']['SID'])
        self.service.setText(globals()['PROPS']['Service'])
        # self.username.setText(globals()['PROPS']['Username'])
        # self.password.setText(globals()['PROPS']['Password'])