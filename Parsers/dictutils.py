from typing import *
import pprint
import collections

#Deberia estar en un modula aparte???????

def histogram(seq: List[Any]) -> Dict[Any,Any]:
    '''
    Crea un diccionario en el que
    se cuenta el número de veces que
    aparece cada elemento en seq (histograma).
    Cada elemento de seq debe poder ser
    la cave de un diccionario.

    Argumentos:
    -----------
    seq : List[Any]  -- Lista de partida.

    Valor de retorno:
    -----------------
    Dict[Any,Any] -- Histograma. 
    ''' 
    hist = {}
    def f(a):
        if a in hist:
            hist[a]+=1
        else:
            hist[a]=1
    list(map(f,seq))
    return hist


def filterdict(d : Dict[Any,Any],pred: Callable[[Any],bool],use_values: bool = False) -> Dict[Any,Any]:
    '''
    Crea un diccionario a partir de otro
    y un predicado que hace de filtro.
    Sólo aquellas claves que cumplan el
    predicado se pondrán en el de salida.
    El diccionario de partida no se modifica.

    Argumentos:
    -----------
    d : Dict[Any,Any]          -- Diccionario de partida.
    pred: Callable[[Any],bool] -- Predicado que acepta una clave de d.
    use_values: bool           -- Si es True se usan los valores 
                                  en vez de las claves en pred.

    Valor de retorno:
    -----------------
    Dict[Any,Any] -- Diccionario filtrado. 
    '''   
    sd={}
    for k in d.keys():
        test = k if use_values == False else d[k]
        if pred(test):
            sd[k]=d[k]
    return sd


def mapdict(d: Dict[Any,Any],fun: Callable[[Any],Any],use_keys:bool = False) -> Dict[Any,Any]:
    '''
    Crea un diccionario a partir de otro
    y una función que se aplicará a los
     valores del mismo.
    El diccionario de partida no se modifica.

    Argumentos:
    -----------
    d : Dict[Any,Any]          -- Diccionario de partida.
    fun: Callable[[Any],bool]  -- Función que acepta una clave de d.
    use_keys: bool             -- Si es True se usan las claves 
                                  en vez de los valores en pred.

    Valor de retorno:
    -----------------
    Dict[Any,Any] -- Diccionario mapeado. 
    '''   
    sd={}
    for k in d.keys():
        if use_keys == False:
            sd[k]= fun(d[k])
        else:
            sd[fun(k)] = d[k]
    return sd


def splitDictByPred(d: Dict[Any,Any],pred: Callable[[Any],bool],use_values:bool = False) -> List[Dict[Any,Any]]:
    '''
    Crea dos particiones del diccionario
    según los cumplan o no sus claves
    el predicado pred. Si use_values es True,
    se usan los valores en vez de las claves.

    Argumentos:
    -----------
    d : Dict[Any,Any]           -- Diccionario de partida.
    pred: Callable[[Any],bool]  -- Función que acepta una clave de d.
    use_values: bool            -- Si es True se usan los valores 
                                   en vez de las claves en pred.

    Valor de retorno:
    -----------------
    List[Dict[Any,Any]] -- Lista con las particiones. 
    '''   
    yes={}
    no={}
    for k in d.keys():
        test = k if use_values == False else d[k]
        if pred(k):
            yes[k]=d[k]
        else:
            no[k]=d[k]
    return [yes,no]


def splitDictByPreds(d: Dict[Any,Any],predlist: List[Callable[[Any],bool]],use_values:bool = False) -> List[Dict[Any,Any]]:
    '''
    Crea una lista de particiones del diccionario
    según los cumplan o no sus claves
    los predicados de predlist. Si use_values es True,
    se usan los valores en vez de las claves.

    Argumentos:
    -----------
    d : Dict[Any,Any]           -- Diccionario de partida.
    pred: Callable[[Any],bool]  -- Función que acepta una clave de d.
    use_values: bool            -- Si es True se usan los valores 
                                   en vez de las claves en pred.

    Valor de retorno:
    -----------------
    List[Dict[Any,Any]] -- Lista con las particiones. 
    '''  
    results=[]
    for el in predlist:
        results.append({})
    for k in d.keys():
        for i in range(len(predlist)):
            if predlist[i](k):
                results[i][k]=d[k]
    return results


def groupby(func: Callable[[Any],Any],seq: List[Any]) -> Dict[Any,Any]:
    '''
    Función de utilidad que agrupa los items
    de una lista en un diccionario según los
    valores de  una función que se aplica
    a sus elementos.

    Argumentos:
    -----------
    fun: Callable[[Any],Any]  -- Función que acepta un elemento de seq.
    seq: List[Any]            -- Lista de partida.

    Valor de retorno:
    -----------------
    Dict[Any,Any] -- Diccionario de agrupación.
    '''
    res={}
    for s in seq:
        if func(s) in res:
            res[func(s)].append(s)
        else:
            res[func(s)]=[s]
    return res


def multiGroup(seq: List[Any],flist: List[Callable[[Any],Any]]) -> Dict[Any,Any]:
    '''
    Función de utilidad que agrupa los items
    de una lista en un diccionario según los
    valores de una lista de funciónes que se aplica
    recursivamente a sus elementos. En general produce
    un diccionario cuyos elementos son a su vez diccionarios
    anidados (un DictTree).

    Argumentos:
    -----------
    funlist: List[Callable[[Any],Any]]  -- Función que acepta un
                                           elemento de seq.
    seq: List[Any]                      -- Lista de partida.

    Valor de retorno:
    -----------------
    Dict[Any,Any] -- Diccionario de agrupación.
    '''
    if len(flist)==0: return seq
    f= flist[0]
    flst=flist[1:]
    temp= groupby(f,seq)
    for item in temp:
        temp[item]= multiGroup(temp[item],flst)
    return temp


def group(seq: List[Any],flist: List[Callable[[Any],Any]],_sorted: bool = False) -> Dict[Any,Any]:
    '''
    Version de multiGroup no recursiva.
    Paralelizable en teoría.
    Si sorted es True, se ordena la lista y
    se usa un OrderedDict. seq debe ser finita.

    Argumentos:
    -----------
    seq : List[Any]  -- Lista  de partida.

    Valor de retorno:
    -----------------
    Dict[Any,Any] -- Diccionario de agrupación. 
    '''
    #Precondiciones: seq debe ser finita (una lista)
    assert(type(seq) == list)
    grouped=None

    #Usamos lista ordenada y OrderedDict si sorted es true
    if _sorted == True:
        grouped = collections.OrderedDict()
        seq = sorted(seq)
    else:
        grouped = {}

    
    for s in seq:
        tmp = grouped
        #print("tmp al comenzar el for:  %s"%tmp)
        #print('-----------------------------------------------')
        #print("Procesando %s"%s)
        for k in flist[:-1]:
            #print("processando clave: %s"%k(s))
            if k(s) in tmp:
                if  type(tmp[k(s)])!= list:
                    tmp = tmp[k(s)]
                else:
                    break
            else:
                tmp[k(s)] = {}
                tmp = tmp[k(s)]
            #print ("tmp aqui: %s"%tmp)
        #print ("tmp al terminar: %s"%tmp)
        if flist[-1](s) in tmp and type(tmp[flist[-1](s)]) == list:
            tmp[flist[-1](s)].append(s) 
        else:
            tmp[flist[-1](s)] = [s]
    return grouped


#DictTrees

#Funciones de utilidad para DictTrees.
#Un DictTree es un diccionario de diccionarios
#cuyo ultimo elemento (las hojas) es una lista
# o un objeto o valor.


#Devuelve la primera aparicion de item en md o None si no lo encuentra.
#Procede segun las claves. No se garantiza encontrar primero la de nivel mas alto.
def findItemInMultiDict(md: Dict[Any,Any],item: Any) -> Any:
    '''
    Función de utilidad que busca la primera aparición
    de un elemento en un DictTree(un diccionario de diccionarios)
    cuya clave es item y lo devuelve si lo encuentra. 
    En caso contrario devuelve None.
    No se garantiza encontrar primero la de nivel más alto.

    Argumentos:
    -----------
    md: Dict[Any,Any]    -- Función que acepta un elemento de seq.
    item: Any            -- Elemento a buscar.

    Valor de retorno:
    -----------------
    Any -- Primera aparición de item.
    '''
    resul=None
    for key in md.keys():
        if key==item:
            resul= md[item]
            break
        else:
            if type(md[key])==type({}):
                temp= findItemInMultiDict(md[key],item)
                if temp!=None:
                    resul=temp
                    break

    return resul


#Devuelve todas las apariciones de item en md o la lista vacia si no lo encuentra.
#Procede segun las claves. No se garantiza encontrar primero la de nivel mas alto.
def findAllItemInMultiDict(md: Dict[Any,Any],item: Any) ->List[Any]:
    '''
    Función de utilidad que busca todas las apariciónes
    de los elementos en un DictTree(un diccionario de diccionarios)
    cuya clave es item y los devuelve si lo encuentra.
    En caso contrario devuelve la lista vacia.
    No se garantiza encontrar primero la de nivel más alto.

    Argumentos:
    -----------
    md: Dict[Any,Any]    -- Función que acepta un elemento de seq.
    item: Any            -- Elemento a buscar.

    Valor de retorno:
    -----------------
    List[Any] -- Valores asociados a la clave item.
    '''
    resul=[]
    for key in md.keys():
        if key==item:
            temp=md[item]
            if type(temp)==type({}): #Busqueda recursiva
                resul.append(temp)
                temp= findAllItemInMultiDict(md[item],item)
                if temp!=[]:
                    for el in temp:
                        resul.append(el)
                resul.append(md[item])
        else:
            if type(md[key])==type({}):
                temp= findAllItemInMultiDict(md[key],item)
                if temp!=[]:
                    for el in temp:
                        resul.append(el)
    return resul

#Cambia todas las apariciones de item en md por value.
def changeAllItemInMultiDict(md,item,value):
    for key in md.keys():
        if key==item:
            md[item]=value
        else:
            if type(md[key])==type({}):
                changeAllItemInMultiDict(md[key],item,value)


#Borra todas las apariciones de item en md.
def deleteAllItemInMultiDict(md,item):
    for key in md.keys():
        if key==item:
            del md[item]
        else:
            if type(md[key])==type({}):
                deleteAllItemInMultiDict(md[key],item)


#Funcion para convertir a lista
#un diccionario de diccionarios
#(lo que sale de un multiGroup)

def multiDictToList(md,fun=None):
    resul=[]
    for item in md.keys():
        if type(md[item])!=type({}):
            if fun==None:
                resul.append(md[item])
            else:
                resul.append(map (fun,md[item]))
        else:
            resul.append(multiDictToList(md[item]))
    return resul



#Funcion para aplicar una lista de funciones a
#un diccionario de diccionarios
#(lo que sale de un multiGroup)

def mapDictTree(dt,funlist):
    for item in dt.keys():
        if type(dt[item])==type([]):
            temp=dt[item]
            for fun in funlist:
                temp=fun(temp)
            dt[item]=temp
        else:
            mapDictTree(dt[item],funlist)


#Funcion para visitar
#un diccionario de diccionarios
#(lo que sale de un multiGroup)

def visitDictTree(dt,funlist,collected):
    #Error conocido: con |?collected=[], python 36 recicla la lista y lo que contuviera!!!
    for item in dt.keys():
        if type(dt[item])==type([]):
            temp=dt[item]
            for fun in funlist:
                temp=fun(temp)
            collected.append([item,temp])
        else:
            visitDictTree(dt[item],funlist,collected)
    return collected


def visitDictTreeWithKeys(dt,funlist,actual_key=None):
    collected=[]
    if actual_key!=None:
        collected.append(actual_key)
    for item in dt.keys():
        if type(dt[item])==type([]):
            temp=dt[item]
            for fun in funlist:
                temp=fun(temp)
            collected.append([item,temp])
        else:
            collected.append(visitDictTreeWithKeys(dt[item],funlist,item))
    return collected

#Utilidad para recuento: pivot
def pivot(dt,flist):
    return visitDictTreeWithKeys(group(dt,flist),[len])


#Funcion para visitar
#un diccionario de diccionarios
#(lo que sale de un multiGroup) y filtrar los resultados

def filterDictTree(dt,fun,collected):
    #Error conocido: con collected=[], python 36 recicla la lista y lo que contuviera!!!
    for item in dt.keys():
        if type(dt[item])==type([]):
            temp=dt[item]
            for elem in temp:
                if fun(elem)==True:
                    collected.append([item,elem])
        else:
            filterDictTree(dt[item],fun,collected)
    return collected

def filterDictTreeWithKeys(dt,fun,actual_key=None):
    collected=[]
    if actual_key!=None:
        collected.append(actual_key)
    for item in dt.keys():
        if type(dt[item])==type([]):
            temp=dt[item]
            for elem in temp:
                if fun(elem)==True:
                    collected.append([item,elem])
        else:
            collected.append(filterDictTreeWithKeys(dt[item],fun,item))
    return collected


#Funcion para obtener un subnivel de 
#un diccionario de diccionarios
#(lo que sale de un multiGroup)

def getDictTreeLevel(dt,level,collected,cont=0):
    for item in dt.keys():
        if cont==level:
            collected.append(dt[item])
        else:
            if type(dt[item])==type({}):
                getDictTreeLevel(dt[item],level,collected,cont+1)
    return collected


#Funcion para obtener la lista final del dicttree (las hojas)

def getLeaves(dtree,collected):
    for item in dtree.keys():
        if type(dtree[item])==list:
            for elem in dtree[item]:
                collected.append(elem)
        else:
            getLeaves(dtree[item],collected)
    return collected


#Funcion para obtener los elementos de un path 
#del dicttree

def getDictTreePath(dtree,elems):
    temp=dtree
    for item in elems:
        if type(temp)!=type({}):
            return {}
        if item not in temp.keys():
            return {}
        else:
            temp=temp[item]
    return temp