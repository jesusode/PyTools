#Base de Iterator

from typing import *
import abc

class IteratorBase(abc.ABC):
    '''
    IteratorBase
    -----------

    Clase base abstracta para Iterator.
    Iterator define a un objeto que es capaz de iterar por
    los elementos de su iterable mientras existan.
    El funcionamiento de Iterator depende de dos métodos: hasNext(),
    que devuelve True si hay más elementos o False si no los hay,
    y next(), que obtiene el siguiente elemento o None si el
    Iterable no tiene más elementos.
    Admite una lista de observadores que serán notificados
    cada vez que se llame a next().

    Uso
    ----

    En bucles while:
        while instance.hasNext():
            x = instance.next()
    o con llamadas a next():
        instance.next()
    '''

    def __init__(self : "IteratorBase",iterable) -> None:
        self._iterable = iterable
        self._closed = False
        self._observers : List = []

    @abc.abstractmethod
    def next(self : "IteratorBase") -> Any:
        '''
        Devuelve el siguiente elemento de self_iterable,
        y notifica a los observers con el mismo.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def hasNext(self : "IteratorBase") -> bool:
        '''
        Devuelve True si Repeater tiene más elementos 
        o False si no.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def close(self : "IteratorBase") -> None:
        '''
        Pone self._closed a True, con lo que hasNext()
        siempre devuelve False.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self : "IteratorBase") -> Any:
        '''
        Devuelve una nueva instancia de Iterator con
        una copia de self._iterable.
        '''
        raise NotImplementedError

    #Interfaz Observer/Observable
    @abc.abstractmethod
    def addObserver(self : "IteratorBase",observer : "IteratorObserver") -> None:
        '''
        Añade observer a la lista de observables.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def removeObserver(self : "IteratorBase",observer : "IteratorObserver") -> None:
        '''
        Borra observer de la lisgta de observables.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def _notifyObservers(self : "IteratorBase") -> None:
        '''
        Notifica a todos los observables cada vez que se llama a next().
        '''
        raise NotImplementedError
