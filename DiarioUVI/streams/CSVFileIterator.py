#CSVFileIterator

from typing import *
#import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class CSVFileIterator(IteratorBase):
    '''
    CSVFileIterator
    ---------------

    Implementación ded IteratorBase para
    iterar arcchivos CSV.
    Itera por líneas.
    '''

    def __init__(self : "CSVFileIterator",iterable=None,encoding=None,separator=","):
        self._iterable=iterable
        self._encoding=encoding
        self._separator=separator
        assert self._iterable!= None
        self._pos=0
        self._last=0
        if self._encoding==None : self._encoding="utf-8" 
        #_print("self._encoding: "  + self._encoding)
        self._fhandle= open(self._iterable,"r",encoding=self._encoding,errors="replace")
        self._separator= separator
        #self._separator=_strip(self._separator)
        self._closed=False
        #Observers
        self._observers : List[IteratorObservers] = []
    

    def getSeparator(self : "CSVFileIterator"):
        return self._separator
    

    def setSeparator(self : "CSVFileIterator",value : str):
        self._separator=value
    

    def hasNext(self : "CSVFileIterator"):
        assert self._fhandle!=None
        assert self._closed==False
        #eof si file.tell es igual ahora que antes
        if self._pos==0 : return True 
        if self._pos!=0 and self._fhandle.tell()!=self._last :
            return True
        else:   
            return False
        

    def next(self : "CSVFileIterator"):
        if self.hasNext()==True :
            self._last=self._fhandle.tell()
            l= self._fhandle.readline()
            #print('LEIDO POR CSV: ' + l)
            self._pos=self._fhandle.tell()
            if l in ["","\n"," "] : return None 
            #_print("self.sparator: " + repr(self._separator))
            #print("A DEVOLVER POR CSVITERATOR: " + _tostring(_split(l,self._separator)))
            #notify observers if any
            flds = l.split(self._separator)
            self._notifyObservers(flds)
            return flds
        else:  
            #print("DEVOLVEMOS None")
            return None

    def close(self):
        if self._closed==True :
            raise "Error: BridgeCSVFileIterator is closed"
        else:  
            self._closed=True
        
    def copy(self : "CSVtFileIterator"):
        return CSVFileIterator(iterable=self._iterable,encoding=self._encoding,separator=self._separator)
    

    #Interfaz Observer/Observable
    def addObserver(self : "CSVFileIterator", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "CSVFileIterator", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "CSVFileIterator", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)
