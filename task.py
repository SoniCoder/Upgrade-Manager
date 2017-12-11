"""
Author: Hritik Soni

Description:

This module describes the task system.

It contains 3 types of categories mainly.

1. Task(Class): This Class is required to create Task objects which have some functionality.
This task also contains the run method which described what exactly is to be done when the task is executed.

2. PrepareTasks(Function): This functions creates tasks one by one and puts them into a queue.
The way to create a task is to call the constructor of the Task class with certain describing params.
This is followed by appending the created Task object to the queue.

3. Updater(Function): This function runs in the main thread and contains statements which are to be executed
after a certain task is completed.
"""



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
    """
    This Class is responsible for creating task objects.
    
    Refer to docs on further details about the task system.
    """
    lblcntr = 0 #This counter is used to keep track of the row for a particular task in the UI.
    def __init__(self, op, schema = None, labels = False, TaskType = "Accessory Task", Action = "None", phase = "Other"):
        """
        Constructor of Task class

        Description of Params:

        1. op : This is operation code. This has to be unique for each Task object if it performs a unique functionality.
        If a task is to be reperformed, this code can be reused to create a new task object with similar functionality.

        2. schema: This describes which schema a particular task acts on. This also helps to place logs at appropriate folder.

        3. labels: This is a boolean variable which tells the program whether the task needs to be shown in UI.

        4. TaskType: A very brief idea of the Task.

        5. Action: A more exact idea of the Task.

        6. phase: Can be one of the three - Premigration, Migration and Postmigration.

        Other Instance/Class Variables:

        7. Status: Status of a Task

        It can be one of these.

        (i)     0 : Newly Created Task
        (ii)    1 : A Running Task
        (iii)   2 : Successfully Completed Task
        (iv)    4 : Task completed with Errors

        """
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
            # The following code is responsible for displaying Tasks in the UI
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
        """
        This function tells python exactly what to do when the task is in progress.

        """        
        self.status = 1 #Declare Task as Running.
        
        #Get Ready to Capture Encountered Errors for Mailing
        globs.curErrBlock = ErrorBlock("Error Analysis for Task: "+self.Action)        

        """
        You can practically do anything while a task is running.

        Here are some helper functions:
        (Go to these functions for more info)
        1. runSQLQuery                   : Executes any sql script.
        2. find_errors/findErrorsInFiles : Checks a file list for errors and report them.
        3. Popen                         : Inbuilt function for executing batch scripts.
        4. safecopy                      : copies a file to its destination, reports if file not found.

        """

        if self.op == 1:
            #Task for Gathering Stats
            #Execute Script from the log folder
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            os.chdir(self.schema)
            #The following statement generates a string which contains the absolute path of the sql script and any parameters
            sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\gather_db_stats '+self.schema, 'utf-8')
            #The following function automatically executes the sqlcommand given above
            runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)
            #The following code is used for handling error inside a single file
            log_file = "\\".join([globs.ARCHIVEFOLDER, self.phase, self.schema, "gather_db_stats.log"])
            errFound = find_errors(log_file, ["ORA-", "PLS-"])
            if errFound:
                self.status = 4
            os.chdir(globs.PROGDIR)
        elif self.op == 2:
            #Task for Counting Rows
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            os.chdir(self.schema)
            sqlcommand = bytes("@'%s\\sqls\\CountRows'"%globs.PROGDIR+ self.schema, 'utf-8')
            runSQLQuery(sqlcommand, self.schema, sys.__stdout__)
            os.chdir(globs.PROGDIR)
            
        elif self.op == 3:
            #Task for Counting Invalid Objects
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            os.chdir(self.schema)
            sqlcommand = bytes("@'%s\\sqls\\InvalidObjects'"%globs.PROGDIR+ self.schema, 'utf-8')
            runSQLQuery(sqlcommand, self.schema, sys.__stdout__)
            os.chdir(globs.PROGDIR)
            
        elif self.op == 4:
            #Task for WWFMGR Premigration Script
            progPath = os.getcwd()
            #Store location of the batch scriptfolder
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            #Switch Current Working Directory to the Script Folder
            os.chdir(scriptFolder)
            #Use Popen built-in command to execute required script
            #stdout is set to where you want to display the output, LogPipe is our custom console
            session = Popen(['premigrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            #Wait until Script Finishes Executing
            session.communicate()
            #Move to the Log Folder
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Premigration")
            #Prepare a list of files that need to be backed up
            BACKUPFILES = ['premigrate.log', 'gen_refschema.log', 'platform_db_creation.log', 'refsch_check.log', 'r_query.log']
            for f in BACKUPFILES:
                #Copy Files one by one
                safecopy(scriptFolder+f, self.schema)
            #Check All Files for Errrors
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
            os.chdir(globs.PROGDIR)
        elif self.op == 5:
            #Task for WWFMGR migration scripts
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_webworks.cmd', globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Migration")
            BACKUPFILES = ['migrate_webworks.log', 'platform_db_creation.log', 'gen_refschema.log']
            for f in BACKUPFILES:
                safecopy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
            os.chdir(globs.PROGDIR)

        elif self.op == 6:
            #Task for Monitor Premigration Scripts
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['premigrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Premigration")
            BACKUPFILES = ['premigrate.log', 'platform_db_creation.log', 'gen_refschema.log', 'refsch_check.log']
            for f in BACKUPFILES:
                safecopy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4    
            os.chdir(globs.PROGDIR)
        elif self.op == 7:
            #Task for Monitor Migration Scripts
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\monitor\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_monitor.cmd', globs.props['Monitor_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir("Migration")
            BACKUPFILES = ['migrate_monitor.log', 'platform_db_creation.log', 'gen_refschema.log', 'ema_populate_wwf.log', 'enroll_app_schema.log']
            for f in BACKUPFILES:
                safecopy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
            os.chdir(globs.PROGDIR)
        
        elif self.op == 13:
            #Task for SCPOMGR Premigration Scripts
            d = globs.saveDir()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['premigrate_scpo.cmd', globs.props['SCPO_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=sys.__stdout__)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            BACKUPFILES = ['create_scporefschema.log', 'create_wwfrefschema.log', 'grant_manu_privs.log', 'premigrate_scpo.log', 'show_badrows.log']
            for f in BACKUPFILES:
                safecopy(scriptFolder+f, self.schema)
            found = findErrorsInFiles(BACKUPFILES, self)
            globs.SignalObj.updateErrorSignal.emit("Review show_badrows.log in %s before proceeding"%("\\".join([globs.ARCHIVEFOLDER, self.phase, self.schema])))
            self.status = 4
            d.restore()
        elif self.op == 9:
            #Task for SCPOMGR Migration Scripts
            d = globs.saveDir()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_scpo.cmd', globs.props['SCPO_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=sys.__stdout__)
            session.communicate()
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            BACKUPFILES = ['create_scporefschema.log', 'create_wwfrefschema.log', 'grant_manu_privs.log', 'migrate_scpo.log']
            for f in BACKUPFILES:
                safecopy(scriptFolder+f, self.schema)
            if findErrorsInFiles(BACKUPFILES, self):
                self.status = 4
            d.restore()
        elif self.op == 10:
            #Task for Checking Row Count Matching
            phase = "Premigration"
            predct = getattr(globs,'RowCountDict'+phase)
            phase = "Postmigration"
            postdct = getattr(globs,'RowCountDict'+phase)
            res = (predct == postdct)
            if not res:
                globs.SignalObj.updateErrorSignal.emit("Row Count Matching Failed!")
                self.status = 4
        elif self.op == 11:
            #Task for Invalid Object Count Matching
            phase = "Premigration"
            predct = getattr(globs,'InvalidCountDict'+phase)
            phase = "Postmigration"
            postdct = getattr(globs,'InvalidCountDict'+phase)
            res = (predct == postdct)
            if not res:
                globs.SignalObj.updateErrorSignal.emit("Invalid Object Count Matching Failed!")
                self.status = 4
        elif self.op == 103:
            #Task for Creating Manguistics Package in JDA_SYSTEM
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
            #Task for Creating ABPP Schema if it doesn't exist 
            progPath = os.getcwd()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
            os.chdir(scriptFolder)
            session = Popen(['createAbppSchema.cmd'], stdin=PIPE, stdout=globs.LogPipe)
            session.communicate()
            os.chdir(progPath)

        elif self.op == 105:
            #Task for Providing ABPP necessary Grants
            sqlcommand = bytes('@sqls/ABPP_GRANTS', 'utf-8')
            runSQLQuery(sqlcommand, globs.props['System_Username'], globs.LogPipe)
        elif self.op == 106:
            #Task for Updating ABPP Schema
            progPath = os.getcwd()
            scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\platform\\'
            os.chdir(scriptFolder)
            session = Popen(['updateAbppSchema.cmd', '-coreServices'], stdout=globs.LogPipe, stdin = PIPE)
            session.communicate()
            os.chdir(progPath)
        elif self.op == 107:
            #Premigration Custom Script
            os.chdir(globs.ARCHIVEFOLDER)
            os.chdir(self.phase)
            sqlcommand = bytes("@'%s\\sqls\\custompremgr'"%globs.PROGDIR, 'utf-8')
            runSQLQuery(sqlcommand, 'JDA_SYSTEM', sys.__stdout__)
            os.chdir(globs.PROGDIR)
        elif self.op == 202:
            #Sample Task Error
            log_file = globs.PROGDIR+'\\tmp\\sample.log'
            errFound = find_errors(log_file, ["ORA-", "PLS-"])
            if errFound:
                self.status = 4
        globs.curErrBlock.finalize()

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
    
    q.append(Task(13,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "Premigration"))
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
    """
    This function runs in main thread and tells python exactly what to do once a task is completed.

    Here, you can write anything that you might want to update in the GUI interface realted to the task.
    """

    # The following code updates the lights depending upon the status of a task
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


    # Get ready to handle errors
    if task.status == 4:
        globs.CONTROLLER.resbtn.setDisabled(False)
        globs.CONTROLLER.fixbtn.setDisabled(False)
        globs.CONTROLLER.taskMonitor.errorBox.append("Errors Encountered While Performing Task #%d"%(task.localid+1))
        globs.CONTROLLER.taskMonitor.errorBox.append("")

    # Read Spooled RowCounts into accessible dictionaries
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



#---------------------------------------------------
# The following are some definitions of additional tasks to force execution of FixBadRows.sql
# q.append(Task(8,comp, True, 'Pre Migration', "Pre-Migrating %s"%comp, "Premigration"))
# q.append(Task(12,comp, True, 'Fix Bad Rows', "Automatic Fixing of Bad Rows", "Premigration"))

# elif self.op == 8:
#     d = globs.saveDir()
#     scriptFolder = globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\migration\\'
#     os.chdir(scriptFolder)
#     session = Popen(['premigrate_scpo.cmd', globs.props['SCPO_Password'], globs.props['WebWORKS_Password'], globs.props['System_Username'], globs.props['System_Password']], stdin=PIPE, stdout=sys.__stdout__)
#     session.communicate()
#     os.chdir(globs.ARCHIVEFOLDER)
#     os.chdir(self.phase)
#     BACKUPFILES = ['create_scporefschema.log', 'create_wwfrefschema.log', 'grant_manu_privs.log', 'premigrate_scpo.log', 'show_badrows.log']
#     for f in BACKUPFILES:
#         safecopy(scriptFolder+f, self.schema)
#     if findErrorsInFiles(BACKUPFILES, self):
#         self.status = 4
#     d.restore()
# elif self.op == 12:
#     d = globs.saveDir()
#     os.chdir(globs.ARCHIVEFOLDER)
#     os.chdir(self.phase)
#     os.chdir(self.schema)
#     sqlcommand = bytes('@'+globs.props['JDA_HOME']+'\\config\\database\\scpoweb\\migration\\FixBadRows C', 'utf-8')
#     runSQLQuery(sqlcommand, globs.props['SCPO_Username'], globs.LogPipe)
#     d.restore()