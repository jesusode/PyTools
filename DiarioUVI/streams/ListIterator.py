#ListIterator
from typing import *
import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class ListIterator(IteratorBase):
    '''
    ListIterator
    -----------

    Implementacion de IteratorBase para iterar listas.
    '''

    def __init__(self : "ListIterator", iterable : List = []) -> None:
        self._iterable = iterable
        self._index : int = 0
        self._type = List
        self._closed : bool = False
        #Observers
        self._observers : List[IteratorObservers] = []


    def hasNext(self : "ListIterator") -> bool :
        return self._index < len(self._iterable) and self._closed == False


    def next(self : "ListIterator") -> Any:
        if self._closed == False:
            if self.hasNext():
                t : Any = self._iterable[self._index]
                self._index += 1
                #Notificar a los observers
                self._notifyObservers(t)
                return t
            else: 
                return null
        else:
            raise Exception("Error: Call to next() when BridgeListIterator is closed.")

    def close(self : "ListIterator") -> None:
        if self._closed == True:
            raise Exception("Error: BridgeListIterator is closed")
        else:
            self._closed = True

    def copy(self : "ListIterator") -> "ListIterator":
        return ListIterator(iterable = self._iterable)


    #Interfaz Observer/Observable
    def addObserver(self : "ListIterator", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "ListIterator", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "ListIterator", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)