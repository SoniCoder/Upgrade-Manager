from PyQt5.QtCore import *

class CSignal(QObject):
    updateErrorSignal = pyqtSignal(str)