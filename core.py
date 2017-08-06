import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *
from subprocess import Popen

from config import *

def execute():
    p = Popen("sample.bat", cwd=os.getcwd())
    stdout, stderr = p.communicate()


class Window(QMainWindow):
    def __init__(self):     
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 400)
        self.setWindowTitle("AppDB Updater")
        self.design()
        self.show()
	
    def design(self):
        btn = QPushButton("Execute", self)
        btn.clicked.connect(self.execute)
        btn.resize(btn.minimumSizeHint())
        btn.move(20,40)
	
    def execute(self):
        execute()