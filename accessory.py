import globs
import os
from errorhandling import find_errors

def findErrorsInFiles(FILELIST, taskobj):
    anyFound = False
    for f in FILELIST:
        log_file = "\\".join([globs.ARCHIVEFOLDER, taskobj.phase, taskobj.schema, f])
        errFound = find_errors(log_file, ["ORA-", "PLS-"])
        if errFound: anyFound = True
    return anyFound

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
