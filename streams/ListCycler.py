#ListIterator
from typing import *
import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class ListCycler(IteratorBase):
    '''
    ListCycler
    ----------

    Implementación de IteratorBase para iterar
    de manera cíclica una lista.
    '''

    def __init__(self : "ListCycler", iterable : List = []) -> None:
        self._iterable = iterable
        self._index : int = 0
        self._type = List
        self._closed : bool = False
        #Observers
        self._observers : List[IteratorObservers] = []


    def hasNext(self : "ListCycler") -> bool :
        return self._index < len(self._iterable) and self._closed == False


    def next(self : "ListCycler") -> Any:
        if self._closed == False:
            if self.hasNext():
                t : Any = self._iterable[self._index]
                self._index += 1

                #Notificar a los observers
                self._notifyObservers(t)

                #poner index a cero si se ha superado el maximo
                if self._index == len(self._iterable):
                    self._index = 0

                return t
            else: 
                return null
        else:
            raise Exception("Error: Call to next() when ListCycler is closed.")

    def close(self : "ListCycler") -> None:
        if self._closed == True:
            raise Exception("Error: ListCycler is closed")
        else:
            self._closed = True

    def copy(self : "ListCycler") -> "ListCycler":
        return ListCycler(iterable = self._iterable)


    #Interfaz Observer/Observable
    def addObserver(self : "ListCycler", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "ListCycler", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "ListCycler", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)