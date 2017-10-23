import cx_Oracle
import datetime
import os
import threading
import sys

import globs

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
from task import Task, parseTaskList
from config import *
from commands import *


def connect():
    dbpath = globs.props['TargetServer'] + ":" + globs.props['Port'] + "/" + globs.props['Service']
    
    print("Checking Connection with SYSTEM USER")
    username, password = globs.SYSTEM_USER_KEYS
    try:
        con = cx_Oracle.connect(globs.props[username], globs.props[password], dbpath)
        print("Connection Successful")
        con.close()
    except Exception as e:
        print("Connection Failed", e)
        return (False, e, "Connection Attempt Failed! Username:%s"%(globs.props[username]))
    con = cx_Oracle.connect(globs.props[username], globs.props[password], dbpath)    
    print("Checking JDA_SYSTEM existence")
    cur = con.cursor()
    cur.execute("select * from ALL_USERS where username = 'JDA_SYSTEM'")
    cur.fetchall()
    if(cur.rowcount==1):
        print("User Exists")
    else:
        print("Creating USER JDA_SYSTEM")
        createJDASYSTEM()
    cur.close()

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
    sqlcommand = bytes('@sqls/ABPP_GRANTS', 'utf-8')
    runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)

def createABPPMGRUPDATE():
    progPath = os.getcwd()
    scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
    os.chdir(scriptFolder)
    session = Popen(['updateAbppSchema.cmd', '-coreServices'], stdout=globs.LogPipe, stdin = PIPE)
    session.communicate()
    os.chdir(progPath)

def createABPPMGRUSER():
    password = globs.props['ABPP_Password']  
    sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\setup\\cr_abpp_user '+password, 'utf-8')
    stdout, stdin = runSQLQuery(sqlcommand, globs.props['System_Username'])
    print(stdout.decode('ascii'))

def createABPPMGRSCHEMA():
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
    os.mkdir("PREMGR")
    os.mkdir("MGR")
    os.mkdir("POSTMGR")
    print("Storing All Logs in ARCHIVES/%s"%logFolder)
    globs.ARCHIVEFOLDER = os.getcwd()
    os.chdir(globs.PROGDIR)

class EmittingStream(QObject):
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


def readInvalidObjects(phase):
    dct = getattr(globs,'InvalidCountDict'+phase)
    os.chdir(globs.ARCHIVEFOLDER)
    os.chdir(phase)
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        os.chdir(comp)     
        dct[comp] = []
        lst = dct[comp]
        fileName = "invalidObj(%s).txt"%comp
        print("Opening File:",fileName)
        f = open(fileName)
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        while True:
            line = f.readline()
            ls = line.split()
            if len(ls)!=4: break
            lst.append(ls)
        os.chdir("..")
    os.chdir(globs.PROGDIR)

def readRows(phase):
    dct = getattr(globs,'RowCountDict'+phase)
    os.chdir(globs.ARCHIVEFOLDER)
    os.chdir(phase)
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        os.chdir(comp)
        dct[comp] = []
        lst = dct[comp]
        fileName = "count(%s)list.txt"%comp
        print("Opening File:",fileName)
        f = open(fileName)
        f.readline()
        f.readline()
        f.readline()
        while True:
            line = f.readline()
            pair = line.split()
            if len(pair)!=2: break
            lst.append(pair)
        os.chdir("..")
    os.chdir(globs.PROGDIR)
def updateTable(phase, type, schema):
    print("Updating Table for schema %s"%schema)
    if type == "ROW":
        dct = getattr(globs,'RowCountDict'+phase)
        lst = dct[schema]
        globs.DISP_SCREEN.tview.setData(lst, "Table Name in schema %s; Row Count"%schema)
        globs.DISP_SCREEN.currentWidget.hide()
        globs.DISP_SCREEN.tview.show()
        globs.DISP_SCREEN.currentWidget = globs.DISP_SCREEN.tview
    elif type == "INVALIDOBJ":
        dct = getattr(globs,'InvalidCountDict'+phase)
        lst = dct[schema]
        globs.DISP_SCREEN.tview.setData(lst, "Owner; Constraint_Name; Table_Name; Status")
        globs.DISP_SCREEN.currentWidget.hide()
        globs.DISP_SCREEN.tview.show()
        globs.DISP_SCREEN.currentWidget = globs.DISP_SCREEN.tview
def updater(task):
    if task.labels:
        imgLbl = globs.DISP_SCREEN.progress.rightList[task.localid]
        if task.status == 0:       
            pixmap = QPixmap('images/amber.png')
        elif task.status == 2 or task.status == 5:
            pixmap = QPixmap('images/green.png')
            globs.CONTROLLER.pbar.updateCompleted(task.localid + 1)
        elif task.status == 4:
            pixmap = QPixmap('images/red.png')
        imgLbl.setPixmap(pixmap)

    if task.status == 4:
        globs.CONTROLLER.resbtn.setDisabled(False)
        globs.CONTROLLER.fixbtn.setDisabled(False)
        globs.CONTROLLER.taskMonitor.errorBox.append("Errors Encountered While Performing Task #%d"%(task.localid+1))
        globs.CONTROLLER.taskMonitor.errorBox.append("")

    if task.op == 100:
        if task.status == 2:
            readRows(task.phase)
            rowcmenu = getattr(globs,'RowCMenu'+task.phase)
            print("Creating and Adding New View Row Actions for Phase %s"%task.phase)
            actions = [QAction(comp, globs.MAIN_WINDOW) for comp in globs.COMPONENTS]            
            for act_i in range(len(actions)):
                rowcmenu.addAction(actions[act_i])
                actions[act_i].triggered.connect(lambda f, i = act_i: updateTable(task.phase, "ROW", globs.COMPONENTS[i]))
    elif task.op == 101:
        if task.status == 2:
            readInvalidObjects(task.phase)
            menu = getattr(globs,"InvalidCMenu"+task.phase)
            print("Creating and Adding New View Invalid Object Count Actions for Phase %s"%task.phase)
            actions = [QAction(comp, globs.MAIN_WINDOW) for comp in globs.COMPONENTS]            
            for act_i in range(len(actions)):
                menu.addAction(actions[act_i])
                actions[act_i].triggered.connect(lambda f, i = act_i: updateTable(task.phase, "INVALIDOBJ", globs.COMPONENTS[i]))
            # globs.DISP_SCREEN.currentWidget.hide()
            # globs.DISP_SCREEN.tview.show()
            # globs.DISP_SCREEN.currentWidget = globs.DISP_SCREEN.tview
            # dct = globs.InvalidCountDict
            # lst = dct[globs.COMPONENTS[4]]
            # globs.DISP_SCREEN.tview.setData(lst, "Owner; Constraint_Name; Table_Name; Status")
            # rowcmenu = globs.RowCMenu
            # print("Creating and Adding New View Row Actions")
            # actions = [QAction(comp, globs.MAIN_WINDOW) for comp in globs.COMPONENTS]            
            # funcs = []
            # for act_i in range(len(actions)):
            #     rowcmenu.addAction(actions[act_i])
            #     actions[act_i].triggered.connect(lambda f, i = act_i: updateTable(globs.COMPONENTS[i]))
    globs.LAST_TASK = task
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
#             os.chdir("PREMGR")
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
#             os.chdir("PREMGR")
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
#             sqlcommand = bytes('@sqls/custompremgr', 'utf-8')
#             runSQLQuery(sqlcommand, 'JDA_SYSTEM', sys.__stdout__)
#         elif self.op == 202:
#             self.status = 4
class UpdateSignal(QObject):
    updateTask = pyqtSignal(Task)

class prThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
    def run(self):    
        q = globs.TQueue
        sig = globs.UpdateSignal.updateTask
        while q:
            task = q.popleft()
            sleep(0.5)
            print("Running Task",task.TaskType,task.schema)
            sleep(0.5)
            sig.emit(task)
            sleep(1)
            task.runtask()
            if task.status == 1:
                task.status = 2
            sig.emit(task)

            if task.status == 4:
                globs.ERREVENT.clear()
                globs.ERREVENT.wait()
                task.status = 2
                sig.emit(task)
                # if task.status == 5:
                #     sig.emit(task)
                # else:
                #     task.status = 0
                #     q.appendleft(task)
        sleep(0.5)
        print("Migration Procedure Completed")
        sleep(0.5)

def init():
    globs.PROGDIR = os.getcwd()
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
    globs.TQueue = deque()

    globs.UpdateSignal = UpdateSignal()
    globs.UpdateSignal.updateTask.connect(updater)

    globs.SignalObj = CSignal()
    globs.SignalObj.updateErrorSignal.connect(dispErr)

    globs.LogPipe = LogPipe()
    globs.ABPP_CREATED = False
    createLogFolders()
    
    errorEvent = threading.Event()
    globs.ERREVENT = errorEvent


def prepareTasks():
    q = globs.TQueue
    parseTaskList(globs.TQueue)
    # for comp_i in range(len(globs.COMPONENTS)):
    #     comp = globs.COMPONENTS[comp_i]
    #     q.append(Task(1,comp, True, 'Stat Gathering', "Gathering Stats on %s"%comp, "PREMGR"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(2,comp, True, "Row Counting", "Counting Rows for %s"%comp, "PREMGR"))
    q.append(Task(100, phase ="PREMGR"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(3,comp, True, "Invalid Object Counting", "Counting Invalid Objects for %s"%comp, "PREMGR"))
    q.append(Task(101, phase = "PREMGR"))

    
    # q.append(Task(107, 'None', True, "Custom Script", "Running Custom Pre-Migration Script", "PREMGR"))
    # q.append(Task(103, 'JDA_SYSTEM', True, "Manugistics Installation", "Manugistics Installation in JDA_SYSTEM", "PREMGR"))
    # if globs.ABPP_CREATED:
    #     q.append(Task(104, 'ABPPMGR', True, "Schema Creation", "Creating ABPPMGR Schema", "PREMGR"))
    # else:
    #     q.append(Task(105, 'ABPPMGR', True, "Grant Providing", "Providing Grants to ABPPMGR Schema", "PREMGR"))
    #     q.append(Task(106, 'ABPPMGR', True, "Schema Update", "ABPPMGR Schema Update", "PREMGR"))
        
    # comp = globs.props['WebWORKS_Username']
    # q.append(Task(4,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "PREMGR"))
    # q.append(Task(5,comp, True, 'Migration', "Migrating %s"%comp, "MGR"))
    # comp = globs.props['Monitor_Username']
    # q.append(Task(6,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "PREMGR"))
    # q.append(Task(7,comp, True, 'Migration', "Migrating %s"%comp, "MGR"))

    # comp = globs.props['SCPO_Username']
    # q.append(Task(8,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "PREMGR"))
    # q.append(Task(9,comp, True, 'Migration', "Migrating %s"%comp, "MGR"))

    # for comp_i in range(len(globs.COMPONENTS)):
    #     comp = globs.COMPONENTS[comp_i]
    #     q.append(Task(1,comp, True, 'Stat Gathering', "Gathering Stats on %s"%comp, "POSTMGR"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(2,comp, True, "Row Counting", "Counting Rows for %s"%comp, "POSTMGR"))
    q.append(Task(100, phase = "POSTMGR"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(3,comp, True, "Invalid Object Counting", "Counting Invalid Objects for %s"%comp, "POSTMGR"))
    q.append(Task(101, phase = "POSTMGR"))

    q.append(Task(10,"ALLSCHEMAS", True, 'Validation', "Row Count Matching", "POSTMGR"))
    q.append(Task(11,"ALLSCHEMAS", True, 'Validation', "Invalid Object Count Matching", "POSTMGR"))


    # for i in range(5):
    #     q.append(Task(200+i,":P", True, 'Migration: '+ str(i), "HAHAHA"))    


def migrate():
    print("Creating and Starting Task Processor Thread") 
    controller = globs.CONTROLLER
    controller.btn.setDisabled(True)
    controller.vtable.hide()
    controller.taskMonitor.show()
    th = prThread()
    th.start()

def disableTaskControls():
    globs.CONTROLLER.resbtn.setDisabled(True)
    globs.CONTROLLER.fixbtn.setDisabled(True)

def resume():
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

    comps.remove(globs.props['WebWORKS_Username'].upper())
    comps.remove(globs.props['Monitor_Username'].upper())
    comps.remove(globs.props['SCPO_Username'].upper())

    augComps += comps

    augComps.append(globs.props['SCPO_Username'].upper())


    globs.COMPONENTS = augComps

    for comp in augComps:
        for dirs in ["PREMGR", "MGR", "POSTMGR"]:
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
        premgrMenu = mainMenu.addMenu('&Pre-Migration')
        postmgrMenu = mainMenu.addMenu('&Post-Migration')
        helpMenu = mainMenu.addMenu('&Help')
        loadPropAction= QAction("&Load Property File", self)
        loadPropAction.setShortcut("Ctrl+L")
        loadPropAction.setStatusTip('Load upgrade.properties')
        loadPropAction.triggered.connect(self.readProperties)
        exitAction= QAction("&Exit", self)
        exitAction.setStatusTip('Exit the Program')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(loadPropAction)
        fileMenu.addAction(exitAction)
        rowCounts = premgrMenu.addMenu('&Row Counts')
        invalidobjCounts = premgrMenu.addMenu('&Invalid Object Counts')
        rowCountsPost = postmgrMenu.addMenu('&Row Counts')
        invalidobjCountsPost = postmgrMenu.addMenu('&Invalid Object Counts')
        globs.RowCMenuPREMGR = rowCounts
        globs.RowCMenuPOSTMGR = rowCountsPost
        globs.InvalidCMenuPREMGR = invalidobjCounts
        globs.InvalidCMenuPOSTMGR = invalidobjCountsPost
        viewProgressAction= QAction("&Progress", self)
        viewProgressAction.triggered.connect(self.viewProgress)
        viewMenu.addAction(viewProgressAction)
        
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