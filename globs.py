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
FROM = "Hritik.Soni@jda.com"
TO = "f2014480@pilani.bits-pilani.ac.in"
TEXT = "Sample Content"
SERVER = "mailout.jdadelivers.com"
PORT = "25"
PASSWORD = ""
COMPRESS = True
USE_TLS = False

class saveDir():
    def __init__(self):
        self.svdir = os.getcwd()
    def restore(self):
        os.chdir(self.svdir)    