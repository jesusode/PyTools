from typing import *
import streams
import streams.IteratorBase
from streams.IteratorObserver import *
import pylightxl as xl
import ODSReader_tuned
import pathlib
import itertools

__version__ = "1.0.0.0"

class XLFileIterator(streams.IteratorBase.IteratorBase):

    '''
    XLFileIterator
    ---------------

    Implementa IteratorBase para archivos excel de tipo
    xlsx y ods. Esta version lee todas las hojas.
    Pendiente de arreglarlo para que pueda leer las que se indiquen.
    '''
    def __init__(self,iterable : str,sheets : List[str]=[]):

        #Abrir excel y leer las hojas especificadas o bien la primera
        #si no se especifica nada
        self._iter=None
        self._actual=None
        self._flds : List[str] = []
        p = pathlib.Path(iterable)
        #print(p.exists())
        #print(p.suffix)
        if p.suffix == ".xlsx":
            excel = xl.readxl(iterable)
            sheets : List[str] = excel.ws_names
            #self._iter = excel.ws(ws=sheets[0]).rows
            self._iter = itertools.chain(*[excel.ws(ws=sheets[x]).rows for x in range(len(sheets))])
        elif p.suffix == ".ods":
            excel = ODSReader_tuned.ODSReader(iterable)
            shrows = []
            if sheets != []:
                for sheet in sheets:
                    shrows += excel.getSheet(sheet)
            else:
                shrows = excel.getSheet(excel.getSheetNames()[0])
            self._iter = iter(shrows)
        else:
            raise Exception(f"Tipo de archivo no soportado : {iterable}")
        #Nombres de campos en primera fila(configurable)
        self._flds = self._iter.__next__()
        print(self._flds)
        #Observers
        self._observers = []
        
    def hasNext(self) -> bool:
        if self._actual == None: #Solo al iniciar
            try:
                self._actual = self._iter.__next__()
                return True
            except StopIteration:
                return False
    
    def next(self) -> str:
        values = self._actual
        #Notify observers
        self._notifyObservers(values)
        self._actual = None
        return values
    
    def close(self : "XLFileIterator") -> NoReturn:
        pass

    def copy(self : "XLFileIterator") -> Any:
        '''
        Devuelve una nueva instancia de Iterator con
        una copia de self._iterable.
        '''
        return None

    #Interfaz Observer/Observable
    def addObserver(self : "XLFileIterator", observer : IteratorObserver) -> NoReturn:
        self._observers.append(observer)

    def removeObserver(self : "XLFileIterator", observer : IteratorObserver) -> NoReturn:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "XLFileIterator", evt : Any) -> NoReturn:
        for observer in self._observers:
            observer.onIterNext(evt)


#Mini test
if __name__ == '__main__':
    class XLObserver(IteratorObserver):
        def onIterNext(self,evt):
            print(f"XLObserver: RECIBIDO EVENTO: {evt}")
    #iter = XLFileIterator("catalogo_suministros_2021.xlsx")
    #iter = XLFileIterator("catalogo_suministros_2021.ods")
    #iter = XLFileIterator("determinaciones_micro_2021.xlsx", sheets=["Hoja1","Hoja2"] )
    iter = XLFileIterator("determinaciones_micro_2021.ods", sheets=["Hoja1","Hoja2"] )
    iter.addObserver(XLObserver())
    cont =0
    while iter.hasNext():
        #if cont == 100 : break
        print(iter.next())
        cont+=1