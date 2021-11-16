#Permutator

import math
from typing import *
from  streams.IteratorBase import *
from streams.IteratorObserver import *

class Permutator:
    '''
    Permutator
    ---------

    Implementación de IteratorBase para las
    permutaciones de un iterable.
    '''

    def __init__(self : "Permutator",iterable=None):
        self._iterable=iterable
        self._closed=False
        #_print("self._iterable en init:" + _tostring(self._iterable))
        if self._iterable== None : self._iterable=[] 
        assert self._n>0 and self._n < len(self._iterable)
        self._numels=0
        self._conts=[]
        self._fullconts=[]
        self._cardinality=1
        #Convertir iterable en n copias de iterable, adaptar cardinality y calcular numero de permutaciones
        #self._cardinality=len(self._iterable)*self._n
    
        #Permutaciones totales: n! / (n-r)!
        self._maxpermuts= int(math.factorial(len(self._iterable))/math.factorial(len(self._iterable)-self._n))
        #_print("Numero maximo de permutaciones: " + self._maxpermuts)
        self._permuts=0
        temp=[]
        cont=0
        while cont < self._n:
            temp.append(self._iterable)
            self._cardinality=self._cardinality*len(self._iterable)
            cont+=1
        
        #_print("self._cardinality: " + self._cardinality)
        self._iterable=temp
        #_print("self._iterable al comienzo: " + _tostring(self._iterable))
        #Inicializar contadores
        for item in self._iterable:
            self._conts.append(0)
            self._fullconts.append(len(item)-1)
        if self._cycle==None : self._cycle=False
        #Observers
        self._observers : List[IteratorObservers] = [] 
    
    def hasNext(self : "Permutator"):
        if self._numels < self._cardinality and self._permuts < self._maxpermuts : 
            return True
        else:
            return False
        
    
    def next(self : "Permutator"):
        while self.hasNext():
            actual=[]
            if self._numels==0 : #Devolver primer elemento del producto
                #actual= map |(x):x[0]| in self._iterable
                actual = [x[0] for x in self._iterable]
                self._numels+=1
                if self.isPermutation(actual) :
                    #Informar a los observers
                    self._notifyObservers(actual)
                    return actual
            else:
                #Incrementar self._conts de fin a inicio hasta fullconts
                proposed=len(self._conts)-1
                while True:
                    if self._conts[proposed]<self._fullconts[proposed] :
                        self._conts[proposed]+=1
                        break
                    else:
                        self._conts[proposed]=0
                        proposed-=1

                #Coger elemento actual del producto cartesiano
                for i in range(self._conts):
                    actual.append(self._iterable[i][self._conts[i]])
                self._numels+=1
                if self.isPermutation(actual)==True :
                    self._permuts+=1
                    #Informar a los observers
                    self._notifyObservers(actual)
                    return actual
        return None
    
    def isPermutation(self : "Permutator",lst):
        t=[]
        for item in lst:
            if item not in t :
                t.append(item)
        if len(t)==len(lst) :
            return True
        else:
            return False
                             
    def close(self : "Permutator"):
        self._closed=True
    
    def copy(self : "Permutator"):
        return Permutator(iterable=self._iterable)

    #Interfaz Observer/Observable
    def addObserver(self : "Permutator", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "Permutator", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "Permutator", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)
