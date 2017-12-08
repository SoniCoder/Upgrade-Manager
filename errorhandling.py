"""
Author: Hritik Soni

Description: Module for the whole error handling mechanisms and functions involved
"""

import globs
import re # Import Regular Expression Library to Search for Error Patterns  

from net import *

class ErrorBlock:
    """
    This Class is used to create an object for initiating error capturing
    everytime a new task is run and finally send any errors via mail
    """
    def __init__(self, SUBJECT):
        self.errList = []
        globs.SUBJECT = SUBJECT
    def addError(self, s):
        self.errList.append(s)
    def finalize(self):
        globs.PASSWORD = "Dbz123!!!!"
        globs.TEXT = "\n".join(self.errList)
        if self.errList and globs.MAIL_ON:
            send()
        globs.ATTACHMENTS = []



def dispErr(s):
    """
    Function meant to be executed in Main Thread
    It shows new errors in error console and error table
    """
    globs.CONTROLLER.taskMonitor.errorBox.append(s)
    globs.CONTROLLER.taskMonitor.errorBox.append("")
    globs.DISP_SCREEN.errorView.addError(s)


def find_errors(filepath, patterns):
    """
    Function to find errors in a single file for given pattern list
    It also emits signal whenever an error is found and also passes the error to
    the current error capturing block.
    """
    line_no = 0
    try:
        f = open(filepath)
        re_patterns = []
        output = []
        for p in patterns:
            re_patterns.append(re.compile(p))
        while True:
            # Read line by line and search each line for all patterns
            line = f.readline()
            if line == '':break
            line_no += 1
            for p in re_patterns:
                match = p.match(line)
                if match:
                    output.append((line_no, p.pattern))
        if output:
            # If any errors encountered send them appropriately and return True
            if filepath not in globs.ATTACHMENTS:
                globs.ATTACHMENTS.append(filepath)
            if len(output) > 1000:
                # If error count in current file is more than 1000, return a single error
                err = "Error Encountered in %s for more than 1000 times"%(filepath)
                globs.curErrBlock.addError(err)
                globs.SignalObj.updateErrorSignal.emit(err)
                return True
            else:
                for l_no, pat in output:
                    err = "Error Encountered in %s at line %d matching pattern %s"%(filepath, l_no, pat)
                    globs.curErrBlock.addError(err)
                    globs.SignalObj.updateErrorSignal.emit(err)
                return True
        return False     
    except:
        return False



def checkIfAllFixed():
    tb = globs.DISP_SCREEN.errorView
    rows = tb.rowc
    fixed = True
    for i in range(rows):
        chk = tb.cellWidget(i, 0).chkbox.isChecked()
        if not chk:
            fixed = False
            break
    return fixed

def selallerrors():
    tb = globs.DISP_SCREEN.errorView
    rows = tb.rowc
    for i in range(rows):
        chk = tb.cellWidget(i, 0).chkbox.setChecked(True)
        
    return