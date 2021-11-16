
import io
from typing import *

#Esto deberia ser un modulo aparte de streams

def tryEncodings ( fpath: str , enc_list: List[str]) -> str:
    '''
    Intenta abrir un archivo con una serie de
    encodings que se le pasan en una lista.
    Devuelve el primero que no de un error.

    Argumentos:
    -----------
    fpath : str -- Path al archivo
    enc_list: List[str] -- Lista de encodings a probar

    Valor de retorno:
    -----------------
    str -- Primer encoding con el que abre el archivo
           sin error. 
    '''
    for encoding in enc_list: 
        try : 
            with open(fpath,"rb") as fhandle:
                bytes = fhandle.read(1024) #Vale la pena leer mas??
                bytes.decode(encoding)
            return encoding
        except :
            pass
    return ''



def previewFile(path: str,encodings: List[str],numlines: int = 5) -> List[str]:
    '''
    Obtiene una serie de lineas de un archivo
    probando a abrirlo con los encodings que se le pasan.
    Lo abre con el primero que no de un error.

    Argumentos:
    -----------
    fpath : str -- Path al archivo
    encodings: List[str] -- Lista de encodings a probar
    numlines: int -- Número de líneas a devolver. Por defecto 5.

    Valor de retorno:
    -----------------
    List[str] -- Lista de líneas leidas. 
    '''
    encoding : str = tryEncodings(path,encodings)
    if encoding != '':
        with open(path,"r",encoding =encoding) as arch:
            return arch.readlines()[:numlines]
    else:
        return ''


def readf(f: str,encoding: str ='utf-8',errors: str ='replace') -> str: 
    '''
    Lee el archivo especificado y devuelve su contenido
    como un str. Si no se especifica encoding lo abre
    usando utf-8.

    Argumentos:
    -----------
    f : str        -- Path al archivo
    encodings: str -- Encoding a usar. Por defecto utf-8
    errors: int    -- Qué hacer en caso de error.
                      Por defecto replace.

    Valor de retorno:
    -----------------
    str -- Contenido del archivo de texto. 
    '''
    #io.open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
    try:
        return io.open(f,'r',encoding=encoding,errors=errors).read()
    except:
        return ''



def readflines(f: str,encoding: str ='utf-8',errors: str ='replace') -> List[str]: 
    '''
    Lee el archivo especificado y devuelve su contenido
    como una lista de str. Si no se especifica encoding lo abre
    usando utf-8.

    Argumentos:
    -----------
    f : str        -- Path al archivo
    encodings: str -- Encoding a usar. Por defecto utf-8
    errors: int    -- Qué hacer en caso de error.
                      Por defecto replace.

    Valor de retorno:
    -----------------
    List[str] -- Lista de líneas leidas. 
    ''' 
    try:   
        return io.open(f,'r',encoding=encoding,errors=errors).readlines()
    except:
        print("Excepcion en readflines!")
        return []


def readflist(flist: List[str],encoding:str ='utf-8',errors: str='ignore') -> List[str]:
    '''
    Lee la lista de archivos especificados y devuelve
    sus contenidos como una lista de str.
    Si no se especifica encoding lo abre usando utf-8.

    Argumentos:
    -----------
    flist : List[str]  -- Lista de paths a los archivos
    encodings: str     -- Encoding a usar. Por defecto utf-8
    errors: int        -- Qué hacer en caso de error.
                          Por defecto ignore

    Valor de retorno:
    -----------------
    List[str] -- Lista de líneas leidas. 
    '''   
    texts: List[str] = []
    try:
        for item in flist:
            texts.append(readf(item,encoding,errors))
    except:
        pass
    return texts


#Escritura en archivos de texto que acepta un encoding
def writef(fl: str,_bytes: Iterable,encoding: str='utf-8',append: bool =True) -> bool:
    '''
    Escribe el contenido de _bytes en el archivo cuyo 
    path es fl. 
    Si no se especifica encoding lo codifica a utf-8.
    Si append es False, trunca el archivo. Si no,
    lo escribe al final de lo que haya.

    Argumentos:
    -----------
    fl : str            -- Path del archivo a escribir.
    _bytes : Iterable   -- Iterable con los bytes a escribir.
    encodings: str      -- Encoding a usar. Por defecto utf-8
    append: bool        -- Si es False, trunca el archivo.
                           Si es True, añade al final.
                           Por defecto True.

    Valor de retorno:
    -----------------
    bool -- true si todo Ok. Si error, False. 
    '''      
    #f=None
    try:
        #if append==True:
        #    f= io.open(fl,'w',encoding=encoding)
        #else:
        #    f= io.open(fl,'a',encoding=encoding)
        mode : str = 'a' if append else 'w'
        f :Any = io.open(fl,mode,encoding=encoding)
        b: str=str(_bytes)
        f.write(b)
        f.close()
        return True
    except:
        return False


def writeflines(fl: str,lines: List[str],encoding: str='utf-8',append: bool = True) -> bool: 
    '''
    Escribe el contenido de lines en el archivo cuyo 
    path es fl. 
    Si no se especifica encoding lo codifica a utf-8.
    Si append es False, trunca el archivo. Si no,
    lo escribe al final de lo que haya.

    Argumentos:
    -----------
    fl : str            -- Path del archivo a escribir.
    lines: List[str]    -- Lista con las lineas a escribir.
    encodings: str      -- Encoding a usar. Por defecto utf-8
    append: bool        -- Si es False, trunca el archivo.
                           Si es True, añade al final.
                           Por defecto True.

    Valor de retorno:
    -----------------
    bool -- true si todo Ok. Si error, False. 
    '''

    #f : Any =None
    #if append==0:
    #    f = io.open(fl,'w',encoding=encoding)
    #else:
    #    f = io.open(fl,'a',encoding=encoding)
    mode : str = 'a' if append else 'w'
    f :Any = io.open(fl,mode,encoding=encoding)
    for line in lines:
        f.write(line)
    f.close()
    return True


#Transcodifica un archivo a otro con otro encoding
def  transcodeFile (path : str  , encoding1 : str  , encoding2 : str  ) -> bool:
    '''
    Escribe el contenido del archivo cuyo 
    path es path en otro con distinto encoding.
    El nuevo se llamará igual que el anterior
    pero con el prefijo "_encoding2"

    Argumentos:
    -----------
    path : str          -- Path del archivo a escribir.
    encoding1: str      -- Encoding actual.
    encoding1: str      -- Nuevo encoding.


    Valor de retorno:
    -----------------
    bool -- true si todo Ok. Si error, False. 
    '''   
    enc1txt: str = open(path, "r", encoding = encoding1).read()
    f: Any = open(path + "_" + encoding2 + ".txt", "w", encoding=encoding2)
    f.write(enc1txt)
    f.close()
    return True


if __name__ == '__main__':
    transcodeFile("utf8.txt","utf-8","utf-16")
