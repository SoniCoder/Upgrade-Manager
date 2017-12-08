"""
Author: Hritik Soni

Description:

Module containing important helper functions mainly to be used in the run function
of the task system
"""

import globs
from subprocess import Popen, PIPE

def runSQLQuery(sqlCommand, user, out = PIPE):
    """
    Description: This function executes an sql script by passing it to SQLPlus and wait
    until execution finishes

    Params:
    sqlCommand: This is the string that is directly passed to SQLPlus after connect string or
    after connection has been established

    user: Actual User String which is used for connection. Example: WWFMGR, SYSTEM, etc.abs
    You can use globs.props['System_Username'] for specifying it using property file

    out: One of the three - globs.LogPipe (For Displaying output on Custom Console), sys.__stdout__ (For output on orig console)
    or PIPE (No output displayed)

    """
    # Get Password of the User from Property File Read Earlier
    password = globs.UserPassDict[user]
    # Prepare the connect string 
    connectString = user+'/'+password+"@"+globs.props['TargetServer']+'/'+globs.props['Service']
    # Open a Popen session
    session = Popen(['sqlplus', '-S', connectString], stdin=PIPE, stdout=out)
    # Foward the sqlCommand to SQLPlus after successful connection
    session.stdin.write(sqlCommand)
    # Wait until Script finishes
    return session.communicate()

def RUNSQLQUERY(sqlCommand, user, out):
    sqlCommand = bytes(sqlCommand, 'utf-8')
    runSQLQuery(sqlCommand, user, out)


#--FUTURE-- The following code was meant to be used for reading tasks from text files

# FUNCTIONS = {
#     "RUNSQLQUERY": lambda sqlCommand, user, out : RUNSQLQUERY(sqlCommand, user, out)
# }