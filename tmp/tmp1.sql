select * from v$tablespace

WWFDATA;

CREATE TABLESPACE EMADATA
  DATAFILE 'C:\oracle\oradata\O12CR102\EMADATA01.dat' 
    SIZE 20M
  ONLINE;
  
  alter user abppmgr identified by abppmgr
  
  commit
  
  drop user wwfmgr cascade;
  drop user emamgr cascade;
  drop user abppmgr cascade;
  drop user jda_system cascade;
  
  
  GRANT SELECT_CATALOG_ROLE TO ABPPMGR;
GRANT CREATE SESSION TO ABPPMGR;
GRANT CREATE TABLE TO ABPPMGR;
GRANT CREATE VIEW TO ABPPMGR;
GRANT CREATE PROCEDURE TO ABPPMGR;
GRANT CREATE TRIGGER TO ABPPMGR;
GRANT CREATE SEQUENCE TO ABPPMGR;
GRANT CREATE SYNONYM TO ABPPMGR;
GRANT CREATE MATERIALIZED VIEW TO ABPPMGR;

ALTER SYSTEM SET SEC_CASE_SENSITIVE_LOGON = FALSE;

select * from wwfmgr.csm_application;

select * from wwfmgr.csm_schema_log   where name='DATABASE_VERSION';

select * from wwfmgr.csm_schema_log  where name='SCPODB_VERSION'