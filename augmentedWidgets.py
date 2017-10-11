from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QCenteredLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.setAlignment(Qt.AlignCenter)

class QHLine(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class VBOXNOEXMG(QVBoxLayout):
    def __init__(self, parent= None):
        QVBoxLayout.__init__(self, parent)
        defMG = self.getContentsMargins()
        self.setContentsMargins(0, defMG[1], 0, defMG[3])
class HBOXNOEXMG(QHBoxLayout):
    def __init__(self, parent= None):
        QHBoxLayout.__init__(self, parent)
        defMG = self.getContentsMargins()
        self.setContentsMargins(defMG[0], 0, defMG[2], 0)

class VBOXNOMG(QVBoxLayout):
    def __init__(self, parent= None):
        QVBoxLayout.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
class HBOXNOMG(QHBoxLayout):
    def __init__(self, parent= None):
        QHBoxLayout.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)