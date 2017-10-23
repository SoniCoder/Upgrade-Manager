import globs
import re

def dispErr(s):
    globs.CONTROLLER.taskMonitor.errorBox.append(s)
    globs.CONTROLLER.taskMonitor.errorBox.append("")
    globs.DISP_SCREEN.errorView.addError(s)

def find_errors(filepath, patterns):
    line_no = 0
    f = open(filepath)
    re_patterns = []
    output = []
    for p in patterns:
        re_patterns.append(re.compile(p))
    while True:
        line = f.readline()
        if line == '':break
        line_no += 1
        for p in re_patterns:
            match = p.match(line)
            if match:
                output.append((line_no, p.pattern))
    if output:
        for l_no, pat in output:
            globs.SignalObj.updateErrorSignal.emit("Error Encountered in %s at line %d matching pattern %s"%(filepath, l_no, pat))
        return True
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