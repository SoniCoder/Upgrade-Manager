"""
Author: Hritik Soni

Description: Module for Storing Signal Classes
"""

from PyQt5.QtCore import *

class CSignal(QObject):
    updateErrorSignal = pyqtSignal(str)