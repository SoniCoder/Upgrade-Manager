DECLARE 
val NUMBER;
BEGIN
FOR I IN (SELECT TABLE_NAME FROM USER_TABLES) LOOP
EXECUTE IMMEDIATE 'SELECT count(*) FROM ' || i.table_name INTO val;
DBMS_OUTPUT.PUT_LINE(i.table_name || ' ==> ' || val );
END LOOP;
END;




set pages 999;

col count format 999,999,999;
spool countlist.txt

select
   table_name,
   to_number(
   extractvalue(
      xmltype(
         dbms_xmlgen.getxml('select count(*) c from '||table_name))
    ,'/ROWSET/ROW/C')) count
from 
   user_tables
order by 
   table_name;