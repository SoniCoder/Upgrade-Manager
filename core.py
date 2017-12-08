"""
AUTHOR: Hritik Soni

Description: Contains Major Portions of Code for functioning of Interface


"""

import cx_Oracle #This library is used by python to interact with oracle
import datetime
import os
import threading #This library is used to create multiple threads
import sys

import globs #This module is being used to share code across all modules

#The following import are required for GUI interface
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *

from collections import deque
from shutil import copyfile, copy
from subprocess import Popen, PIPE
from time import sleep

from errorhandling import *
from GUI_Design import *
from signals import *
from task import Task, updater, prepareTasks 
from commands import *


def connect():
    """
    Checks Connections to all Users
    """

    dbpath = globs.props['TargetServer'] + ":" + globs.props['Port'] + "/" + globs.props['Service']
    
    print("Checking Connection with SYSTEM USER")
    username, password = globs.SYSTEM_USER_KEYS
    try:
        # Try connection with SYSTEM User
        con = cx_Oracle.connect(globs.props[username], globs.props[password], dbpath)
        print("Connection Successful")
        con.close()
    except Exception as e:
        print("Connection Failed", e)
        return (False, e, "Connection Attempt Failed! Username:%s"%(globs.props[username]))
    con = cx_Oracle.connect(globs.props[username], globs.props[password], dbpath)    
    print("Checking JDA_SYSTEM existence")
    cur = con.cursor()
    # Check whether JDA_SYSTEM exists
    cur.execute("select * from ALL_USERS where username = 'JDA_SYSTEM'")
    cur.fetchall()
    if(cur.rowcount==1):
        print("User Exists")
    else:
        # IF JDA_SYSTEM doesn't exist, create it
        print("Creating USER JDA_SYSTEM")
        createJDASYSTEM()
    cur.close()

    # Check for ABPP User and create it if it doesn't exist
    print("Checking ABPP User existence")
    cur = con.cursor()
    cur.execute("select * from ALL_USERS where username = 'ABPPMGR'")
    cur.fetchall()
    if(cur.rowcount==1):
        print("User Exists")
    else:
        globs.ABPP_CREATED = True
        print("Creating USER ABPPMGR")
        createABPPMGRUSER()
    cur.close()

    con.close()


    # Check connection with all users
    for username, password in globs.SCHEMA_CREDS_KEYS:
        print("Attempting Connection with Username %s and Password %s"%(globs.props[username], globs.props[password]))
        try:
            con = cx_Oracle.connect(globs.props[username], globs.props[password], dbpath)
            print("Connection Successful")
            con.close()
        except Exception as e:
            print("Connection Failed", e)
            return (False, e, "Connection Attempt Failed! Username:%s"%(globs.props[username]))
    print()

    return (True, None, None)

def createABPPMGRGRANTS():
    """
    Function to provide appropriate grants to ABPP user
    """
    sqlcommand = bytes('@sqls/ABPP_GRANTS', 'utf-8')
    runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)

def createABPPMGRUPDATE():
    """
    Function to run updateAbppSchema batch script
    """
    progPath = os.getcwd()
    scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
    os.chdir(scriptFolder)
    session = Popen(['updateAbppSchema.cmd', '-coreServices'], stdout=globs.LogPipe, stdin = PIPE)
    session.communicate()
    os.chdir(progPath)

def createABPPMGRUSER():
    """
    Function to create ABPP User
    """
    password = globs.props['ABPP_Password']  
    sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\setup\\cr_abpp_user '+password, 'utf-8')
    stdout, stdin = runSQLQuery(sqlcommand, globs.props['System_Username'])
    print(stdout.decode('ascii'))

def createABPPMGRSCHEMA():
    """
    Function to run createAbppSchema batch script
    """
    progPath = os.getcwd()
    scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
    os.chdir(scriptFolder)
    session = Popen(['createAbppSchema.cmd'], stdin=PIPE, stdout=globs.LogPipe)
    session.communicate()
    os.chdir(progPath)

def createJDASYSTEM():
    user = globs.props['JDA_SYSTEM_Username']
    password = globs.props['JDA_SYSTEM_Password']  
    sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\setup\\create_jda_system '+password, 'utf-8')
    stdout, stdin = runSQLQuery(sqlcommand, globs.props['System_Username'])
    print(stdout.decode('ascii'))
    
    
def createManugistics():
    user = globs.props['JDA_SYSTEM_Username']
    print("Creating the ManugisticsPkg table in the JDA System schema")
    sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\platform\\ManugisticsPkg '+user, 'utf-8')
    stdout, stdin = runSQLQuery(sqlcommand, user, globs.LogPipe)
    
def createLogFolders():
    """
    This function creates a folder for archiving all logs
    """
    os.chdir("ARCHIVES")
    logFolder = datetime.datetime.now().strftime("ARCHIVE_%d_%b_%Y_%H_%M_%S_0")
    while logFolder in os.listdir():
        split = logFolder.split('_')
        curIndex = int(split[7])
        nextIndex = curIndex + 1
        split[7] = str(nextIndex)
        logFolder = '_'.join(split)
    os.mkdir(logFolder)
    os.chdir(logFolder)
    os.mkdir("Premigration")
    os.mkdir("Migration")
    os.mkdir("Postmigration")
    os.mkdir("Other")
    print("Storing All Logs in ARCHIVES/%s"%logFolder)
    globs.ARCHIVEFOLDER = os.getcwd()
    os.chdir(globs.PROGDIR)

class EmittingStream(QObject):
    """
    Signal class to redirect all output to custom console
    """
    textWritten = pyqtSignal(str)
    
    def __init__(self):
        QObject.__init__(self)
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        

    def write(self, text):
        self.textWritten.emit(str(text))

    def fileno(self):
        """
        Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def flush(self):
        pass

class LogPipe(threading.Thread):
    """
    Thread Class to listen for output to its instance and pass it to custom console
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            print(line.strip('\n'))
        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)



           
    
# class Task():
#     lblcntr = 0
#     def __init__(self, op, schema = None, labels = False, TaskType = "Accessory Task", Action = "None", phase = "None"):
#         self.schema = schema
#         self.op = op
#         self.status = 0
#         self.localid = 0
#         self.labels = labels
#         self.phase = phase
#         self.TaskType = TaskType
#         self.Action = Action
#         self.outputStatus = ""
#         if self.labels:
#             self.localid = Task.lblcntr
#             dispLbl = QCenteredLabel(str(self.localid + 1))
#             dispLbl.setFixedHeight(30)
#             globs.DISP_SCREEN.progress.snoLayout.addWidget(dispLbl)
#             globs.DISP_SCREEN.progress.snoLayout.addWidget(QHLine())

#             dispLbl = QCenteredLabel(self.phase)
#             dispLbl.setFixedHeight(30)
#             globs.DISP_SCREEN.progress.phaseLayout.addWidget(dispLbl)
#             globs.DISP_SCREEN.progress.phaseLayout.addWidget(QHLine())


#             dispLbl = QCenteredLabel(TaskType)
#             dispLbl.setFixedHeight(30)
#             globs.DISP_SCREEN.progress.leftList.append(dispLbl)
#             globs.DISP_SCREEN.progress.leftLayout.addWidget(dispLbl)
#             globs.DISP_SCREEN.progress.leftLayout.addWidget(QHLine())

#             dispLbl = QCenteredLabel(Action)
#             dispLbl.setFixedHeight(30)            
#             globs.DISP_SCREEN.progress.middleList.append(dispLbl)
#             globs.DISP_SCREEN.progress.middleLayout.addWidget(dispLbl)
#             globs.DISP_SCREEN.progress.middleLayout.addWidget(QHLine())
            
#             imgLbl = QCenteredLabel()
#             pixmap = QPixmap('images/white.png')
#             imgLbl.setPixmap(pixmap)
#             globs.DISP_SCREEN.progress.rightList.append(imgLbl)
#             globs.DISP_SCREEN.progress.rightLayout.addWidget(imgLbl)
#             globs.DISP_SCREEN.progress.rightLayout.addWidget(QHLine())
#             Task.lblcntr += 1
#     def runtask(self):        
#         self.status = 1
#         if self.op == 1:
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir(self.phase)
#             os.chdir(self.schema)
#             sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\gather_db_stats '+self.schema, 'utf-8')
#             runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)
#             os.chdir(globs.PROGDIR)
#         elif self.op == 2:
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir(self.phase)
#             os.chdir(self.schema)
#             sqlcommand = bytes("@'%s\\sqls\\CountRows'"%globs.PROGDIR+ self.schema, 'utf-8')
#             runSQLQuery(sqlcommand, self.schema, sys.__stdout__)
#             os.chdir(globs.PROGDIR)
            
#         elif self.op == 3:
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir(self.phase)
#             os.chdir(self.schema)
#             sqlcommand = bytes("@'%s\\sqls\\InvalidObjects'"%globs.PROGDIR+ self.schema, 'utf-8')
#             runSQLQuery(sqlcommand, self.schema, sys.__stdout__)
#             os.chdir(globs.PROGDIR)
            
#         elif self.op == 4:
#             progPath = os.getcwd()
#             scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
#             os.chdir(scriptFolder)
#             session = Popen(['premigrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
#             session.communicate()
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir("Premigration")
#             BACKUPFILES = ['premigrate.log', 'gen_refschema.log', 'platform_db_creation.log', 'refsch_check.log', 'r_query.log']
#             for f in BACKUPFILES:
#                 copy(scriptFolder+f, self.schema)
#             os.chdir(progPath)
#         elif self.op == 5:
#             scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
#             os.chdir(scriptFolder)
#             session = Popen(['migrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
#             session.communicate()
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir("MGR")
#             BACKUPFILES = ['migrate_webworks.log', 'platform_db_creation.log', 'gen_refschema.log']
#             for f in BACKUPFILES:
#                 copy(scriptFolder+f, self.schema)
#             os.chdir(globs.PROGDIR)
#         elif self.op == 6:
#             scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
#             os.chdir(scriptFolder)
#             session = Popen(['premigrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
#             session.communicate()
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir("Premigration")
#             BACKUPFILES = ['premigrate.log', 'platform_db_creation.log', 'gen_refschema.log', 'refsch_check.log']
#             for f in BACKUPFILES:
#                 copy(scriptFolder+f, self.schema)
#             os.chdir(globs.PROGDIR)
#         elif self.op == 7:
#             scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
#             os.chdir(scriptFolder)
#             session = Popen(['migrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
#             session.communicate()
#             os.chdir(globs.ARCHIVEFOLDER)
#             os.chdir("MGR")
#             BACKUPFILES = ['migrate_monitor.log', 'platform_db_creation.log', 'gen_refschema.log', 'ema_populate_wwf.log', 'enroll_app_schema.log']
#             for f in BACKUPFILES:
#                 copy(scriptFolder+f, self.schema)
#             os.chdir(globs.PROGDIR)
#         elif self.op == 103:
#             createManugistics()
#         elif self.op == 104:
#             createABPPMGRSCHEMA()
#         elif self.op == 105:
#             createABPPMGRGRANTS()
#         elif self.op == 106:
#             createABPPMGRUPDATE()
#         elif self.op == 107:
#             sqlcommand = bytes('@sqls/customPremigration', 'utf-8')
#             runSQLQuery(sqlcommand, 'JDA_SYSTEM', sys.__stdout__)
#         elif self.op == 202:
#             self.status = 4
class UpdateSignal(QObject):
    """
    Signal to be used after task completion and calling updater function
    """
    updateTask = pyqtSignal(Task)

class prThread(threading.Thread):
    """
    Class for Thread #2 which is responsible to execute all tasks
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
    def run(self):    
        q = globs.TQueue
        sig = globs.UpdateSignal.updateTask
        while q:
            # Pop tasks from the queue until queue is empty
            task = q.popleft()
            sleep(0.5)
            print("Running Task",task.TaskType,task.schema)
            sleep(0.5)
            sig.emit(task)
            sleep(1)
            # Run Task
            task.runtask()
            # If Task finished without errors mark it as finished successfully
            if task.status == 1:
                task.status = 2
            sig.emit(task)

            # If Tasks completed with errors wait for incoming signal upon fixing
            if task.status == 4:
                globs.ERREVENT.clear()
                globs.ERREVENT.wait()
                task.status = 2
                sig.emit(task)
                # The following code can be used to rerun the task in case of failure
                # if task.status == 5:
                #     sig.emit(task)
                # else:
                #     task.status = 0
                #     q.appendleft(task)
        sleep(0.5)
        print("Migration Procedure Completed")
        sleep(0.5)

def init():
    """
    Initialization function for several globals
    """

    globs.PROGDIR = os.getcwd() #Save the program directory
    

    # Prepare to Read from Property File

    globs.SYSTEM_USER_KEYS = ('System_Username', 'System_Password')
    globs.SCHEMA_CREDS_KEYS = [('WebWORKS_Username', 'WebWORKS_Password'), ('ABPP_Username', 'ABPP_Password'), ('Monitor_Username', 'Monitor_Password'), ('JDA_SYSTEM_Username', 'JDA_SYSTEM_Password'), ('SCPO_Username', 'SCPO_Password')]
    globs.CRED_DICT = {
        'System_Username':'System_Password', 
        'WebWORKS_Username':'WebWORKS_Password',
        'ABPP_Username':'ABPP_Password',
        'Monitor_Username':'Monitor_Password',
        'JDA_SYSTEM_Username':'JDA_SYSTEM_Password',
        'SCPO_Username':'SCPO_Password'
    }

    # The following Queue(deque) will contain all Tasks 
    globs.TQueue = deque()

    # Create an instance of TaskUpdate Signal and connect it
    globs.UpdateSignal = UpdateSignal()
    globs.UpdateSignal.updateTask.connect(updater)

    # Error Signal
    globs.SignalObj = CSignal()
    globs.SignalObj.updateErrorSignal.connect(dispErr)

    globs.LogPipe = LogPipe()
    globs.ABPP_CREATED = False
    createLogFolders()
    
    errorEvent = threading.Event()
    globs.ERREVENT = errorEvent


def migrate():
    """
    Starts Migration Procedure
    """
    print("Creating and Starting Task Processor Thread") 
    controller = globs.CONTROLLER

    controller.btn.setDisabled(True)
    controller.vtable.hide()
    controller.taskMonitor.show()
    # Start Task Handler Thread
    th = prThread()
    th.start()

def disableTaskControls():
    """
    Error Fixing Done and Migration in Process
    """
    globs.CONTROLLER.resbtn.setDisabled(True)
    globs.CONTROLLER.fixbtn.setDisabled(True)

def resume():
    """
    Resumes migration after all errors have been fixed
    """
    if checkIfAllFixed():
        disableTaskControls()
        globs.ERREVENT.set()
        globs.DISP_SCREEN.updateScreen(globs.DISP_SCREEN.progress)
    else:
        globs.CONTROLLER.taskMonitor.errorBox.append("WARNING! Fix All Errors Before Resuming")
        globs.CONTROLLER.taskMonitor.errorBox.append("")
def fixerr():
    globs.DISP_SCREEN.currentWidget.hide()
    globs.DISP_SCREEN.errorView.show()
    globs.DISP_SCREEN.currentWidget = globs.DISP_SCREEN.errorView 
    # disableTaskControls()
    # globs.LAST_TASK.status = 5
    # globs.ERREVENT.set()

def queryComponents():
    """
    Get Current Version, Target Version and Available Schemas
    """
    dbpath = globs.props['TargetServer'] + ":" + globs.props['Port'] + "/" + globs.props['Service']
    con = cx_Oracle.connect(globs.props['WebWORKS_Username'], globs.props['WebWORKS_Password'], dbpath)
    cur = con.cursor()
    print("Querying Schema Names")
    cur.execute('select DISTINCT(SCHEMA_NAME) from csm_application')
    comps = []
    for result in cur:
        comps.append(result[0])
    cur.close()

    augComps = []
    augComps.append(globs.props['JDA_SYSTEM_Username'].upper())
    augComps.append(globs.props['WebWORKS_Username'].upper())
    augComps.append(globs.props['ABPP_Username'].upper())
    augComps.append(globs.props['Monitor_Username'].upper())

    # comps.remove(globs.props['WebWORKS_Username'].upper())
    # comps.remove(globs.props['Monitor_Username'].upper())
    # comps.remove(globs.props['SCPO_Username'].upper())

    # augComps += comps

    augComps.append(globs.props['SCPO_Username'].upper())

    # This Variable Contains List of Intended Users
    globs.COMPONENTS = augComps

    # Create appropriate log folders for each User
    for comp in augComps:
        for dirs in ["Premigration", "Migration", "Postmigration"]:
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(dirs)
            os.mkdir(comp)
            
    os.chdir(globs.PROGDIR)

    cur = con.cursor()
    print("Querying Current Version")
    cur.execute("select VALUE from csm_schema_log where name='DATABASE_VERSION'")
    result = cur.fetchone()
    globs.COMPVER = result[0]
    cur.close()
    con.close()   

    print("Performing Target Version Check")
    targetv_path = globs.props['JDA_HOME'] + '\\' + 'install\\platform.version'
    f = open(targetv_path)
    line = f.readline()
    line = f.readline()
    targetVersion = line.split(':')[1].strip()
    print("Found Target Version:", targetVersion)
    globs.TARGET_VERSION = targetVersion
    f.close()

def readProperties():
    """
    Reads the property file and stores key-value pairs in a dictionary
    """
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
    globs.props = props

    globs.UserPassDict = {}
    for user_cat in globs.CRED_DICT:
        globs.UserPassDict[props[user_cat]] = props[globs.CRED_DICT[user_cat]] 




class ControllerScreen(QWidget):
    """
    This Screen Contains the Version Table as well as any buttons.
    This Screen will be displayed inside Action Screen on top-left corner after successful connection.
    """
    def __init__(self, parent = None):     
        QWidget.__init__(self, parent)
        self.arch = QVBoxLayout(self)
        self.design()
    
    def design(self):
        vtable = ComponentTable(self)
        self.vtable = vtable
        vtable.setRowCount(len(globs.COMPONENTS))
        vtable.setColumnCount(3)
        vtable.setHorizontalHeaderLabels("Component;Current Version;Target Version;".split(";"))

        curRow = 0
        for i in globs.COMPONENTS:
            vtable.setItem(curRow,0, QTableWidgetItem(i))
            vtable.setItem(curRow,1, QTableWidgetItem(globs.COMPVER))
            vtable.setItem(curRow,2, QTableWidgetItem(globs.TARGET_VERSION))
            curRow += 1

        self.buttonBar = QWidget(self)
        self.buttonBarLayout = HBOXNOMG(self.buttonBar)
        self.btn = QPushButton("Start Migration Procedure", self.buttonBar)
        self.buttonBarLayout.addWidget(self.btn)
        self.btn.clicked.connect(migrate)

        self.resbtn = QPushButton("Resume Migration Safely", self.buttonBar)
        self.buttonBarLayout.addWidget(self.resbtn)
        self.fixbtn = QPushButton("Fix Errors", self.buttonBar)
        self.buttonBarLayout.addWidget(self.fixbtn)
        self.resbtn.setDisabled(True)
        self.fixbtn.setDisabled(True)
        self.resbtn.clicked.connect(resume)
        self.fixbtn.clicked.connect(fixerr)

        self.semiController = QWidget(self)
        self.semiCLayout = VBOXNOEXMG(self.semiController)
        self.semiCLayout.addWidget(vtable)

        self.taskMonitor = TaskMonitor(self) 
        self.semiCLayout.addWidget(self.taskMonitor)


        self.semiController.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pbar = FULLProgressBar(self)
        self.pbar.setMaxTasks(Task.lblcntr)
        self.arch.addWidget(self.pbar)
        self.arch.addWidget(self.semiController)
        self.arch.addWidget(self.buttonBar)
        
class Window(QMainWindow):
    """
    Main Windows Screen Class which creates everything else
    """
    def __init__(self):     
        QMainWindow.__init__(self)
        init()
        self.setGeometry(50, 50, 1280, 720)
        self.showMaximized()
        self.setWindowTitle("Upgrade Manager")
        self.setWindowIcon(QIcon('icon.png'))
        self.design()
        sys.stdout = EmittingStream()
        sys.stdout.textWritten.connect(self.normalOutputWritten)
        self.load()
        self.show()
        
        globs.MAIN_WINDOW = self
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
	
    def design(self):
        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        viewMenu = mainMenu.addMenu('&View')
        optionsMenu = mainMenu.addMenu('&Options')
        PremigrationMenu = mainMenu.addMenu('&Pre-Migration')
        PostmigrationMenu = mainMenu.addMenu('&Post-Migration')
        helpMenu = mainMenu.addMenu('&Help')
        loadPropAction= QAction("&Load Property File", self)
        loadPropAction.setShortcut("Ctrl+L")
        loadPropAction.setStatusTip('Load upgrade.properties')
        loadPropAction.triggered.connect(self.readProperties)
        exitAction= QAction("&Exit", self)
        exitAction.setStatusTip('Exit the Program')
        exitAction.triggered.connect(self.close)

        selAllErrAction= QAction("&Select All Errors", self)
        selAllErrAction.setStatusTip('Select All Errors')
        selAllErrAction.triggered.connect(selallerrors)

        fileMenu.addAction(loadPropAction)
        fileMenu.addAction(exitAction)
        rowCounts = PremigrationMenu.addMenu('&Row Counts')
        invalidobjCounts = PremigrationMenu.addMenu('&Invalid Object Counts')
        rowCountsPost = PostmigrationMenu.addMenu('&Row Counts')
        invalidobjCountsPost = PostmigrationMenu.addMenu('&Invalid Object Counts')
        globs.RowCMenuPremigration = rowCounts
        globs.RowCMenuPostmigration = rowCountsPost
        globs.InvalidCMenuPremigration = invalidobjCounts
        globs.InvalidCMenuPostmigration = invalidobjCountsPost
        viewProgressAction= QAction("&Progress", self)
        viewProgressAction.triggered.connect(self.viewProgress)
        viewMenu.addAction(viewProgressAction)

        optionsMenu.addAction(selAllErrAction)
        
        contentScreen = QWidget(self)
        self.setCentralWidget(contentScreen)

        self.primaryLayout = QHBoxLayout(contentScreen)
        
        self.leftSide = QWidget()
        self.leftLayout = QVBoxLayout(self.leftSide)
        #self.leftSide.setLayout(self.leftLayout)

        self.actionScreen = ActionScreen()
        
        self.connectionScreen = ConnectionScreen()
        self.actionScreen.layout.addWidget(self.connectionScreen)
        self.connectionScreen.conbtn.clicked.connect(self.connect)
        
        self.leftLayout.addWidget(self.actionScreen)
        self.leftLayout.addWidget(QHLine())
        self.ConTextField = ConsoleTE()        
        self.leftLayout.addWidget(self.ConTextField)


        self.rightSide = DisplayScreen()
        globs.DISP_SCREEN = self.rightSide
        self.primaryLayout.addWidget(self.leftSide)
        self.primaryLayout.addWidget(QVLine())
        self.primaryLayout.addWidget(self.rightSide)

        # font_db = QFontDatabase()
        # font_id = font_db.addApplicationFont("fonts/UbuntuMono-R.ttf")
        # families = font_db.applicationFontFamilies(font_id)[0]
        # font = QFont(families, 10)
        # self.setFont(font)
    
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
        prepareTasks()
        globs.CONTROLLER = ControllerScreen(self.actionScreen)
        self.actionScreen.layout.addWidget(globs.CONTROLLER)
        self.connectionScreen.hide()
        self.rightSide.currentWidget.hide()
        self.rightSide.progress.show()
        self.rightSide.currentWidget = self.rightSide.progress

    def load(self):
        self.readProperties()

    @pyqtSlot(str)
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        self.ConTextField.moveCursor(QTextCursor.End)
        self.ConTextField.insertPlainText( text )
        QApplication.processEvents()

    def readProperties(self):
        readProperties()
        self.connectionScreen.dbserver.setText(globs.props['TargetServer'])
        self.connectionScreen.port.setText(globs.props['Port'])
        self.connectionScreen.sid.setText(globs.props['SID'])
        self.connectionScreen.service.setText(globs.props['Service'])

    def viewProgress(self):
        self.rightSide.currentWidget.hide()
        self.rightSide.progress.show()
        self.rightSide.currentWidget = self.rightSide.progress