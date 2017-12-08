set pages 45999;
set linesize 200
col count format 999,999,999;
spool count(&1)list.txt

select
   table_name,
   to_number(
   extractvalue(
      xmltype(
         dbms_xmlgen.getxml('select count(1) c from '||table_name))
    ,'/ROWSET/ROW/C')) count
from 
   user_tables
order by 
   table_name;

spool off;