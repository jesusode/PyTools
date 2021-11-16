#Pruebas de pypyodbc

import sqlite3
import argparse
import psycopg2
import pypyodbc
import mysql.connector
import streams
from adoV6 import *



ACCESS_CONN_STRING = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;Uid=%s;Pwd=%s;" #odbc
ACCESS_CONN_STRING = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=%s;User Id=%s;Password=%s;" #OLE DB/ADO
ACCESS_CONN_STRING = 'Provider=Microsoft.ACE.OLEDB.12.0;Data Source=%s;Extended Properties="Excel 8.0;HDR=YES";'


#Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:\myFolder\myAccessFile.accdb;Persist Security Info=False;

connstr = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=e:\\ProyectosPython\\diarioUVI\\Northwind.MDB;Uid=;Pwd=;"
#connstr= "Provider=Microsoft.ACE.OLEDB.1.0;Data Source=e:\\ProyectosPython\\diarioUVI\\Northwind.MDB;User Id=;Password=;"
print(f"ACCESS DRIVER: {connstr}")
#pypyodbc.connect(connstr)
con=Connection(connstr,1).getConnection()
rst=Recordset()