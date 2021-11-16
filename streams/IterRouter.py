#IterRouter

from typing import *
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class IterRouter(IteratorBase):
    '''
    IterRouter
    ----------
    
    IterRouter permite mapear los valores producidos por una lista de iteradores que se le
    pasa en el constructor a otra lista de salida que puede tener los mismos o mas elementos. Acepta
    un mapa de llamadas, que es una lista cuyos items consisten en un entero, que indica el numero
    del valor producido por la lista de iteradores, y una lista de funciones a aplicar a dicho valor.
    Si no se especifica retval_size, la lista de salida tendra el mismo tamaño que la lista de iteradores.
    Permite tambien colapsar la lista de salida a un valor mediante una funcion de agregacion que se
    puede pasar al constructor como valor de aggregate_fun. 
    La clase consume los iterables. Si los iterables no son del mismo tamaño, se ejecuta next() hasta
    que se llegue al final del mas pequeño.
    Usos: reutilizar un mismo valor de uno o mas iterables, componer la salida de varios iterables.
    '''
    def __init__(self :"IterRouter",iterable = None,callmap = [],aggregate_fun = None,retval_size = -1) -> None:

        #check: todos son iterables
        #check: estructura de items de callmap
        self._iterlist = iterable
        self._callmap = []
        self._aggregate_fun = aggregate_fun
        self._cache = [None]*len(self._iterlist)
        self._closed=False
        self._retsize = len(self._iterlist) if retval_size==-1 else retval_size
        #Observers
        self._observers : List[IteratorObservers] = []

        #Estructura de callmap : [ [int,[funlist]],...]
        #print('calmmap:%s'%callmap);
        for item in callmap:
            assert type(item)==list and len(item)==2 and item[0] >= 0 and item[0] < len(self._iterlist) and type(item[1])==list
            #Check: items de item[1] deben ser callables
            self._callmap.append([int(item[0]),item[1]])


    def hasNext(self : "IterRouter") -> bool:
        #Solo si todos los iterables dan True en hasNext, damos True
        for iter in self._iterlist:
            if iter.hasNext() == False:
                return False
        return True


    def next(self : "IterRouter"):
        if self.hasNext()==True:
            retval = [None] * self._retsize
            assert self._retsize >= len(self._callmap)
            #Guardar en cache el resultado de next() de los iterables
            for i in range(len(self._iterlist)):
                self._cache[i]=self._iterlist[i].next()

            #print('self._cache: %s' % self._cache);
            #Aplicar el mapeo y las funciones a los valores cacheados
            cont : int = 0
            for item in self._callmap: 
                tmp : Any = self._cache[item[0]]
                for fun in item[1]:
                    tmp= fun(tmp)

                #retval[item[0]]=tmp;
                retval[cont]=tmp
                cont += 1

            #Aplicar aggregate_fun si se ha especificado
            if self._aggregate_fun!= None:
                retval = reduce(self._aggregate_fun,retval)
                self._notifyObservers(retval)
                return retval
            else:
                self._notifyObservers(retval)
                return retval
        else:
            return None


    def close(self :"IterRouter") ->None:
        if self._closed==True:
            raise Exception("Error: BridgeIterRouter is closed")
        else:  
            self._closed=True


    def copy(self :"IterRouter") -> "IterRouter":
        return IterRouter(iterable=self.iterable,callmap= self._callmap,aggregate_fun=self._aggregate_fun)


    #Interfaz Observer/Observable
    def addObserver(self : "IterRouter", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "IterRouter", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "IterRouter", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)