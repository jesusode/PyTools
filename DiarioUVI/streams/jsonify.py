from typing import *
import io
import re


__version__ = "1.0.0.0"


def jsonify(keys : List[Any], 
            values : List[str],
            indent : str = "    " ,
            compact : bool = False, 
            recur : bool = False,
            is_obj :  bool = False,
            find_nums_bool_null : bool = False,
            clean_whitespace : bool = False) -> str:
    '''
    Function jsonify
    ----------------

    Intenta obtener un objeto JSON a partir de una lista de claves
    y una lista de valores. Permite subobjetos dentro de values, 
    que se procesan mediante llamada recursiva. Permite compactar el 
    texto obtenido para ahorrar espacio y permite decidir si los
    valores tipo string compatibles con numeros, valores booleanos
    o null se pasen como tales al JSON generado.
    
    @retval : JSON as str
    '''

    if type(values) != list or values == None:
        return '' 

    #Sanity checks
    if keys != [] and values != None:
        assert(len(values) == len(keys))

    builder : io.StringIO = io.StringIO()
    #Extra para control de espacio cuando compact es False
    extra : str = ""
    keys_counter = 0
    if compact == False:
        extra  ='\n'
    
    #Montar el JSON
    if recur == False : builder.write("{" + extra)
    for item in values : 

        #Quitar espacio en blanco si se pide
        if clean_whitespace == True:
            item = item.strip().replace('\n','')
        
        #print(f"ITEM: {item}")

        if recur == False:
            builder.write(indent +  ('"' + keys[keys_counter] + '"' if keys!=[] else '"field' + str(keys_counter) + '"') + " : ")
        else:
            if is_obj:
                builder.write(indent + '"' + keys[keys_counter] + '"' + " : ")
        
        #Proceder segun el tipo de item
        res = re.fullmatch("[\\-|\\+]?[0-9]+|true|false|null",item.strip()) #??

        if type(item) in [int,float]:
            builder.write(str(item))
        elif type(item) == bool:
            if item == True:
                builder.write("true")
            else:
                builder.write("false")
        elif find_nums_bool_null == True and res!=None:
            builder.write(res.group(0))
        #Convertir '' en null??????
        elif type(item) == list:
            #Escribir el array con llamada recursiva
            builder.write("[")
            builder.write(jsonify(item,recur = True,compact = compact,find_nums_bool_null = find_nums_bool_null))
            builder.write("]")
        elif type(item) == dict:
            #Escribir el objeto con llamada recursiva
            builder.write("{" + (extra if not compact else ""))
            #Aumentar la indentacion para la llamada recursiva
            builder.write(jsonify(list(item.values()),list(item.keys()),recur = True,compact = compact,is_obj = True,indent = indent * 2,find_nums_bool_null = find_nums_bool_null))
            builder.write(("\n" +  indent*2+" " if not compact else ""   ) + "}")
        else:
            builder.write('"' + str(item) + '"')
        
        if keys_counter < len(values)-1:
            if not is_obj:
                builder.write(" , " + (extra if recur == False else ""))
            else:
                #builder.write((indent if not compact else "") + "," + extra)
                builder.write("," + extra)                

        else:
            builder.write(extra if recur == False else "")
        keys_counter += 1
    
    if recur == False: builder.write("}" + extra)
    
    val : str = builder.getvalue()
    builder.close()
    return val