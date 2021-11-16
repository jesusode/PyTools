#blockParser

from typing import *
import re

#En estqa version no reconocemos los bloques """ o '''
blocks_default : Dict[str,str] = { 
    "\"":"\"",
    "'":"'",
    "(":")",
    "[":"]",
    "{":"}"
}

def blockParser(source_str : str, 
                blocks : Dict[str,str] = blocks_default,
                sep : str = " ",
                step_sep = "",
                is_file : bool = False) -> List[List[str]]:
    '''
    Funcion blockParser:
    --------------------

    Recorre un string y va metiendo en una lista las partes
    separadas por el separador sep que por defecto es el espacio.
    Acepta un dict de delimitadores de bloque.
    Cuando encuentra un delimitador de comienzo de bloque, coge todo hasta el
    fin de bloque.
    Si is_file es True, asume source_str como path a un archivo y
    procesa cada una de las lineas no vacias.
    Acepta que las lineas que comienzan por "#"
    son comentarios y las ignora.
    Si se define step_sep, parte el texto a procesar por esa expresion
    regular y procesa cada parte por separado.
    De utilidad para trocear cadenas de linea de comando o de otro tipo en
    las que se quiera respetar los bloques y separar por el separador

    Parametros
    ----------

    * source_str : str -> Cadena a trocear.
    * blocks : Dict[str,str] -> Mapa con los delimitadores de comienzo y fin de bloque.
    * sep : str -> separador de elementos de cadena. Por defecto el espacio.

    Valor de retorno
    ----------------

    * steps_list : List[List[str]] Lista de listasresultantes de procesar la cadena.

    Limitaciones
    ------------

    * No permite bloques anidados.
    * Los delimitadores de bloque estan limitados a 1 caracter.
    '''
    steps_list : List[List[str]] = []
    steps : List[str] = []
    #Si is_file es True, asumimos source_str como un archivo.
    #Cada linea se evaluara como source si no es un comentario.
    if is_file == True:
        step_sep = "\n"
        with open(source_str,"r") as f:
            source_str = step_sep.join([lin for lin in f.read().split("\n") if lin.strip()!="" and lin.strip()[0]!='#'])
    #Coger los pasos partiendo por step_sep si lo hay
    if step_sep !="":
        steps = re.split(step_sep,source_str)
    else:
        steps = [[source_str]]
    for source in steps:
        #print(f"PROCESANDO SOURCE: {source}")
        tokens : List[str] = []
        buff : List[str] = []
        aux : List[str] = []
        cont : int = 0
        block_beg :str = ""
        block_end : str = ""
        cont = 0
        while cont < len(source):
            #if cont > 500 : break
            #Si pillamos un delimitador de bloque y no estamos dentro de otro
            #establecer nuevo delimitador de bloque
            #print(f"Valor de cont en el for: {cont}")
            #print(f"procesando caracter : {source[cont]}")
            if source[cont] in blocks.keys():
                #print(f"entrando a bloque : {source[cont]}")
                block_beg = source[cont]
                block_end = blocks[block_beg]
                #Coger hasta encontrar el fin de bloque
                aux.append(source[cont])
                cont+=1
                while source[cont] != block_end and cont < len(source):
                    aux.append(source[cont])
                    cont+=1
                    #print(f"i en el while: {cont}")
                #print(f"i al salir del while: {cont}")
                #meter fin de bloque
                aux.append(source[cont])
                cont+=1
                tokens.append(''.join(aux))
                #print(f"saliendo de bloque{source[cont]} con aux: {''.join(aux)}")
                aux =[]
                #resetear delimitadores de bloque
                block_beg=""
                block_end=""
            #print(f"len(source): {len(source)}, valor de i:{cont},car: {source[cont]}")
            if cont < len(source) and source[cont] != sep:
                buff.append(source[cont])
            else:
                if buff != []:
                    tokens.append(''.join(buff))
                    buff = []
            cont+=1
        #Coger la ultima parte si la hay
        if buff != []:
            tokens.append(''.join(buff))
        steps_list.append(tokens)
    return steps_list



if __name__=='__main__':

    exstr = "-a 23 --ghj '123456 es un bloque' {23,'ww',[7,8]} paso coge esto tambien"
    print(blockParser(exstr,step_sep="paso"))
    exstr = "-a 23 --ghj '123456 es un bloque' {23,'ww',[7,8]} pasote coge esto tambien"
    print(blockParser(exstr,step_sep="\\bpaso\\b"))
    print(blockParser("blocks_test.txt",is_file=True))