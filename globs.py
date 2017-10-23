import os

# DISP_SCREEN = None

ARCHIVEFOLDER = None

RowCountDictPREMGR = {}
RowCountDictPOSTMGR = {}
InvalidCountDictPREMGR = {}
InvalidCountDictPOSTMGR = {}

class saveDir():
    def __init__(self):
        self.svdir = os.getcwd()
    def restore(self):
        os.chdir(self.svdir)    