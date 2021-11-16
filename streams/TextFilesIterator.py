#TextFilesIterator

from typing import *
import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *
import os
import os.path

class TextFilesIterator(IteratorBase):
    '''
    TextFilesIterator
    -----------------

    Implementación de IteratorBase para
    un conjunto de archivos de texto.
    Itera por cada uno línea a linea.
    '''
    def __init__(self : "TextFilesIterator",iterable=None,encoding=None,skip=0):
        self._observers = []
        self._iterable=iterable
        self._encoding=encoding
        assert self._iterable!= None
        self._pos=0
        self._last=0
        self._curfile=0
        self._skip=skip
        if self._encoding==None : self._encoding="utf-8" 
        self._closed=False
        self._fhandle=open(self._iterable[self._curfile],"r",encoding=self._encoding,errors="replace")
        if self._skip>0 :
            for i in range(self._skip):
                self._fhandle.readline()
        #Observers
        self._observers : List[IteratorObservers] = []

            
    def hasNext(self : "TextFilesIterator"):
        #print('En hasNext()')
        assert self._fhandle!=None
        #assert self._closed==False
        if self._closed==True : return False 
        #eof si file.tell es igual ahora que antes
        #Si es el ultimo archivo y el cursor esta al final, no hay mas que leer
        if self._curfile == len(self._iterable)-1 and self._pos==os.path.getsize(self._iterable[self._curfile]) :
            return False
        else:
            return True
        
    
    def next(self : "TextFilesIterator"):
        #print('En next--')
        if self.hasNext()==True :
            self._last=self._fhandle.tell()
            l= self._fhandle.readline()
            self._pos=self._fhandle.tell()
            #Si hemos llega: al fin del archivo y hay mas, poner _fhandle al siguiente
            if self._pos!=0 and self._fhandle.tell()==self._last :
                #print('Cambiando: al siguiente archivo...')
                if self._curfile < len(self._iterable)-1 :
                    self._curfile+=1
                    self._fhandle=open(self._iterable[self._curfile],"r",encoding=self._encoding,errors="replace")
                    if self._skip>0 :
                        for i in range(self._skip):
                            self._fhandle.readline()
                    self._last=self._fhandle.tell()
                    l= self._fhandle.readline()
                    self._pos=self._fhandle.tell()
                
            if self._curfile == len(self._iterable)-1 and self._pos==os.path.getsize(self._iterable[self._curfile]) :
                #print('Cerrando: el iterator pq no hay mas archivos')
                self._closed=True
            
            #notify observers if any
            self._notifyObservers(l)
            return l
        else:  
            return None
        
    

    def close(self : "TextFilesIterator"):
        if self._closed==True :
            raise "Error: BridgeTextFilesIterator is closed"
        else:  
            self._closed=True
        
    

    def copy(self : "TextFilesIterator"):
        return TextFilesIterator(iterable=self._iterable,encoding=self._encoding)
    

    #Interfaz Observer/Observable
    def addObserver(self : "TextFilesIterator", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "TextFilesIterator", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "TextFilesIterator", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)
        
    



