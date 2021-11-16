#BinaryFileIterator

from typing import *
#from streams.IteratorBase import *
#from streams.IteratorObserver import *
from IteratorBase import *
from IteratorObserver import *
from binary_dumper import *
import os.path


class BinaryFileIterator(IteratorBase):
    '''
    BinaryFileIterator 
    ----------------

    Implementación de IteratorBase para
    archivos binarios leidos como estructuras. 
    '''

    def __init__(self : "BinaryFileIterator",iterable,_struct) -> None:
        self._iterable=iterable
        assert self._iterable!= None
        self._struct = Struct(_struct)
        self._size = calcsize(_struct)
        self._fsize = os.path.getsize(self._iterable)
        self._pos=0
        self._last=0
        self._fhandle=open(self._iterable,"rb")
        self._closed=False
        #Observers
        self._observers : List[IteratorObservers] = []
 
    def hasNext(self : "BinaryFileIterator") -> bool:
        assert self._fhandle!=None
        assert self._closed==False
        #eof si file.tell es igual ahora que antes
        print(f"self.pos: {self._pos} , self._last:{self._last} ,  self.fhandle.tell():{self._fhandle.tell()}")
        if self._pos==0:
            return True
        elif self._pos == self._fsize:
            return False
        elif self._pos!=0 and self._fhandle.tell()!=self._last:
            return True
        else:   
            return False

    def next(self : "BinaryFileIterator") -> Any:
        if self.hasNext()==True:
            self._last=self._fhandle.tell()
            _read = self._fhandle.read(self._size)
            self._pos=self._fhandle.tell()
            l = None
            if _read != b"":
                l= self._struct.unpack(_read)
            else:
                self._last = self._pos
            #Notificar a los observers
            self._notifyObservers(l)
            return l
        else:
            return None

    def close(self : "BinaryFileIterator") -> None:
        if self._closed==True:
            raise Exception("Error: BinaryFileIterator is closed")
        else:  
            self._closed=True

    def copy(self : "BinaryFileIterator") -> "BinaryFileIterator":
        return BinaryFileIterator(iterable=self._iterable,encoding=self._encoding)
    
    #Interfaz Observer/Observable
    def addObserver(self : "BinaryFileIterator", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "BinaryFileIterator", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "BinaryFileIterator", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)



if __name__ == '__main__':
    bi = BinaryFileIterator("struct_file.bin","6sll")
    while bi.hasNext():
        print(bi.next())
    print("Ok")