sqlplus system/manager@localhost/O12CR102 @refresh_db

impdp system/manager@localhost/O12CR102 schemas=scpomgr dumpfile=sample78.dp.dmp