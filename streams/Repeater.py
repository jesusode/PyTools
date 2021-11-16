#Clases soporte para lazy streams

from typing import *
import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class Repeater(IteratorBase):
    '''
    Repeater
    --------

    Implementación de IteratorBase que devuelve siempre el mismo valor.
    Si maxreps es mayor que cero, solo devuelve hasta maxreps.
    '''


    def __init__(self : "Repeater",iterable = None,maxreps : int = 0) -> None:
        IteratorBase.__init__(self,iterable)
        #Precondicion: maxreps debe ser >=0
        assert(maxreps >=0)
        #--------------------------------
        self.maxreps : int = maxreps
        self._reps : int = 0
        #Observers
        self._observers : List[IteratorObservers] = []

    def next(self : "Repeater") -> Any:
        if self.hasNext() :
            self._reps+=1
            #Notificar a los observers
            self._notifyObservers(self._iterable)
            return self._iterable
        else:
            return None

    def hasNext(self : "Repeater") -> None:
        if self._closed==False : 
            if self.maxreps==0 :
                return True
            else:
                if  self._reps< self.maxreps :
                    return True
                else:
                    return False
        else:
            return False

    def close(self : "Repeater") -> None:
        self._closed=True

    def copy(self) -> "Repeater":
        return Repeater(iterable=self.iterable)

    #Interfaz Observer/Observable
    def addObserver(self : "Repeater", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "Repeater", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "Repeater", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)
    