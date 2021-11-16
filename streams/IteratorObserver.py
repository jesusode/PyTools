
#Base de IteratorObserver

from typing import *
import abc

class IteratorObserver(abc.ABC):
    '''
    IteratorObserver
    ---------------
    
    Interfaz para los observadores de Iterator.
    Deben implementar onIterNext(evt).
    '''
    @abc.abstractmethod
    def onIterNext(self : "IteratorObserver",evt : Any) -> None:
        raise NotImplementedError

