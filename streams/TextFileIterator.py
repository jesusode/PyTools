#TextFileIterator

from typing import *
import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *


class TextFileIterator(IteratorBase):
    '''
    TextFileIterator 
    ----------------

    Implementación de IteratorBase para
    archivos de texto. 
    Itera por las lineas de un
    archivo de texto.
    '''

    def __init__(self : "TextFileIterator",iterable=None,encoding=None) -> None:
        self._iterable=iterable
        self._encoding=encoding
        assert self._iterable!= None
        self._pos=0
        self._last=0
        if self._encoding==None: 
            self._encoding="utf-8"
        self._fhandle=open(self._iterable,"r",encoding=self._encoding,errors="replace")
        self._closed=False
        #Observers
        self._observers : List[IteratorObservers] = []
 
    def hasNext(self : "TextFileIterator") -> bool:
        assert self._fhandle!=None
        assert self._closed==False
        #eof si file.tell es igual ahora que antes
        if self._pos==0:
            return True
        if self._pos!=0 and self._fhandle.tell()!=self._last:
            return True
        else:   
            return False

    def next(self : "TextFileIterator") -> Any:
        if self.hasNext()==True:
            self._last=self._fhandle.tell()
            l= self._fhandle.readline()
            self._pos=self._fhandle.tell()
            #Notificar a los observers
            self._notifyObservers(l)
            return l
        else:
            return None

    def close(self : "TextFileIterator") -> None:
        if self._closed==True:
            raise Exception("Error: BridgeTextFileIterator is closed")
        else:  
            self._closed=True

    def copy(self : "TextFileIterator") -> "TextFileIterator":
        return TextFileIterator(iterable=self._iterable,encoding=self._encoding)
    
    #Interfaz Observer/Observable
    def addObserver(self : "TextFileIterator", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "TextFileIterator", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "TextFileIterator", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)
