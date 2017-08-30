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
    dbpath = globals()['PROPS']['TargetServer'] + ":" + globals()['PROPS']['Port'] + "/" + globals()['PROPS']['SID']
    try:
        con = cx_Oracle.connect(globals()['PROPS']['Username'], globals()['PROPS']['Password'], dbpath)
        print("Connection Successful")
        return (True, None)
    except Exception as e:
        print("Connection Failed", e)
        return (False, e)

def execute():
    p = Popen("sample.bat", cwd=os.getcwd())
    stdout, stderr = p.communicate()

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

    globals()['PROPS'] = props
    

class Window(QMainWindow):
    def __init__(self):     
        super(Window, self).__init__()
        self.setGeometry(50, 50, 400, 400)
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

        usernamelbl = QLabel("Username",self)
        usernamelbl.move(20, 200)

        self.username = QLineEdit(self)
        self.username.move(150, 200)
        self.username.setFixedWidth(200)
        self.username.setEnabled(False)

        passwordlbl = QLabel("Password",self)
        passwordlbl.move(20, 240)

        self.password = QLineEdit(self)
        self.password.move(150, 240)
        self.password.setFixedWidth(200)
        self.password.setEnabled(False)

        conbtn = QPushButton("Connect", self)
        conbtn.clicked.connect(self.connect)
        conbtn.move(20,320)

    def connect(self):
        status = connect()

        msg = QMessageBox(self)
        msg.setWindowTitle("Connection Test")
        if status[0]:
            msg.setIcon(QMessageBox.Information)
            msg.setText("Connection Successful")
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Connection Failed")
            msg.setInformativeText(str(status[1]))
        
        msg.exec_()

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
        self.username.setText(globals()['PROPS']['Username'])
        self.password.setText(globals()['PROPS']['Password'])