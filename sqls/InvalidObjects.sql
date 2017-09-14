set pages 999;
set linesize 1000
col count format 999,999,999;
spool invalidObj(&1).txt

select owner, constraint_name, table_name, status from user_constraints where owner='&1' and (status <> 'ENABLED' or validated='NOT VALIDATED');


spool off;