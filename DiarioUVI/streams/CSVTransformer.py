from typing import *
import sqlite3

import io
import re
import json


__version__ = "1.0.0.0"


class CSVTransformer:
    '''
    CSVConverter 
    ------------
    Implementa IteratorObserver.
    Clase que acepta una función transformadora que
    convierte una lista de strings procedente
    de un archivo CSV en cualquier otra cosa.
    '''
    def __init__(self : "CSVTransformer", transformers : List[Callable[[List[str]],Any]] = None) -> NoReturn:
        self._transformers = transformers
    

    def transform(self  : "CSVTransformer", csv : List[str], *args,**kwargs) -> List[Any]:
        transformed = []
        if self._transformers != None :
            for transformer in self._transformers:
                transformed.append(transformer(csv, *args,**kwargs))
        return transformed



#Funciones de utilidad para diversas transformaciones

def CSVToDict(csv : List[str], keys : List[str],*args,**kwargs) -> Dict[str,Any]:
    '''
    Convierte una lista de valores CSV en un diccionario.
    '''
    assert(len(csv) == len(keys))
    return dict(zip(keys,csv))

def CSVToDictWithConversions(csv : List[str], keys : List[str], *args,clean : bool = False,**kwargs) -> Dict[str, Any]:
    '''
    Convierte una lista de valores CSV en un diccionario,
    y convierte lo que puede a numeros, True, False y None.
    Considerar Date.
    '''
    assert(len(csv) == len(keys))
    csv2 = []
    if clean == True:
        keys = [x.strip().strip('\n') for x in keys]
        #print(f"keys ahora: {keys}")
    for item in csv:
        if clean == True:
            item = item.strip().strip('\n')
        #Proceder segun el tipo de item
        #print(f"Item: {item.strip()}")
        res = re.fullmatch("[\\-|\\+]?[0-9]+(\\.[0-9]+)?",item.strip().strip("\n"))
        if item in ["","null"]:
            csv2.append(None)
        elif res!=None:
            nm = res.group(0)
            csv2.append(float(nm) if '.' in nm else int(nm))
        elif item in ["True","true"]:
            csv2.append(True)
        elif item in ["False","false"]:
            csv2.append(False)
        else:
            csv2.append(item)
    #print(f"csv2: {csv2}")
    return dict(zip(keys,csv2))

def CSVToJSON(csv : List[str], keys : List[str],*args,**kwargs) -> str:
    '''
    Convierte una lista de valores CSV en una cadena SQL INSERT,
    y convierte lo que puede a numeros, True, False y None.
    Considerar Date.
    '''    
    return json.dumps(CSVToDictWithConversions(csv,keys,*args,**kwargs))

def CSVToSQL(csv : List[str], colnames : List[str], *args, tname: str = "table1",convert : bool = True,**kwargs):
    '''
    Convierte una lista de valores CSV en una cadena SQL INSERT,
    y convierte lo que puede a numeros y NULL.
    Considerar Date.
    '''
    assert(len(csv) == len(colnames))
    csv = [x.strip().strip("\n") for x in csv]
    colnames =  [x.strip().strip("\n") for x in colnames]
    buffer = io.StringIO()
    buffer.write("INSERT INTO ")
    buffer.write(tname)
    buffer.write("(")
    buffer.write(",".join(colnames))
    buffer.write(") VALUES (")
    for i in range(len(csv)):
        if convert == True and re.fullmatch("[\\-|\\+]?[0-9]+(\\.[0-9]+)?|NULL",csv[i]):
            buffer.write(csv[i])
        else:
            buffer.write("'")
            buffer.write(csv[i])
            buffer.write("'")
        if i < len(csv) -1:
            buffer.write(",")
    buffer.write(");\n")

    return buffer.getvalue()

