#Manejo de CSVIteratorObservers

from typing import *
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class PROAWorker(IteratorObserver):
    
    def __init__(self, fun : Callable[[str],Any]) ->NoReturn:
        self._fun = fun
    
    #Implementacion de IteratorObserver
    def onIterNext(self : "PROAWorker",evt : Any) -> NoReturn:
        raise NotImplementedError("Function PROAWorker->onIterNext is virtual and must be implemented")   




if __name__ == '__main__':
    wk = PROAWorker(lambda x : x)
    wk.onIterNext("tralari") #Excepcion
    print("Ok.")