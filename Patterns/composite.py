#Modulo patterns

from typing import *

#Composite generico

T = TypeVar('T')


class Composite:
    '''
    Patrón Composite genérico para Python.
    Composite y Leaf son iguales, solo que Leaf no
    tiene hijos  su lista esta vacia.
    '''
    def __init__(self,data : T , children : List["Composite"] = []) ->None:
        self._data  : T = data
        self._children  : List["Composite"] = children
    
 
    @property
    def leaf(self) -> bool:
        '''
        @property leaf
        '''
        return self._children == []
    
    @property
    def data(self) -> T:
        '''
        @property data
        '''
        return self._data
    
    @property
    def children(self):
        return self._children

    
    def add(self,child : "Composite")->None:
        '''
        addChild
        '''
        self._children.append(child)

    def remove(self,child : "Composite"):
        '''
        removeChild
        '''
        if child in self._children:
            del self._children[self._children.index[child]]
    
    @staticmethod
    def visit(composite : "Composite",fun : Callable[[T],Any]): #Opcion collect para recoger todo en una lista
        '''
        visit
        '''
        #Primero visitar el nodo y luego los hijos
        fun(composite.data)
        for child in composite.children:
            fun(child.data)
    
    

if __name__ == '__main__':
    cpst = Composite("my composite")
    print(cpst.leaf)
    for i in range(10):
        cpst.add(Composite(f"child: {i}"))
    Composite.visit(cpst,print)