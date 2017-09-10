import cx_Oracle
import os
import threading
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *
from collections import deque
from subprocess import Popen, PIPE
from time import sleep

from GUI_Design import *

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
    print()
    return (True, None, None)

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


def readInvalidObjects():
    globals()['InvalidCountDict'] = {}
    dct = globals()['InvalidCountDict']
    for comp_i in range(len(globals()['COMPONENTS'])):
        comp = globals()['COMPONENTS'][comp_i]
        dct[comp] = []
        lst = dct[comp]
        fileName = "logs/" + "invalidObj(%s).txt"%comp
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

def readRows():
    globals()['RowCountDict'] = {}
    dct = globals()['RowCountDict']
    for comp_i in range(len(globals()['COMPONENTS'])):
        comp = globals()['COMPONENTS'][comp_i]
        dct[comp] = []
        lst = dct[comp]
        fileName = "logs/" + "count(%s)list.txt"%comp
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

def updateTable(schema):
    print("Updating Table for schema %s"%schema)
    dct = globals()['RowCountDict']
    lst = dct[schema]
    globals()['DISP_SCREEN'].tview.setData(lst, "Table Name in schema %s; Row Count"%schema)

def updater(task):
    if task.labels:
        imgLbl = globals()['DISP_SCREEN'].statGather.rightList[task.localid]
        if task.status == 1:       
            pixmap = QPixmap('images/yellow.png')
        elif task.status == 2:
            pixmap = QPixmap('images/green.png')
        imgLbl.setPixmap(pixmap)
        
    if task.op == 100:
        if task.status == 2:
            readRows()
            globals()['DISP_SCREEN'].currentWidget.hide()
            globals()['DISP_SCREEN'].tview.show()
            globals()['DISP_SCREEN'].currentWidget = globals()['DISP_SCREEN'].tview
            dct = globals()['RowCountDict']
            lst = dct[globals()['COMPONENTS'][1]]
            globals()['DISP_SCREEN'].tview.setData(lst, "Table Name in schema %s; Row Count"%globals()['COMPONENTS'][1])
            rowcmenu = globals()['RowCMenu']
            print("Creating and Adding New View Row Actions")
            actions = [QAction(comp, globals()['MAIN_WINDOW']) for comp in globals()['COMPONENTS']]            
            funcs = []
            for act_i in range(len(actions)):
                rowcmenu.addAction(actions[act_i])
                actions[act_i].triggered.connect(lambda f, i = act_i: updateTable(globals()['COMPONENTS'][i]))
    elif task.op == 101:
        if task.status == 2:
            readInvalidObjects()
            globals()['DISP_SCREEN'].currentWidget.hide()
            globals()['DISP_SCREEN'].tview.show()
            globals()['DISP_SCREEN'].currentWidget = globals()['DISP_SCREEN'].tview
            dct = globals()['InvalidCountDict']
            lst = dct[globals()['COMPONENTS'][4]]
            globals()['DISP_SCREEN'].tview.setData(lst, "Owner; Constraint_Name; Table_Name; Status")
            # rowcmenu = globals()['RowCMenu']
            # print("Creating and Adding New View Row Actions")
            # actions = [QAction(comp, globals()['MAIN_WINDOW']) for comp in globals()['COMPONENTS']]            
            # funcs = []
            # for act_i in range(len(actions)):
            #     rowcmenu.addAction(actions[act_i])
            #     actions[act_i].triggered.connect(lambda f, i = act_i: updateTable(globals()['COMPONENTS'][i]))
    elif task.op == 102:
        if task.status == 2:
            globals()['DISP_SCREEN'].currentWidget.hide()
            globals()['DISP_SCREEN'].statGather.show()
            globals()['DISP_SCREEN'].currentWidget = globals()['DISP_SCREEN'].statGather
class Task():
    lblcntr = 0
    def __init__(self, op, schema = None, labels = False, TaskName = None):
        self.schema = schema
        self.op = op
        self.status = 0
        self.localid = None
        self.labels = labels
        if self.labels:
            dispLbl = QLabel(TaskName)
            dispLbl.setFixedHeight(30)
            globals()['DISP_SCREEN'].statGather.leftList.append(dispLbl)
            globals()['DISP_SCREEN'].statGather.leftLayout.addWidget(dispLbl)
            imgLbl = QLabel()
            pixmap = QPixmap('images/red.png')
            imgLbl.setPixmap(pixmap)
            globals()['DISP_SCREEN'].statGather.rightList.append(imgLbl)
            globals()['DISP_SCREEN'].statGather.rightLayout.addWidget(globals()['DISP_SCREEN'].statGather.rightList[-1])
            self.localid = Task.lblcntr
            Task.lblcntr += 1
    def runtask(self):        
        if self.op == 1:
            sqlcommand = bytes('@'+globals()['PROPS']['JDA_HOME']+'\\config\\database\\scpoweb\\gather_db_stats '+self.schema, 'utf-8')
            runSQLQuery(sqlcommand, globals()['PROPS']['System_Username'], globals()['LogPipe'])
        elif self.op == 2:
            sqlcommand = bytes('@sqls/CountRows '+ self.schema, 'utf-8')
            runSQLQuery(sqlcommand, self.schema, PIPE)
        elif self.op == 3:
            sqlcommand = bytes('@sqls/InvalidObjects '+ self.schema, 'utf-8')
            runSQLQuery(sqlcommand, self.schema, PIPE)
        elif self.op == 4:
            progPath = os.getcwd()
            scriptFolder = globals()['PROPS']['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            os.chdir(scriptFolder)

            session = Popen(['premigrate_webworks.cmd', globals()['PROPS']['WebWORKS_Password'], globals()['PROPS']['System_Username'], globals()['PROPS']['System_Password']], stdin=PIPE, stdout=globals()['LogPipe'])
            session.communicate()
            os.chdir(progPath)
            pass
        elif self.op == 5:
            progPath = os.getcwd()
            scriptFolder = globals()['PROPS']['JDA_HOME']+'\\config\\database\\platform\\migration\\'
            os.chdir(scriptFolder)
            session = Popen(['migrate_webworks.cmd', globals()['PROPS']['WebWORKS_Password'], globals()['PROPS']['System_Username'], globals()['PROPS']['System_Password']], stdin=PIPE, stdout=globals()['LogPipe'])
            session.communicate()
            os.chdir(progPath)
        elif self.op == 102:
            sleep(3)
class UpdateSignal(QObject):
    updateTask = pyqtSignal(Task)

class prThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
    def run(self):    
        q = globals()['TQueue']
        sig = globals()['UpdateSignal'].updateTask
        while q:
            task = q[0]
            sleep(0.5)
            print("Running Task",task.op,task.schema)
            sleep(0.5)
            task.status = 1
            sig.emit(task)
            sleep(1)
            task.runtask()
            task.status = 2
            sig.emit(task)
            q.popleft()
        sleep(0.5)
        print("Migration Procedure Completed")
        sleep(0.5)

def execute():
    p = Popen("sample.bat", cwd=os.getcwd())
    stdout, stderr = p.communicate()

def init():
    globals()['SCHEMA_CREDS_KEYS'] = [('System_Username', 'System_Password'), ('WebWORKS_Username', 'WebWORKS_Password'), ('ABPP_Username', 'ABPP_Password'), ('Monitor_Username', 'Monitor_Password'), ('JDA_SYSTEM_Username', 'JDA_SYSTEM_Password'), ('SCPO_Username', 'SCPO_Password')]
    globals()['CRED_DICT'] = {
        'System_Username':'System_Password', 
        'WebWORKS_Username':'WebWORKS_Password',
        'ABPP_Username':'ABPP_Password',
        'Monitor_Username':'Monitor_Password',
        'JDA_SYSTEM_Username':'JDA_SYSTEM_Password',
        'SCPO_Username':'SCPO_Password'
    }
    globals()['TQueue'] = deque()
    globals()['UpdateSignal'] = UpdateSignal()
    globals()['UpdateSignal'].updateTask.connect(updater)
    globals()['LogPipe'] = LogPipe()
def prepareTasks():
    q = globals()['TQueue']
    for comp_i in range(len(globals()['COMPONENTS'])):
        comp = globals()['COMPONENTS'][comp_i]
        q.append(Task(1,comp, labels = True, TaskName = 'Stat Gather: '+ comp))

    for comp_i in range(len(globals()['COMPONENTS'])):
        comp = globals()['COMPONENTS'][comp_i]
        q.append(Task(2,comp))
    q.append(Task(100))
    for comp_i in range(len(globals()['COMPONENTS'])):
        comp = globals()['COMPONENTS'][comp_i]
        q.append(Task(3,comp))
    q.append(Task(101))
    q.append(Task(102))
    comp = globals()['PROPS']['WebWORKS_Username']
    q.append(Task(4,comp, labels = True, TaskName = 'Pre Migration: '+ comp))
    q.append(Task(5,comp, labels = True, TaskName = 'Migration: '+ comp))
    comp = globals()['PROPS']['Monitor_Username']
    q.append(Task(6,comp, labels = True, TaskName = 'Pre Migration: '+ comp))
    q.append(Task(7,comp, labels = True, TaskName = 'Migration: '+ comp))
    


def migrate():
    print("Creating and Starting Task Processor Thread") 
    globals()['vschkscr'].btn.setDisabled(True)
    th = prThread()
    th.start()



def queryComponents():
    dbpath = globals()['PROPS']['TargetServer'] + ":" + globals()['PROPS']['Port'] + "/" + globals()['PROPS']['Service']
    con = cx_Oracle.connect(globals()['PROPS']['WebWORKS_Username'], globals()['PROPS']['WebWORKS_Password'], dbpath)
    cur = con.cursor()
    print("Querying Schema Names")
    cur.execute('select DISTINCT(SCHEMA_NAME) from csm_application')
    comps = []
    for result in cur:
        comps.append(result[0])
    cur.close()

    augComps = []
    augComps.append(globals()['PROPS']['JDA_SYSTEM_Username'].upper())
    augComps.append(globals()['PROPS']['WebWORKS_Username'].upper())
    augComps.append(globals()['PROPS']['ABPP_Username'].upper())
    augComps.append(globals()['PROPS']['Monitor_Username'].upper())

    comps.remove(globals()['PROPS']['WebWORKS_Username'].upper())
    comps.remove(globals()['PROPS']['Monitor_Username'].upper())
    comps.remove(globals()['PROPS']['SCPO_Username'].upper())

    augComps += comps

    augComps.append(globals()['PROPS']['SCPO_Username'].upper())


    globals()['COMPONENTS'] = augComps


    cur = con.cursor()
    print("Querying Current Version")
    cur.execute("select VALUE from csm_schema_log where name='DATABASE_VERSION'")
    result = cur.fetchone()
    globals()['COMPVER'] = result[0]
    cur.close()
    con.close()   

    print("Performing Target Version Check")
    targetv_path = globals()['PROPS']['JDA_HOME'] + '\\' + 'install\\platform.version'
    f = open(targetv_path)
    line = f.readline()
    line = f.readline()
    targetVersion = line.split(':')[1].strip()
    print("Found Target Version:", targetVersion)
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

    globals()['UserPassDict'] = {}
    for user_cat in globals()['CRED_DICT']:
        globals()['UserPassDict'][props[user_cat]] = props[globals()['CRED_DICT'][user_cat]] 

def runSQLQuery(sqlCommand, user, out = PIPE):
    password = globals()['UserPassDict'][user]
    connectString = user+'/'+password+"@"+globals()['PROPS']['TargetServer']+'/'+globals()['PROPS']['Service']
    # print(connectString)
    #session = Popen(['sqlplus', '-S', connectString], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    session = Popen(['sqlplus', '-S', connectString], stdin=PIPE, stdout=out)
    session.stdin.write(sqlCommand)
    return session.communicate()


class VersionCheckerScreen(QWidget):
    def __init__(self, parent = None):     
        QWidget.__init__(self, parent)
        self.setGeometry(50, 50, 400, 40*len(globals()['COMPONENTS']) + 60)
        self.design()
    
    def design(self):
        vtable = QTableWidget(self)
        tableWidth = 400
        vtable.move(0, 20)
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

        self.btn = QPushButton("Start Migration Procedure", self)
        self.btn.move(20,self.height() - 20)
        self.btn.clicked.connect(migrate)
        vtable.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def sizeHint(self):
        return QSize(400,300)
class Window(QMainWindow):
    def __init__(self):     
        QMainWindow.__init__(self)
        init()
        self.setGeometry(50, 50, 1280, 720)
        self.setWindowTitle("Upgrade Manager")
        self.setWindowIcon(QIcon('icon.png'))
        self.design()
        sys.stdout = EmittingStream()
        sys.stdout.textWritten.connect(self.normalOutputWritten)
        self.load()
        self.show()
        globals()['MAIN_WINDOW'] = self
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
	
    def design(self):
        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        premgrMenu = mainMenu.addMenu('&Pre-Migration')
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
        globals()['RowCMenu'] = rowCounts
        contentScreen = QWidget(self)
        self.setCentralWidget(contentScreen)

        self.primaryLayout = QHBoxLayout(contentScreen)
        #contentScreen.setLayout(self.primaryLayout)


        
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
        globals()['DISP_SCREEN'] = self.rightSide
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
        # globals()['VSCHKINST'] = VersionCheckerWindow()
        if('vschkscr' not in globals()):
            globals()['vschkscr'] = VersionCheckerScreen(self.actionScreen)
            self.actionScreen.layout.addWidget(globals()['vschkscr'])
            self.connectionScreen.hide()
            self.rightSide.currentWidget.hide()
            #self.rightSide.testLbl.show()
            self.rightSide.statGather.show()
            self.rightSide.currentWidget = self.rightSide.statGather
            prepareTasks()
        # self.vschkscr.move(100, 100)
        #self.hide()

    def execute(self):
        execute()



    def load(self):
        self.readProperties()

    @pyqtSlot(str)
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        #sys.__stdout__.write(text)
        #Maybe QTextEdit.append() works as well, but this is how I do it:
        # cursor = self.ConTextField.textCursor()
        # cursor.movePosition(cursor.End)
        # cursor.insertText(text)
        # #self.ConTextField.setTextCursor(cursor)
        # self.ConTextField.ensureCursorVisible()

        self.ConTextField.moveCursor(QTextCursor.End)
        self.ConTextField.insertPlainText( text )
        QApplication.processEvents()

    def readProperties(self):
        readProperties()
        self.connectionScreen.dbserver.setText(globals()['PROPS']['TargetServer'])
        self.connectionScreen.port.setText(globals()['PROPS']['Port'])
        self.connectionScreen.sid.setText(globals()['PROPS']['SID'])
        self.connectionScreen.service.setText(globals()['PROPS']['Service'])