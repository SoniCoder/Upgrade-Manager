from accessory import *
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
    def __init__(self, op, schema = None, labels = False, TaskType = "Accessory Task", Action = "None", phase = "Other"):
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
            log_file = "\\".join([globs.ARCHIVEFOLDER, self.phase, self.schema, "gather_db_stats.log"])
            errFound = find_errors(log_file, ["ORA-", "PLS-"])
            if errFound:
                self.status = 4
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
            os.chdir("Premigration")
            BACKUPFILES = ['premigrate.log', 'gen_refschema.log', 'platform_db_creation.log', 'refsch_check.log', 'r_query.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
            os.chdir(globs.PROGDIR)
        elif self.op == 5:
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Migration")
            BACKUPFILES = ['migrate_webworks.log', 'platform_db_creation.log', 'gen_refschema.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
            os.chdir(globs.PROGDIR)

        elif self.op == 6:
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['premigrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Premigration")
            BACKUPFILES = ['premigrate.log', 'platform_db_creation.log', 'gen_refschema.log', 'refsch_check.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4    
            os.chdir(globs.PROGDIR)
        elif self.op == 7:
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Migration")
            BACKUPFILES = ['migrate_monitor.log', 'platform_db_creation.log', 'gen_refschema.log', 'ema_populate_wwf.log', 'enroll_app_schema.log']
            for f in BACKUPFILES:
                copy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
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
            phase = "Premigration"
            predct = getattr(globs,'RowCountDict'+phase)
            phase = "Postmigration"
            postdct = getattr(globs,'RowCountDict'+phase)
            res = (predct == postdct)
            if not res:
                globs.SignalObj.updateErrorSignal.emit("Row Count Matching Failed!")
                self.status = 4
        elif self.op == 11:
            phase = "Premigration"
            predct = getattr(globs,'InvalidCountDict'+phase)
            phase = "Postmigration"
            postdct = getattr(globs,'InvalidCountDict'+phase)
            res = (predct == postdct)
            if not res:
                globs.SignalObj.updateErrorSignal.emit("Invalid Object Count Matching Failed!")
                self.status = 4
        elif self.op == 103:
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            user = globs.props['JDA_SYSTEM_Username']
            print("Creating the ManugisticsPkg table in the JDA System schema")
            sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\platform\\ManugisticsPkg '+user, 'utf-8')
            stdout, stdin = runSQLQuery(sqlcommand, user, globs.LogPipe)
            log_file = "\\".join([globs.ARCHIVEFOLDER, self.phase, "ManugisticsPkg.log"])
            errFound = find_errors(log_file, ["ORA-", "PLS-"])
            if errFound:
                self.status = 4
            os.chdir(globs.PROGDIR)
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
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            sqlcommand = bytes("@'%s\\sqls\\custompremgr'"%globs.PROGDIR, 'utf-8')
            runSQLQuery(sqlcommand, 'JDA_SYSTEM', sys.__stdout__)
            os.chdir(globs.PROGDIR)
        elif self.op == 202:
            log_file = globs.PROGDIR+'\\tmp\\sample.log'
            errFound = find_errors(log_file, ["ORA-", "PLS-"])
            if errFound:
                self.status = 4

def prepareTasks():
    q = globs.TQueue

    ### -FUTURE- : Method for reading tasks from a file
    # parseTaskList(globs.TQueue)
    
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(1,comp, True, 'Stat Gathering', "Gathering Stats on %s"%comp, "Premigration"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(2,comp, True, "Count Rows", "Counting Rows for %s"%comp, "Premigration"))
    q.append(Task(100, phase ="Premigration"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(3,comp, True, "Invalid Object Counting", "Counting Invalid Objects for %s"%comp, "Premigration"))
    q.append(Task(101, phase = "Premigration"))

    
    q.append(Task(107, 'None', True, "Custom Script", "Running Custom Pre-Migration Script", "Premigration"))
    q.append(Task(103, 'JDA_SYSTEM', True, "Manugistics Installation", "Manugistics Installation in JDA_SYSTEM", "Premigration"))
    if globs.ABPP_CREATED:
        q.append(Task(104, 'ABPPMGR', True, "Schema Creation", "Creating ABPPMGR Schema", "Premigration"))
    else:
        q.append(Task(105, 'ABPPMGR', True, "Grant Providing", "Providing Grants to ABPPMGR Schema", "Premigration"))
        q.append(Task(106, 'ABPPMGR', True, "Schema Update", "ABPPMGR Schema Update", "Premigration"))
        
    comp = globs.props['WebWORKS_Username']
    q.append(Task(4,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "Premigration"))
    q.append(Task(5,comp, True, 'Migration', "Migrating %s"%comp, "Migration"))
    comp = globs.props['Monitor_Username']
    q.append(Task(6,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "Premigration"))
    q.append(Task(7,comp, True, 'Migration', "Migrating %s"%comp, "Migration"))

    comp = globs.props['SCPO_Username']
    q.append(Task(8,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "Premigration"))
    q.append(Task(9,comp, True, 'Migration', "Migrating %s"%comp, "Migration"))

    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(1,comp, True, 'Stat Gathering', "Gathering Stats on %s"%comp, "Postmigration"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(2,comp, True, "Count Rows", "Counting Rows for %s"%comp, "Postmigration"))
    q.append(Task(100, phase = "Postmigration"))
    for comp_i in range(len(globs.COMPONENTS)):
        comp = globs.COMPONENTS[comp_i]
        q.append(Task(3,comp, True, "Invalid Object Counting", "Counting Invalid Objects for %s"%comp, "Postmigration"))
    q.append(Task(101, phase = "Postmigration"))

    q.append(Task(10,"ALLSCHEMAS", True, 'Validation', "Row Count Matching", "Postmigration"))
    q.append(Task(11,"ALLSCHEMAS", True, 'Validation', "Invalid Object Count Matching", "Postmigration"))


    # for i in range(5):
    #     q.append(Task(200+i,"Dummy Task", True, 'Migration: '+ str(i), "Dummy Task"))   

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
    globs.LAST_TASK = task

                ### Unrequired Code (Mainly for Automatically Showing the Tables)

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




### Future Work
### Way of reading tasks from plain text files

# def createTask(q, taskfile, phase, SCHEMA):
#     tfile = open(taskfile)
#     fline = tfile.readline()
    



#     # while True:
#     #     pass

# def parseTaskList(q):
#     d = globs.saveDir()
#     os.chdir("Tasks")
#     tasklist = open("Tasklist.txt")
#     while True:
#         taskline = tasklist.readline()
#         if taskline == '': break
#         tlinesp = taskline.split()
#         taskfile = tlinesp[0]
#         phase = tlinesp[1]
#         SCHEMA = tlinesp[2]
#         if SCHEMA == "ALLSCHEMAS":
#             for comp_i in range(len(globs.COMPONENTS)):
#                 SCHEMA = globs.COMPONENTS[comp_i]
#                 createTask(q, taskfile, phase, SCHEMA)
#         else:
#             createTask(q, taskfile, phase, SCHEMA)

#     d.restore()

