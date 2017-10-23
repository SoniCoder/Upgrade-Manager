import globs
from subprocess import Popen, PIPE

def runSQLQuery(sqlCommand, user, out = PIPE):
    password = globs.UserPassDict[user]
    connectString = user+'/'+password+"@"+globs.props['TargetServer']+'/'+globs.props['Service']
    session = Popen(['sqlplus', '-S', connectString], stdin=PIPE, stdout=out)
    session.stdin.write(sqlCommand)
    return session.communicate()

def RUNSQLQUERY(sqlCommand, user, out):
    sqlCommand = bytes(sqlCommand, 'utf-8')
    runSQLQuery(sqlCommand, user, out)

FUNCTIONS = {
    "RUNSQLQUERY": lambda sqlCommand, user, out : RUNSQLQUERY(sqlCommand, user, out)
}