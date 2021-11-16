#DBRazor

from typing import *
import argparse
#import pyjion
import cffi

#Drivers para Gestores BD-------
import sqlite3
import psycopg2
import pypyodbc
import mysql.connector
import cx_Oracle
#-------------------------------
#Drivers para NoSQL-------------
import pymongo
import redis
import pysolr
import elasticsearch
import cassandra
import couchdb
import hbase
import neo4j
import ibm_db
#-------------------------------

import streams
import blockParser
import SQLTypes
import io
import CSVTransformer
import os

#Rich------------------------------------
import rich
from rich.console import Console
console = Console()
#---------------------------------------


#Experimentos con jpype1---------------------------------
import jpype
import jpype.imports
from jpype.types import *
import jaydebeapi #API para JDBC
#Establecer un JAVA_HOME si no lo hay
#Deberia poderse obtener de la linea de comandos
if not "JAVA_HOME" in os.environ:
    os.environ["JAVA_HOME"] = "e:/OpenJDK16/bin"
jpype.startJVM(classpath=["jackcess-3.0.0.jar","commons-logging-1.2.jar","commons-lang3-3.8.1.jar"])
#-------------------------------------------------------


__version__ = "1.0.0.1"

def csv_export( results : List[Tuple], sep : str) -> str:
    '''
    Exporta resultados a CSV.
    '''
    buff = io.StringIO()
    for row in results:
        buff.write(sep.join([str(x) for x in row]))
        buff.write("\n")
    return buff.getvalue()[:-1]


#Configuracion
SUPPORTED_DATABASES : List[str] = ["sqlite","access","sqlserver","postgres","mysql","mariadb","oracle","db2","mongodb","elasticsearch","solr","redis","cassandra","neo4j"]

EXPORT_OPTIONS : List[str] = ["text","csv","json","sql","html","xml","excel","ods","doc","pdf"]

EXPORT_FUNCS : Dict[str,Callable] = {
    "csv" : csv_export,
    "json" : CSVTransformer.CSVRowToJSON,
    "sql" : CSVTransformer.CSVRowToSQL
}

ACCESS_CONN_STRING = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;Uid=%s;Pwd=%s;" #odbc
ACCESS_CONN_STRING2 = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=%s;User Id=%s;Password=%s;" #OLE DB/ADO
ACCESS_CONN_STRING3 = 'Provider=Microsoft.ACE.OLEDB.12.0;Data Source=%s;Extended Properties="Excel 8.0;HDR=YES";'
SQLSERVER_CONN_STRING = "DRIVER={sql server};server=%s;Database=%sa;UID=%s;PWD=%s"

#Lee una cadena de conexion y extrae: kind,user,database,host y password
def getConnStrParams(connstr : str, 
                     required = ["kind","database","user","password","host","name"], 
                     field_sep=";", 
                     values_sep="=") -> Dict[str,str]:
    '''
    Lee una cadena de conexion y extrae los campos
    separados por ";" y los valores separados por "=". 
    Por defecto busca: kind,user,database,name,host y password.
    Formato de la cadena: "xx=yy;aa=bb;..."
    Separa por defecto por ; y =, aunque esto es configurable.
    '''
    cfg = dict([x.split(values_sep) for x in connstr.split(field_sep)])
    #Asegurar que estan todos los campos
    for item in required:
        if not item in cfg:
            raise Exception(f"Cadena de conexion no valida: Falta el parametro {item}")
    return cfg


def DBConnectionFactory(cfgdict : dict) -> Any:
    '''
    Construye una connection a una de las BBDD soportadas
    y la devuelve
    '''
    print(cfgdict)
    kind = cfgdict["kind"]
    assert kind in SUPPORTED_DATABASES
    if kind == "sqlite":
        #No usa user ni host ni password.
        return sqlite3.connect(cfgdict["host"])
    elif kind == "access":
        #access
        connstr = ACCESS_CONN_STRING % (cfgdict["host"], cfgdict["user"], cfgdict["password"])
        print(f"ACCESS DRIVER: {connstr}")
        return pypyodbc.connect(connstr)
    elif kind == "sqlserver":
        #sqlserver
        connstr = SQLSERVER_CONN_STRING % (cfgdict["host"],cfgdict["database"], cfgdict["user"], cfgdict["password"])
        print(f"SQLSERVER DRIVER: {connstr}")
        return pypyodbc.connect(connstr)
    elif kind == "postgres":
        #postgres
        return psycopg2.connect(user = cfgdict["user"],
                                   password = cfgdict["password"],
                                   host = cfgdict["host"],
                                   port = cfgdict["port"],
                                   database = cfgdict["database"])
    elif kind == "oracle":
        #postgres
        return cx_Oracle.connect(user = cfgdict["user"],
                                   password = cfgdict["password"],
                                   host = cfgdict["host"],
                                   port = cfgdict["port"],
                                   encoding = cfgdict["encoding"])
    elif kind in ["mysql","mariadb"]:
        #mysql/mariadb
        return mysql.connector.connect(user = cfgdict["user"],
                                   password = cfgdict["password"],
                                   host = cfgdict["host"])
    else:
        print("Tipo de Base de Datos no implemetado todavia.")
        return None




class DBRazor:
    '''
    DBRazor
    '''
    def __init__(self, config : Union[argparse.Namespace,Dict[str,str]]):
        '''
        Constructor
        '''
        self._connections = {}
        self._buildConnections(config.connstring)
        self._queries = config.query
        self._results = {} #Resultados de queries
        self._log = False #para --log o --verbose

        if type(config) == argparse.Namespace:
            self._export = config.export
            #
            self._outfile = config.outfile
            self._encoding = config.encoding
            self._csvsep = config.csvsep
        else:
            self._export = config.get("export",None)
            #
            self._outfile = config.get("outfile","resultados.txt")
            self._encoding = config.get("encoding","utf-8")
            self._csvsep = config.get("csvsep",",")


    def _buildConnections(self,connstr_list):
        '''
        Construye las conexiones.
        '''
        for conn in connstr_list:
            params = getConnStrParams(conn)
            self._connections[params["name"]] = DBConnectionFactory(params)
        print(self._connections)


    def runQueries(self):
        '''
        Ejecuta las queries y guarda los resultados con nombre.
        '''
        #print(self._connections)
        for q in self._queries: #logEntry
            print(f"Running query: {q[0]} with connection: {q[1]}")
            qry,cnn,store_as = q
            #Coger la conexion para ejecutarla
            conn = self._connections[cnn]
            cur = conn.cursor()
            cur.execute(qry)
            meta = cur.description #????
            print(f"METADATA: {meta}")
            results = []
            types_get = False
            for row in cur.fetchall():
                if not types_get:
                      print(f"TYPES: {[type(x) for x in row]}")
                      types_get = True
                #print(row)
                results.append(row)
            self._results[store_as] = results
        #print(self._results)



    def run(self):
        '''
        Ejecuta la query y exporta los resultados
        si se indica.
        '''
        #Primero necesitamos una conexion
        if self._dbtype =="sqlite":
            self._conn = sqlite3.connect(self._connstring)
        else:
            print("Todavia no esta disponible el tipo de BBDD {}".format(self._dbtype))
            return 
        self._results = []
        self._cursor = self._conn.cursor()
        self._cursor.execute(self._query)
        self._lastrowid = self._cursor.lastrowid
        print(f"lastrowid : {self._lastrowid}")
        print(f"rowcount: {self._cursor.rowcount}")
        self._metadata = self._cursor.description
        fnames = [x[0] for x in self._metadata]
        for row in self._cursor.fetchall():
            self._results.append(row)
        self._conn.close()
        if self._export != None:
            print(f"Exportando resultados a {self._export}")
            if self._export in EXPORT_FUNCS:
                xfun = EXPORT_FUNCS[self._export]
                if self._export == "csv":
                    exported = xfun(self._results,self._csvsep)
                    if self._outfile != None:
                        with open(self._outfile,"w",encoding= self._encoding) as out:
                            out.write(exported)
                    else:
                        print(exported)
                elif self._export == "json":
                    print("Exportando a JSON")
                elif self._export == "sql":
                    print("exportando a SQL")
            else:
                print(f"No hay funcion definida para exportar a {self._export}")
        else:
            print("No hay que exportar los resultados")




if __name__ == '__main__':

    print(console.size)
    print(console.encoding)
    print(console.color_system)
    console.print("[blue underline]Looks like a link", justify="center") 
    #console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")   

    cnstr = "kind=sqlite;host=World.db3;database=World;user=;password=;name=sqlite_conn1"
    getConnStrParams(cnstr)
    print(getConnStrParams(cnstr))

    #Configuracion segun argumentos de CL
    parser = argparse.ArgumentParser(description='DBRazor. Utilidades para BBDD.')
    #Configurar argumentos de CL
    parser.add_argument("-c","--connstring",
                        help = "Cadenas de conexiones a la BBDD.",
                        type = str,
                        action = "append",
                        required = True)
    parser.add_argument("-q","--query",
                        help = "Cadenas de consultas.",
                        nargs = 3, #query, conn_name , name_to_store_results
                        action = "append",
                        type = str)
    parser.add_argument("-o","--outfile",
                        help = "Archivo de salida para exportaciones.",
                        default = "exported.txt",
                        type = str)
    parser.add_argument("-e","--encoding",
                        help = "Codificacion del texto.",
                        default = "utf-8",
                        type = str)
    parser.add_argument("-s","--csvsep",
                        help = "Separador para exportar a CSV.",
                        default = ",",
                        type = str)
    parser.add_argument("-x","--export",
                        help = "Formato para exportar.",
                        nargs = 2, #tipo,nombre_resultado_a_exportar
                        type = str)
    cl_config = parser.parse_args()
    print(cl_config)
    razor = DBRazor(cl_config)
    print(razor)
    print(repr(razor))
    razor.runQueries()
    print("OK")
    '''
    #JPype
    import java.io
    #import com.healthmarketscience
    from com.healthmarketscience.jackcess import Database,Table,DatabaseBuilder,Row
    db = DatabaseBuilder.open(java.io.File("Northwind.mdb"))
    table = db.getTable("Employees")
    for row in table:
        print(row)
    '''