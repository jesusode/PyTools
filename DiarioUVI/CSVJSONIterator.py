from typing import *
import streams
import streams.CSVFileIterator
from  streams.IteratorBase import *
from streams.IteratorObserver import *

import jsonify

__version__ = "1.0.0.0"

class CSVJSONIterator(streams.CSVFileIterator.CSVFileIterator):

    '''
    CSVJSONIterator
    ---------------
    
    Extiende CSVFileIterator y en next()
    devuelve un objeto JSON.
    Configurable encoding,separator,limpiar espacio en blanco,
    compactar y interpretar strings como numeros, bool o null
    '''
    def __init__(self,iterable = None, encoding : str = None, separator : str =",",
                 jsonconv : Callable[[str],str] = jsonify.jsonify,
                 fnames : List[str] = [],
                 findNumsBoolNull : bool = False, cleanWhitespace : bool = False,
                 compact : bool = False):
        super().__init__(iterable,encoding,separator)
        self._converter = jsonconv
        self._findNumsBoolNull = findNumsBoolNull
        self._cleanWhitespace = cleanWhitespace
        self._compact = compact
        self._fnames = fnames
        #Obtener los nombres de los campos asumiendo que es la primea linea si no se han definido
        if self._fnames == []:
            self._fnames = [x.strip().replace('\n','') for x in super().next()]

        #Observers
        self._observers = []
        
    def hasNext(self) -> bool:
        return super().hasNext()
    
    def next(self) -> str:
        if self.hasNext():
            values = super().next()
            #print(f"Values: {values}")
            json = self._converter(self._fnames,values,
                                   find_nums_bool_null = self._findNumsBoolNull,
                                   compact = self._compact,
                                   clean_whitespace = self._cleanWhitespace)
            #Notify observers
            self._notifyObservers(json)
            return json
    
    def close(self) -> NoReturn:
        super().close()

    #Interfaz Observer/Observable
    def addObserver(self : "CSVJSONIterator", observer : IteratorObserver) -> NoReturn:
        self._observers.append(observer)

    def removeObserver(self : "CSVJSONIterator", observer : IteratorObserver) -> NoReturn:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "CSVJSONIterator", evt : Any) -> NoReturn:
        for observer in self._observers:
            observer.onIterNext(evt)