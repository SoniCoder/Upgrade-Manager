from augmentedWidgets import *
from commands import *
from collections import deque
from errorhandling import *
from shutil import copyfile, copy
import globs
import os
import sys


class Task():
    lblcntr = 0
    def __init__(self, op, schema = None, labels = False, TaskType = "Accessory Task", Action = "None", phase = "None"):
        self.func = None
        self.schema = schema
        self.op = op
        self.status = 0
        self.localid = 0
        self.labels = labels
        self.phase = phase
        self.TaskType = TaskType
        self.Action = Action
        self.outputStatus = ""
        if self.labels:
            self.localid = Task.lblcntr
            dispLbl = QCenteredLabel(str(self.localid + 1))
            dispLbl.setFixedHeight(30)
            globs.DISP_SCREEN.progress.snoLayout.addWidget(dispLbl)
            globs.DISP_SCREEN.progress.snoLayout.addWidget(QHLine())

            dispLbl = QCenteredLabel(self.phase)
            dispLbl.setFixedHeight(30)
            globs.DISP_SCREEN.progress.phaseLayout.addWidget(dispLbl)
            globs.DISP_SCREEN.progress.phaseLayout.addWidget(QHLine())


            dispLbl = QCenteredLabel(TaskType)
            dispLbl.setFixedHeight(30)
            globs.DISP_SCREEN.progress.leftList.append(dispLbl)
            globs.DISP_SCREEN.progress.leftLayout.addWidget(dispLbl)
            globs.DISP_SCREEN.progress.leftLayout.addWidget(QHLine())

            dispLbl = QCenteredLabel(Action)
            dispLbl.setFixedHeight(30)            
            globs.DISP_SCREEN.progress.middleList.append(dispLbl)
            globs.DISP_SCREEN.progress.middleLayout.addWidget(dispLbl)
            globs.DISP_SCREEN.progress.middleLayout.addWidget(QHLine())
            
            imgLbl = QCenteredLabel()
            pixmap = QPixmap('images/white.png')
            imgLbl.setPixmap(pixmap)
            globs.DISP_SCREEN.progress.rightList.append(imgLbl)
            globs.DISP_SCREEN.progress.rightLayout.addWidget(imgLbl)
            globs.DISP_SCREEN.progress.rightLayout.addWidget(QHLine())
            Task.lblcntr += 1
    def runtask(self):        
        self.status = 1
        if self.op == 1:
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            os.chdir(self.schema)
            sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\gather_db_stats '+self.schema, 'utf-8')
            runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)
            os.chdir(globs.PROGDIR)
        elif self.op == 2:
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            os.chdir(self.schema)
            sqlcommand = bytes("@'%s\\sqls\\CountRows'"%globs.PROGDIR+ self.schema, 'utf-8')
            runSQLQuery(sqlcommand, self.schema, sys.__stdout__)
            os.chdir(globs.PROGDIR)
            
        elif self.op == 3:
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            os.chdir(self.schema)
            sqlcommand = bytes("@'%s\\sqls\\InvalidObjects'"%globs.PROGDIR+ self.schema, 'utf-8')
            runSQLQuery(sqlcommand, self.schema, sys.__stdout__)
            os.chdir(globs.PROGDIR)
            
        elif self.op == 4:
            progPath = os.getcwd()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['premigrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("PREMGR")
            BACKUPFILES = ['premigrate.log', 'gen_refschema.log', 'platform_db_creation.log', 'refsch_check.log', 'r_query.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            os.chdir(progPath)
        elif self.op == 5:
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("MGR")
            BACKUPFILES = ['migrate_webworks.log', 'platform_db_creation.log', 'gen_refschema.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            os.chdir(globs.PROGDIR)
        elif self.op == 6:
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['premigrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("PREMGR")
            BACKUPFILES = ['premigrate.log', 'platform_db_creation.log', 'gen_refschema.log', 'refsch_check.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            os.chdir(globs.PROGDIR)
        elif self.op == 7:
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("MGR")
            BACKUPFILES = ['migrate_monitor.log', 'platform_db_creation.log', 'gen_refschema.log', 'ema_populate_wwf.log', 'enroll_app_schema.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            os.chdir(globs.PROGDIR)
        elif self.op == 8:
            d = globs.saveDir()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['premigrate_scpo.cmd', globs.props['SCPO_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=sys.__stdout__)
            session.communicate()
            d.restore()
        elif self.op == 9:
            d = globs.saveDir()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_scpo.cmd', globs.props['SCPO_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            d.restore()
        elif self.op == 10:
            phase = "PREMGR"
            predct = getattr(globs,'RowCountDict'+phase)
            phase = "POSTMGR"
            postdct = getattr(globs,'RowCountDict'+phase)
            res = (predct == postdct)
            if not res:
                globs.SignalObj.updateErrorSignal.emit("Row Count Matching Failed!")
                self.status = 4
        elif self.op == 11:
            phase = "PREMGR"
            predct = getattr(globs,'InvalidCountDict'+phase)
            phase = "POSTMGR"
            postdct = getattr(globs,'InvalidCountDict'+phase)
            res = (predct == postdct)
            if not res:
                globs.SignalObj.updateErrorSignal.emit("Invalid Object Count Matching Failed!")
                self.status = 4
        elif self.op == 103:
            user = globs.props['JDA_SYSTEM_Username']
            print("Creating the ManugisticsPkg table in the JDA System schema")
            sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\platform\\ManugisticsPkg '+user, 'utf-8')
            stdout, stdin = runSQLQuery(sqlcommand, user, globs.LogPipe)
        elif self.op == 104:
            progPath = os.getcwd()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
            os.chdir(scriptFolder)
            session = Popen(['createAbppSchema.cmd'], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(progPath)
        elif self.op == 105:
            sqlcommand = bytes('@sqls/ABPP_GRANTS', 'utf-8')
            runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)
        elif self.op == 106:
            progPath = os.getcwd()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
            os.chdir(scriptFolder)
            session = Popen(['updateAbppSchema.cmd', '-coreServices'], stdout=globs.LogPipe, stdin = PIPE)
            session.communicate()
            os.chdir(progPath)
        elif self.op == 107:
            sqlcommand = bytes('@sqls/custompremgr', 'utf-8')
            runSQLQuery(sqlcommand, 'JDA_SYSTEM', sys.__stdout__)
        elif self.op == 202:
            log_file = globs.PROGDIR+'\\tmp\\sample.log'
            errFound = find_errors(log_file, ["ORA-"])
            if errFound:
                self.status = 4

def createTask(q, taskfile, phase, SCHEMA):
    tfile = open(taskfile)
    fline = tfile.readline()
    



    # while True:
    #     pass

def parseTaskList(q):
    d = globs.saveDir()
    os.chdir("Tasks")
    tasklist = open("Tasklist.txt")
    while True:
        taskline = tasklist.readline()
        if taskline == '': break
        tlinesp = taskline.split()
        taskfile = tlinesp[0]
        phase = tlinesp[1]
        SCHEMA = tlinesp[2]
        if SCHEMA == "ALLSCHEMAS":
            for comp_i in range(len(globs.COMPONENTS)):
                SCHEMA = globs.COMPONENTS[comp_i]
                createTask(q, taskfile, phase, SCHEMA)
        else:
            createTask(q, taskfile, phase, SCHEMA)

    d.restore()