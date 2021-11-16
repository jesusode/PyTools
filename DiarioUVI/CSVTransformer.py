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
    Clase que acepta una lista de funciones transformadoras que
    convierten una lista de strings procedente
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

def CSVRowToDict(csv : List[str], keys : List[str],*args,**kwargs) -> Dict[str,Any]:
    '''
    Convierte una lista de valores CSV en un diccionario.
    '''
    assert(len(csv) == len(keys))
    return dict(zip(keys,csv))

def CSVRowToDictWithConversions(csv : List[str], keys : List[str], *args,clean : bool = False,**kwargs) -> Dict[str, Any]:
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

def CSVRowToJSON(csv : List[str], keys : List[str],*args,**kwargs) -> str:
    '''
    Convierte una lista de valores CSV en una cadena SQL INSERT,
    y convierte lo que puede a numeros, True, False y None.
    Considerar Date.
    '''    
    return json.dumps(CSVToDictWithConversions(csv,keys,*args,**kwargs))

def CSVRowToSQL(csv : List[str], colnames : List[str], *args, tname: str = "table1",convert : bool = True,**kwargs):
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

def CSVRowToTR(csv : List[str], colnames : List[str], *args, buildTH : bool =False, **kwargs):
    '''
    Convierte una lista de valores CSV en una 
    fila de tabla HTML. WSi buildTH es True,
    se genera tambien la cadena con el <th>.
    '''
    csv = [x.strip().strip("\n") for x in csv]
    th = ""
    if buildTH == True:
        th = "</th><th>".join(colnames)
        th = f"<th>\n\t<td>{th}</td>\n</th>\n"        
    tr = "</td><td>".join(csv)
    return f"{th}\n<tr>\n\t<td>{tr}</td>\n</tr>\n"

def CSVRowToUL(csv : List[str], *args, **kwargs):
    '''
    Convierte una lista de valores CSV en una 
    UL de HTML.
    '''
    csv = [x.strip().strip("\n") for x in csv]
    tr = "\n\t".join(["<li>" + x +"</li>" for x in csv])
    return f"<ul>\n\t<{tr}\n</ul>\n"

def CSVRowToHTMLTag(csv : List[str],colnames : List[str],  tag : str,fieldAsAttribute=False, *args, **kwargs):
    '''
    Convierte una lista de valores CSV en un tag 
    HTML: <tag field = 'fname'> fvalue </tag>
    '''
    csv = [x.strip().strip("\n") for x in csv]
    colnames =  [x.strip().strip("\n") for x in colnames]
    buff = io.StringIO()
    if fieldAsAttribute == True:
        for i in range(len(colnames)):
            buff.write(f'<{tag} field="{colnames[i]}">{csv[i]}<{tag}/>\n')
    else:
        for i in range(len(colnames)):
            buff.write(f'<{tag}>{csv[i]}<{tag}/>\n')
    return buff.getvalue()

def CSVRowToXML(csv : List[str], 
                      colnames : List[str], 
                      rowname : str = "row",
                      fieldname : str = "field",
                      valuename : str = "value",
                      fieldAsAttribute : bool = False, 
                      standalone : bool = False,  
                      *args, **kwargs):
    '''
    Convierte una lista de valores CSV en XML con
    formato <row><field>fname</field><value>fvalue</value>...</row>.
    '''
    csv = [x.strip().strip("\n") for x in csv]
    colnames =  [x.strip().strip("\n") for x in colnames]
    standalone_str ='<?xml version="1.0" encoding="UTF-8"?>\n'
    buff = io.StringIO()
    if standalone == True:
        buff.write(standalone_str)
    buff.write(f"<{rowname}>\n")
    if fieldAsAttribute == True:
        for i in range(len(colnames)):
            buff.write(f'\n\t<{valuename} {fieldname} = "{fields[i]}">{csv[i]}</{valuename}>\n')
    else:
        for i in range(len(colnames)):
            buff.write(f'\n\t<{fieldname}>{colnames[i]}</{fieldname}>\n\t<{valuename}>{csv[i]}</{valuename}>\n')
    buff.write(f"</{rowname}>\n")
    return buff.getvalue()



#Mini Test
if __name__ == '__main__':
    csv = " tres tristes tigres triscaban".split()
    fields = "fld1 fld2 fld3 fld4".split()
    print(CSVRowToTR(csv,fields,buildTH = True))
    print("-------------")
    print(CSVRowToUL(csv,fields))
    print("-------------")
    print(CSVRowToXML(csv,fields,valuename="valor",fieldname="campo"))
    print("-------------")
    print(CSVRowToXML(csv,fields,fieldAsAttribute=True, standalone=True,rowname="fila"))
    print("-------------")
    print(CSVRowToHTMLTag(csv,fields,tag="div",fieldAsAttribute=True))
    print("-------------")
    print(CSVRowToHTMLTag(csv,fields,"p"))
    import os
    for item in os.environ:
        print(f"{item} -> {os.environ.get(item)}")