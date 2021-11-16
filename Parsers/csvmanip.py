# -*- coding: utf-8 -*-
# generated code 
import sys
sys.path.append("./modules")
from typing import *
import math
import json
import sqlite3
import os
import os.path
import itertools
import shutil
import re
from bs4 import BeautifulSoup

import teletype
import pprint
import prettytable
import webbrowser
import sys
import os
import mini_tkbasic
import random
import pyexcel
import pyexcel_ods3
import pyexcel_xls
import pyexcel_xlsx
import pyexcel_pygal

import streams
from streams.dictutils import *
from streams.fileutils import *
import copy
_copy=copy.deepcopy

from streams.CSVFileIterator import *
from streams.Streams import *
from RandomUtils import *
from OOUtils import *
import minimal_ado
import subprocess

htmltemplate = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>{0}</title>
</head>
<body>
<pre>
{1}
</pre>
</body>
</html>"""


htmltemplate2 = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>{0}</title>
</head>
<body>
{1}
</body>
</html>"""


help_string = """
Comandos permitidos:
    help :
    ------
        Muestra la ayuda del programa.
    exit :
    ------
        Termina el programa.
    load <file>:
    ------
        Carga un archivo CSV o xlsx o ods.
    reload :
    --------
        Recarga el ultimo archivo.
    encoding <encoding>:
    ----------
        Establece la codificacion del texto. Por defecto utf-8.
    separator <sep> :
    -----------
        Establece el separador de los elementos de un archivo CSV.
        Por defecto ",".
    titles :
    --------
        Muestra las posiciones y los nombres de los titulos
        del archivo CSV. Asume que estan en la primera linea.
    comment <text>:
    ---------
        Pone un comentario en la lista de acciones realizadas.
    runscript <file>:
    -----------
        Ejecuta las ordenes que haya en un archivo.
    loadext <file>:
    ---------
        Importa un archivo con codigo Python para utilizarlo
        dentro del programa.
    log :
    -----
        Muestra el listado de todas las ordenes ejecutadas.
    savelog <file>:
    ---------
        Guarda en un archivo la lista de todas las ordenes ejecutadas.
    getstream :
    -----------
        Funciona igual que load, pero carga en memoria con un alias.
    loadstream :
    ------------
        Reemplaza el CSV cargado por el stream.
    concat :
    --------
        Mezcla dos streams.
    save <file>:
    ------
       Guarda lo procesado en un archivo.
    saveas <file>:
    ------
       Guarda el stream activo en un archivo excel(.xls,.xlsx,.ods).
    view :
    ------
       Muestra lo calculado.
    preview <numlines>:
    ------
       Muestra n lineas de un archivo CSV.
    distinct :
    ---------- 
        Coge las filas no repetidas.
    getcols <collist>:
    ---------
       Coge solo las columnas especificadas.
    filterbycols :
    --------------
       Filtra lo cargado por nombres de columnas y operador especificado.
    groupbycols <collist>:
    -------------
       Agrupa lo cargado por columnas.
    orderbycol <colname>:
    ------------
        Ordena lo cargado por la columna especificada.
    pivot <collist>:
    -------
        Agrupa y hace un recuento por las columnas especificadas.
    take <numrows>:
    ------
       Coge el numero de filas especificado.
    skip <numrows>:
    ------
       Ignora el numero de filas especificado.
    takewhile <condition>:
    -----------
       Coge las filas mientras cumplan una funcion de condicion.
    skipwhile <condition>:
    -----------
       Ignora filas mientras cumplan una funcion de condicion.
    select|map|all <function>:
    --------------
       Aplica la funcion pasada a todas las filas.
    where|filter <condition>:
    --------------
       Coge las filas que cumplan la condicion de la funcion que se pasa.
    groupby <condition>:
    ---------
       Agrupa las filas segun una funcion que se le pasa.
    multigroup <funlist>:
    ----------
       Agrupa las filas segun una serie de funciones que se le pasan.
    ungroup :
    ---------
       Deshace el ultimo agrupamiento.
    orderby <function>:
    ---------
       Ordena las filas segun una funcion que se le pasa.
    takegroups :
    ------------
       Coge los grupos que se especifican.
    groupsapply :
    -------------
       Aplica una funcion a los grupos especificados.
    flatmap <function>:
    ---------
       Aplica la funcion especificada a lo calculado,
       eliminando las listas interiores si las hay.
    flatfilter <condition>:
    ------------
       Selecciona las filas segun la funcion especificada, 
       eliminando las listas interiores si las hay.
"""

commands = ["select","where","orderBy","any","first","last","single","groupBy","take","skip","all","join","reverse","intersect","union","distinct","except","zip","concat","contains","count","aggregate","elementAt","sum","average","max","min","ofType","foreach","selectMany","takeWhile","skipWhile","thenBy","orderByDescending","thenByDescending","groupJoin","defaultIfEmpty","sequenceEqual","toList","toDictionary","toLookup","exit","load","clear","save"]
filter_operators = {"=":"==","!=":"!=",">":">","<":"<",">=":">=","<=":"<=","in":" in ","not_in":" not in ","starts_with":"starts_with","contains":"contains","ends_with":"ends_with","regex":"regex"}
active_encoding = "utf-8"
active_separator = ","


def queryADO(constr,query,encoding='latin-1'):
    if 'win32' in sys.platform:
        return minimal_ado.minimalQuery(constr,query,encoding)
    else:
        return []

def format(cad,lst):
    n= cad
    for i in range(len(lst)):
       p='\{' + str(i) + '\}'
       n= re.sub(re.compile(p),str(lst[i]),n)
    return n

#import chardet
def tryEncodings ( fpath, enc_list, numlines=8):
    '''
    Intenta probar la codificación para abrir un archivo.
    Hay que probar con TODO el archivo o falla.
    Con utf-16 SIEMPRE acierta aunque luego peta con readline.
    Usar cahrdet no es mejor.
    '''
    for encoding in enc_list: 
        try : 
            #print('Probando encoding: ' + encoding)
            fhandle = open(fpath,"rb")
            bytes = fhandle.read()
            bytes.decode(encoding,errors = 'strict')
            fhandle.close()
            return encoding
        except UnicodeError:
            #print('UnicodeError: ' + encoding)
            #fhandle = None
            pass
        except :
            #print('Invalid encoding: ' + encoding)
            #fhandle = None
            pass
    return ''

def getStreamFromCSV ( csvpath, encoding=active_encoding, sep=active_separator):
    csviter = CSVFileIterator(iterable= csvpath.strip(),encoding=encoding,separator=sep)
    coltitles = {}
    firstrow = csviter.next()
    cont = 0
    csvstream = Stream(iterator=csviter)
    return [csvstream,[x.strip() for x in firstrow]]

def getStreamFromFile ( csvpath, encoding=active_encoding, sep=active_separator):
    if csvpath in ['', None] : 
        csvpath = mini_tkbasic.getTkFile("Archivo csv/xlsx/odt/txt a Cargar? (xlsx/odt requieren utf-8 como encoding)","open")
        if csvpath == None : 
            return None
    ext = csvpath.split('.')[-1]
    if not ext in ['ods','xlsx','xls','csv','txt']:
        raise Exception("""assertion error: 'ext in ['ods','xlsx','xls','csv','txt']' is false""")
    if ext in  ['txt','csv']:
        print('cargando CSV')
        t = getStreamFromCSV(csvpath,encoding,sep)
        t.append(ext)
        t.append('')
        return t
    else:
        bk = pyexcel.get_book(file_name=csvpath)
        sheets = bk.get_dict()
        sheetnames = bk.sheet_names()
        print('-------------------------------------------')
        print("Hojas disponibles en el archivo: ")
        print('-------------------------------------------')
        for n,sht in enumerate(sheetnames): 
            print(f"\t{n} : {sht}")
        shnums = range(0,len(sheetnames))
        print('-------------------------------------------')
        tmp2 = input("Hoja a cargar? ")
        print('-------------------------------------------')
        sheet = None
        sheetname = ''
        if tmp2 in sheetnames : 
            sheet = sheets[tmp2]
            sheetname = tmp2
        else:
            if int(tmp2) in shnums : 
                sheet = sheets[sheetnames[int(tmp2)]]
                sheetname = sheetnames[int(tmp2)]
            else:
                raise Exception("Error: Invalid sheet name or number")
        sheetiter = ListIterator(iterable=sheet)
        cols = [x.strip() for x in sheetiter.next()]
        stream = Stream(iterator=sheetiter)
        return [stream,cols,ext,sheetname]

def getStreamFromDBQuery ( connstr, query, encoding='latin-1'):
    results = queryADO(connstr,query,encoding)
    queryiter = ListIterator(iterable=results["data"])
    return [Stream(iterator=queryiter),results["names"]]

def getSheetsNames ( ods):
    return ODSReader(ods).getSheetNames()

def callByName ( _object, fname : str, args):
    if not _object != None:
        raise Exception("""assertion error: '_object != None' is false""")
    f = getattr(_object,fname)
    return f(*args)

def lambdaFromString ( lstr):
    return eval("lambda " + lstr)

def lambdaFromColNameToGroup ( cname):
    lstr="lambda x:" + "x[" + coldict[cname] + "]"
    return eval(lstr)

def lambdaFromColNameToFilter ( cname, oper, value):
    lmb = "lambda x:"
    oper = filter_operators[oper]
    if oper == "starts_with" : 
        lmb=lmb + "x[" + coldict[cname] + "].startswith('" + value + "')"
        return eval(lmb)
    if oper == "ends_with" : 
        lmb=lmb + "x[" + coldict[cname] + "].endswith('" + value + "')"
        return eval(lmb)
    if oper == "contains" : 
        lmb=lmb + "x[" + coldict[cname] + "].find('" + value + "')!=-1"
        return eval(lmb)
    if oper == "regex" : 
        lmb= lmb + "re.match('" + value + "',x[" + coldict[cname] + "])!=None"
        return eval(lmb)
    else:
        lmb= lmb + "x[" + coldict[cname] + "]" + oper + "'" +  value + "'"
        return eval(lmb)

def lambdaFromColNames ( cnames):
    global coldict
    lstr = "lambda x:["
    last = len(cnames)-1
    i = 0
    while i < len(cnames) :
        lstr = lstr + "x[" + coldict[cnames[i]] + "]"
        if i < last : 
            lstr = lstr + ","
        i+=1
    lstr = lstr + "]"
    return eval(lstr)

def colsToDict ( coltitles):
    d = {}
    i = 0
    while i < len(coltitles) :
        d[coltitles[i]] = i
        i+=1
    return d

def toTable (seq, titles):
    t = prettytable.PrettyTable(titles)
    for item in seq: 
        if isinstance(item,list) : 
            t.add_row(item)
        elif isinstance(item,tuple):
            t.add_row(item)
        else:
            t.add_row([item])
    return t

def toHTML ( seq, titles, label):
    t = toTable(seq,titles)
    t = format(htmltemplate,[label,t])
    return t

def toHTML2 ( seq, label):
    if type(seq) == dict : 
        seq = visitDictTreeWithKeys(seq,[lambda x: x])
    t = format(htmltemplate2,[label,multiListToTable(seq)])
    return t

def multiListToTable (seq):
    tablestr = "<table border='1'>\n"
    for item in seq: 
        tablestr = tablestr + "<tr>"
        if type(item) == list : 
            tablestr = tablestr +  "<td>" + str(item[0]) + "</td>\n"
            if len(item) > 1 and type(item[1]) == list : 
                tablestr = tablestr + "<td>" + multiListToTable(item[1:]) + "</td>\n"
            else:
                tablestr = tablestr + "<td>" + str(item[1]) + "</td>\n"
        else:
            tablestr = tablestr +  "<td>" + item + "</td>\n"
        tablestr = tablestr + "</tr>"
    tablestr = tablestr + "\n</table>"
    return tablestr

def showLog ( ):
    print("")
    print("--------------------------------------------------------------------")
    print("    Listado de acciones realizadas")
    print("--------------------------------------------------------------------")
    print("")
    for item in log: 
        print(item)
    print("--------------------------------------------------------------------")
    print("Ok")


def system ( argslist): #, encoding='utf-8'):
    print(f"argslist: {argslist}")
    if not type(argslist) == list:
        raise Exception("""assertion error: 'type(argslist) == list' is false""")
    returned = ''
    try : 
        process = subprocess.run(argslist, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
        #returned = subprocess.check_output(argslist,shell=True)
        #return returned.decode(encoding)
        return output #.decode(encoding)
    except subprocess.CalledProcessError as  e:
        return (f"Error calling system: returned value '{e}'")

streams = {}
active_stream = None
charts = {}
active_chart = None
active_connstring = ""
cols = []
coldict = {}
log = []
command = ""
tmp = 0
tmp2 = 0
s = 0
last_loaded = ""
texts_list = []
print("")
print("========================================")
print("             CSV Stream v1.0            ")
print("========================================")

def runScript ( fname):
    global streams,active_stream,cols,coldict,log,tmp,s,last_loaded,active_encoding,active_separator,filter_operators,variables,texts_list
    ords = readflines(fname.strip("\n"))
    #print(ords)
    for lin in ords: 
        #print(f"running line: {lin}")
        if lin.strip() == "" or lin.strip()[0] == "#" : 
            continue
        command = lin.split(" ")[0]
        args = lin.split(" ")[1:]
        command = command.strip()
        args = "" if len(args) == 0 else " ".join(args)
        if command ==  "exit":
            log.append("Saliendo del programa.")
            sys.exit(0)
        
        elif command ==  "loadext":
            exec("import " + args.strip())
        
        elif command ==  "system":
            t = system( args.strip().split(' ')) #,'cp850')
            texts_list.append(t)
            print(t)
            log.append(format("Llamada al sistema con '{0}'",[args.strip()]))
        
        elif command ==  "text":
            if os.path.exists(args.strip()) : 
                texts_list.append(open(args.strip(),"r",encoding=active_encoding).read())
                log.append(format("Guardado texto de archivo '{0}' en lista de textos",[args.strip()]))
            else:
                texts_list.append(args.strip())
                log.append(format("Guardado texto '{0}' en lista de textos",[args.strip()]))
        
        elif command ==  "savetexts":
            t = args.strip()
            h = open(args.strip(),"w",encoding = active_encoding)
            h.write("\n".join(texts_list))
            h.close()
            log.append(format("Guardada lista de textos en '{0}'",[args.strip()]))
        elif command ==  "savetext":
            t = args.strip().split(' ')
            if not len(t) == 2:
                raise Exception("""assertion error: 'len(t) == 2' is false""")
            h = open(t[1],"w",encoding=active_encoding)
            h.write(texts_list[int(t[0])])
            h.close()
            log.append(format("Guardado texto {0} en '{1}'",[t[0],t[1]]))
        elif command ==  "deltexts":
            texts_list = []
            log.append("Borrada lista de textos guardados")
        elif command ==  "deltext":
            idx = int(args.strip())
            if idx in range(0,len(texts_list)) : 
                del texts_list[idx]
                print(format("Borrado texto {0}",[idx]))
                log.append(format("Borrado texto {0}",[idx]))
            else:
                print(format("Error borrando texto {0}. Texto inexistente",[idx]))
    
        elif command ==  "viewtext":
            idx = int(args.strip())
            if idx in range(0,len(texts_list)): 
                print('-------------------------------')
                print(format("Texto {0}",[idx]))
                print('-------------------------------')
                print(format("{0}\n",[texts_list[idx]]))
                print('-------------------------------')
            else:
                print(format("Error buscando texto {0}. Texto inexistente",[idx]))
    
        elif command ==  "viewtexts":
            print('-------------------------------')
            print('    Textos disponibles         ')
            print('-------------------------------')
            for n,txt in enumerate(texts_list): 
                print(format("Texto {0} : {1}\n",[n,txt]))
                print('-------------------------------')
            print('-------------------------------')
    
        elif command ==  "randoms":
            active_stream = None
            nels = int(args.strip())
            active_stream,cols = getStreamFromRandoms(nels)
            log.append("Creado Stream de " + nels + " numeros aleatorios")
        elif command ==  "randints":
            active_stream = None
            nels,st,_end= args.strip().split(',')
            active_stream,cols=getStreamFromRandomInts(int(nels),int(st),int(_end))
            log.append(format("Creado Stream de {0} numeros enteros aleatorios entre {1} y {2}",[nels,st,_end]))
        
        elif command ==  "runscript":
            tmp = args.strip()
            s = format("Ejecutando script {0}",[tmp])
            log.append(s)
            print(s)
            runScript(tmp)
    
        elif command ==  "comment":
            log(args.strip())
    
        elif command ==  "log":
            showLog()
    
        elif command ==  "savelog":
            f = open(args.strip(),"w",encoding = active_encoding)
            f.write("\n".join(log))
            f.close()
    
        elif command ==  "titles":
            print(toTable(coldict.items(),["Nombre","Indice"]))
            log.append("Mostrados titulos")
    
        elif command ==  "separator":
            print("Separador de texto activo:" + active_separator)
            active_separator = args.strip()
            if active_separator.strip() == "tab" : 
                active_separator = "\t"
            if active_separator.strip() == "nl" : 
                active_separator = "\n"
            if active_separator.strip() == "cr" : 
                active_separator = "\r"
            print("Separador de texto cambiado a:" + active_separator)
            log.append("Separador de texto cambiado a:" + active_separator)
    
        elif command ==  "encoding":
            print("Encoding de texto activo:" + active_encoding)
            active_encoding = args.strip()
            print("Encoding de texto cambiado a:" + active_encoding)
            log.append("Encoding de texto cambiado a:" + active_encoding)
    
        elif command ==  "load":
            active_stream = None
            tmp = args.strip()
            ext = None
            shname = None
            active_stream,cols,ext,shname=getStreamFromFile(tmp,encoding=active_encoding,sep=active_separator)
            coldict = colsToDict(cols)
            last_loaded = tmp
            if shname == '' : 
                print("Cargado archivo " + tmp)
                log.append("Cargado archivo " + tmp)
            else:
                print(format("Cargada hoja '{0}' del archivo '{1}'",[shname,tmp]))
                log.append(format("Cargada hoja '{0}' del archivo '{1}'",[shname,tmp]))
    
        elif command ==  "preview":
            lines = None
            args = args.strip()
            if args == '' : 
                tmp = mini_tkbasic.getTkFile("Archivo CSV a Previsualizar? ","open")
                lines = input('Lineas a previsualizar? ')
                encodings = input('Encodings a probar (separados por comas)? ')
                if encodings in ['',None]:
                    raise Exception("Error: Debe especificarse una lista de encodings separados por comas")
                args = tmp + ' ' + (lines if lines else '8') + ' ' +  encodings
            tmp,lines,encodings= args.split(' ')
            enc = tryEncodings(tmp,[x.strip() for x in encodings.split(',')])
            #print(f"ENC obtenido: {enc}")
            if enc != '' : 
                fhandle = open(tmp,"r",encoding=enc,errors="strict")
                linesread = []
                i = 0
                while i < int(lines) :
                    linesread.append(fhandle.readline())
                    i+=1
                for cont,line in enumerate(linesread): 
                    print(format("Linea {0} : {1}",[cont,line]))
                fhandle.close()
                print(format("Previsualizadas {0} lineas del  archivo '{1}' con encoding '{2}'",[lines,tmp,enc]))
                log.append(format("Previsualizadas {0} lineas del  archivo '{1}' con encoding '{2}'",[lines,tmp,enc]))
            else:
                print('No se pudo leer el archivo con ninguno de los encodings suministrados.')
    
        elif command ==  "getstream":
            args = args.strip().split(",")
            tmp = args[0]
            name = args[1]
            tmp2 = getStreamFromCSV(tmp,encoding=active_encoding,sep=active_separator)
            streams[name] = tmp2
            log.append(format("Cargado stream {0} en tabla de streams con alias {1}",[tmp,name]))
            print(format("Cargado stream {0} en tabla de streams con alias {1}",[tmp,name]))
    
        elif command ==  "loadstream":
            name = args.strip()
            if name.strip() in streams.keys() : 
                active_stream = None
                print(streams[name.strip()])
                active_stream,cols=streams[name.strip()]
                coldict = colsToDict(cols)
                log.append(format("Cargado stream {0} de la tabla interna como stream activo.",[name]))
                print(format("Cargado stream {0} de la tabla interna como stream activo.",[name]))
            else:
                print(format("{0} no existe en la tabla de streams",[name]))
        
        elif command ==  "concat":
            if type(active_stream) == Stream : 
                name = args.strip()
                other_stream = None
                if name.strip() in streams.keys() : 
                    other_stream = streams[name.strip() ][0]
                    active_stream = callByName(active_stream,"concat",[other_stream])
                    log.append(format("Cargado stream {0} de la tabla de streams y concatenado con stream activo.",[name]))
                    print(format("Cargado stream {0} de la tabla de streams y concatenado con stream activo.",[name]))
                else:
                    print(format("{0} no existe en la tabla interna",[name]))
            else:
                print("El resultado activo es una lista o diccionario y no se puede concatenar con un stream")
    
        elif command ==  "reload":
            if last_loaded != '' : 
                active_stream = None
                tmp = getStreamFromFile(last_loaded,sep=active_separator,encoding=active_encoding)
                active_stream,cols=tmp
                coldict = colsToDict(cols)
                log.append("Recargado archivo " + last_loaded)
    
        elif command ==  "save":
            tmp = args.strip()
            if not type(active_stream) == Stream:
                raise Exception("""assertion error: 'type(active_stream) == Stream' is false""")
            if type(active_stream) == Stream : 
                cc = active_stream.copy()
                iterToCSV(cc,tmp,first_line=cols,encoding=active_encoding,sep=active_separator)
                cc = None
                log.append("Resultados guardados en " + tmp)
    
        elif command ==  "view":
            tmp = None
            if active_stream != None : 
                tmp = args.strip()
                if type(active_stream) == Stream : 
                    cc = active_stream.copy()
                    cc.iterator.next()
                    res = cc.toList()
                    text2=""
                    text2=open("tmp.html","w")
                    text2.write(toHTML(res,cols,tmp))
                    text2.close()
                    cc = None
                else:
                    text3=""
                    text3=open("tmp.html","w")
                    text3.write(toHTML2(active_stream,tmp))
                    text3.close()
                webbrowser.open("tmp.html")
    
        elif command ==  "saveview":
            cancel = False
            if active_stream != None : 
                tmp = args.strip()
                if args == '' : 
                    tmp = mini_tkbasic.getTkFile("Guardar resultados como HTML ","save")
                    if tmp == '' : 
                        cancel = True
                    args = tmp
                if cancel == False : 
                    open(tmp,"w").close()
                    if type(active_stream) == Stream : 
                        cc = active_stream.copy()
                        cc.iterator.next()
                        res = cc.toList()
                        text4=""
                        if os.path.exists(tmp) and os.path.isfile(tmp):
                            text4=open(tmp,"w")
                            text4.write(toHTML(res,cols,tmp))
                            text4.close()
                        else:
                             raise Exception('Error: "%s" debe ser un archivo valido'%tmp)
                        cc = None
                    else:
                        text5=""
                        if os.path.exists(tmp) and os.path.isfile(tmp):
                            text5=open(tmp,"w")
                            text5.write(toHTML2(active_stream,tmp))
                            text5.close()
                        else:
                             raise Exception('Error: "%s" debe ser un archivo valido'%tmp)
                    log.append(format("Vista de resultados guardada en '{0}'",[tmp]))
    
        elif command ==  "take":
            tmp = args.strip()
            active_stream = callByName(active_stream,"take",[int(tmp)])
            s = format("Tomadas {0} filas",[int(tmp)])
            log.append(s)
            print(s)
    
        elif command ==  "skip":
            tmp = args.strip()
            active_stream = callByName(active_stream,"skip",[int(tmp)])
            s = format("Saltadas {0} filas",[int(tmp)])
            log.append(s)
    
        elif command ==  "all":
            tmp = args.strip()
            active_stream = callByName(active_stream,"all",[lambdaFromString(tmp)])
            s = format("Aplicada funcion: {0}",[tmp])
            log.append(s)
    
        elif command ==  "flatmap":
            tmp = args.strip()
            active_stream = callByName(active_stream,"flatmap",[lambdaFromString(tmp)])
            s = format("Aplicada funcion: {0}",[tmp])
            log.append(s)
    
        elif command in  ["select","map"]:
            tmp = args.strip()
            active_stream = callByName(active_stream,"map",[lambdaFromString(tmp)])
            s = format("Aplicada funcion: {0}",[tmp])
            log.append(s)
    
        elif command ==  "flatfilter":
            tmp = args.strip()
            active_stream = callByName(active_stream,"flatfilter",[lambdaFromString(tmp)])
            s = format("Aplicada funcion: {0}",[tmp])
            log.append(s)
    
        elif command in  ["filter","where"]:
            tmp = args.strip()
            active_stream = callByName(active_stream,"filter",[lambdaFromString(tmp)])
            s = format("Filtrado por funcion: {0}",[tmp])
            log.append(s)
    
        elif command in  ["takewhile","skipwhile"]:
            tmp = args.strip()
            if command == "takewhile" : 
                active_stream = callByName(active_stream,"takeWhile",[lambdaFromString(tmp)])
            else:
                active_stream = callByName(active_stream,"skipWhile",[lambdaFromString(tmp)])
            s = format("Aplicada funcion: {0}",[tmp])
            log.append(s)
    
        elif command ==  "getcols":
            tmp = args.strip()
            colnames = [x.strip() for x in tmp.split(",")]
            active_stream = callByName(active_stream,"map",[lambdaFromColNames(colnames)])
            cols = colnames
            coldict = colsToDict(cols)
            s = format("Tomadas columnas: {0}",[tmp])
            log.append(s)
    
        elif command ==  "groupby":
            tmp = args.strip()
            active_stream = callByName(active_stream,"groupBy",[lambdaFromString(tmp)])
            s = format("Agrupado por funcion: {0}",[tmp])
            log.append(s)
    
        elif command ==  "groupbycol":
            tmp = args.strip()
            active_stream = callByName(active_stream,"groupBy",[lambdaFromColNameToGroup(tmp.strip())])
            s = format("Agrupado por funcion: {0}",[tmp])
            log.append(s)
    
        elif command ==  "filterbycol":
            args = args.strip().split(",")
            tmp = args[0].strip()
            oper = args[1].strip()
            if not oper in filter_operators.keys():
                raise Exception("""assertion error: 'oper in filter_operators.keys()' is false""")
            val = args[2].strip()
            active_stream = callByName(active_stream,"filter",[lambdaFromColNameToFilter(tmp.strip(),oper,val)])
            s = format("Filtrado por columna {0}, con operador {1} y valor {2}",[tmp,oper,val])
            log.append(s)
    
        elif command ==  "orderby":
            if type(active_stream) == Stream : 
                tmp = args.strip()
                active_stream = callByName(active_stream,"orderBy",[lambdaFromString(tmp.strip())])
                active_stream = Stream(iterator=active_stream)
                log.append("Ordenado por: " + tmp)
            else:
                print("Lo calculado hasta ahora no se puede ordenar")
        
        elif command ==  "orderbycol":
            if type(active_stream) == Stream : 
                tmp = args.strip()
                active_stream = callByName(active_stream,"orderBy",[lambdaFromColNameToGroup(tmp.strip())])
                active_stream = Stream(iterator=active_stream)
                log.append("Ordenado por columna: " + tmp)
            else:
                print("Lo calculado hasta ahora no se puede ordenar")
        
        elif command ==  "multigroup":
            tmp = args.strip()
            funs = list(map(lambdaFromString,tmp.split(";")))
            active_stream = callByName(active_stream,"multiGroup",[funs])
            s = format("Agrupado por funciones: {0}",[tmp.replace(";"," y ")])
            log.append(s)
    
        elif command ==  "groupbycols":
            tmp = args.strip()
            funs = list(map(lambdaFromColNameToGroup,tmp.split(",")))
            active_stream = callByName(active_stream,"multiGroup",[funs])
            s = format("Agrupado por columnas: {0}",[tmp.replace(","," y ")])
            log.append(s)
    
        elif command ==  "pivot":
            tmp = args.strip()
            funs = list(map(lambdaFromColNameToGroup,tmp.split(",")))
            active_stream = callByName(active_stream,"multiGroup",[funs])
            active_stream = visitDictTreeWithKeys(active_stream,[len])
            s = format("Pivot por columnas: {0}",[tmp.replace(","," y ")])
            log.append(s)
        elif command ==  "ungroup":
            if type(active_stream) == dict : 
                active_stream = Stream(iterator=ListIterator(iterable=getLeaves(active_stream)))
                log.append("Desagrupado resultado actual")
            else:
                print("Lo calculado hasta ahora no se puede desagrupar")
        
        elif command ==  "takegroups":
            if type(active_stream) == dict : 
                tmp = args.strip()
                grps = [x.strip() for x in tmp.split(",")]
                dictmp = {}
                for item in grps: 
                    dictmp[tmp] = _copy(active_stream[item])
                active_stream = dictmp
                print("Cogidos grupos " + tmp)
                log.append("Cogidos grupos " + tmp)
            else:
                print("Lo calculado hasta ahora no esta agrupado y  no es aplicable takegroups")
        
        elif command ==  "groupsapply":
            if type(active_stream) == dict : 
                tmp = args.strip()
                funs = list(map(lambdaFromString,list((filter(lambda x: x != "",tmp.split(";"))))))
                mapDictTree(active_stream,funs)
                s = format("Aplicadas funciones a grupos: {0}",[tmp.replace(";"," y ")])
                log.append(s)
            else:
                print("Lo calculado hasta ahora no esta agrupado y no es aplicable groupsapply")
        
        elif command ==  "distinct":
            if type(active_stream) in [list,Stream] : 
                if type(active_stream) == list : 
                    active_stream = list(set(active_stream))
                else:
                    active_stream = Stream(iterator=callByName(active_stream,"distinct",[]))
                log.append("Cogidos elementos distintos ")
            else:
                print("El resultado actual no es un stream y no es aplicable distinct.")
        
        elif command ==  "help":
            print(help_string)
        elif command ==  "saveas":
            tmp = args.strip()
            if tmp != None : 
                file_ext = tmp.split('.')[-1].strip()
                if not file_ext in ['xls','xlsx','ods']:
                    raise Exception("""assertion error: 'file_ext in ['xls','xlsx','ods']' is false""")
                if type(active_stream) == Stream : 
                    pyexcel.save_as(array=[cols] + active_stream.toList(),dest_file_name=tmp)
                    log.append(format("Guardado stream activo en el archivo '{0}'",[tmp]))
                else:
                    print("Saveas Warning: Por ahora no tenemos forma de guardar  el resultado de manipulacion de los streams!")
        
        elif command ==  "connstring":
            if args == '' : 
                print("Cadena de conexion activa:" + active_connstring)
                active_connstring = input("Nueva cadena de conexion? >")
                print("Cadena de conexion cambiada a:" + active_connstring)
            else:
                active_connstring = args
            log.append("Cadena de conexion cambiada a:" + active_connstring)
        
        elif command ==  "querydb":
            query = args
            print('connstring: ' + active_connstring)          
            print('query: ' + query)          
            active_stream,cols=getStreamFromDBQuery(active_connstring,query,active_encoding)           
            log.append(format('Cargado stream activo desde consulta a BBDD "{0}", con connstring: "{1}" ',[active_connstring,query]))
        
        else:
            print(format("Error: {0} no es un comando valido",[command]))



if len(sys.argv) > 1 :
    print(f"running script: {sys.argv[1]}") 
    runScript(sys.argv[1])
else:
    print(help_string)
    sys.exit(0)
    #while True : 
        #command = input("Comando a ejecutar? > ")
        #command = command.strip()
        #doCommandInteractive(command)
