#Clases base para observables y observers y decorador para
#convertir cualquiera otra

from typing import *

class Observer:
    '''
    Observer
    --------

    Interfaz para Observador. Debe implementar un método notify
    que acepte un parámetro de tipo Any, aunque debería ser un Dict[Any:Any].
    '''
    def __init__(self):
        #Hack para permitir cambio dinamico de otra clase
        #Si implementa un metodo notifyObservers, nos vale
        if not hasattr(self,"notify"):
            raise Exception("TypeError: Observer is an interface. Must be implemented.")
    def notify(self,event : Any) -> NoReturn:
        raise Exception("Notify is an bstract method. Must be implemented.")



class Observable:
    '''
    Observable
    ----------

    Clase base para objetos Observables. Cualquiera que herede
    de Observable adquiere este comportamiento.
    '''
    def __init__(self):
        self._observers  = []

    def hasObserver(self,observer : Any) -> bool:
        return observer in self._observers
    
    def addObserver(self,observer : Any) -> NoReturn:
        self._observers.append(observer)
    
    def removeObserver(self,observer : Any) -> NoReturn:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]
    
    def clearObservers(self) -> NoReturn:
        self._observers=[]

    def notifyObservers(self,event : Dict = {}) -> NoReturn:
        for observer in self._observers:
            observer.notify(event)


def makeObservable(klass : Type) -> Type:
    '''
    makeObservable
    --------------

    Hace que una clase que no implementa Observable sea Observable.
    Revisarlo porque puede fallar con el MRO.
    '''
    return type(klass.__name__ + "Observable",(Observable,) + klass.__bases__,{})


def makeObserver(klass : Type, callback : Callable[[Type,Any],NoReturn] = lambda Class, event: print("Evento recibido")):
    '''
    makeObserver
    --------------

    Hace que una clase que no implementa Observer sea Observer.
    Revisarlo porque puede fallar con el MRO.
    '''
    return type(klass.__name__ + "Observer",(Observer,) + klass.__bases__,{"notify" : callback})


if __name__ == '__main__':

    class XObserver(Observer):
        def __init__(self,name):
            self.name = name
        def notify(self,event):
            print("{} : Event received from X".format(self.name))
    
    class X(Observable):
        pass

    class Z:
        pass

    class ZZ(Z):
        pass

    class Y : pass

    def eventHandler(cls : Type,event :Any):
        print(cls.__class__.__name__)
        print("Evento delegado a callback!!")
        print(event)

    x = X()
    obs1 = XObserver("observer1")
    obs2 = XObserver("observer2")
    x.addObserver(obs1)
    x.notifyObservers()
    print(x.hasObserver(obs1))
    print('----------------')
    x.addObserver(obs2)
    x.notifyObservers()
    x.removeObserver(obs1)
    print(x.hasObserver(obs1))
    print(x.hasObserver(obs2))
    print('----------------')
    x.notifyObservers()
    x.clearObservers()
    print('----------------------')
    x.notifyObservers()
    print('----------------------')
    x.addObserver(obs1)
    x.notifyObservers()
    Z_Obs= makeObservable(Z)
    print(Z_Obs)
    zobs = Z_Obs()
    zobs.addObserver(obs1)
    zobs.notifyObservers()
    Y_P = makeObserver(Y,eventHandler)
    print(Y_P)
    yyy = Y_P()
    zobs.addObserver(yyy)
    zobs.notifyObservers()