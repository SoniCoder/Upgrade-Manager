import os

"""
AUTHOR: Hritik Soni

Description: Module for sharing global variables among other modules


"""

# DISP_SCREEN = None

ARCHIVEFOLDER = None

RowCountDictPremigration = {}
RowCountDictPostmigration = {}
InvalidCountDictPremigration = {}
InvalidCountDictPostmigration = {}

# Mailer Options
MAIL_ON = True
ATTACHMENTS = []
SUBJECT = "Sample Subject"
FROM = "hothritik1@gmail.com"
TO = "f2014480@pilani.bits-pilani.ac.in"
TEXT = "Sample Content"
SERVER = "smtp.gmail.com"
PORT = "587"
PASSWORD = ""
COMPRESS = True

class saveDir():
    def __init__(self):
        self.svdir = os.getcwd()
    def restore(self):
        os.chdir(self.svdir)    