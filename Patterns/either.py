# implementacion de either para python

from typing import *

class Either:
    def __init__(self: object,value:Any,*types: List[type]):
        self._types: List[type]= types
        self._type: type=None
        self._value: Any =None
        if value is None:
            raise Exception("Error: value for Either must not be None")
        if type(value) not in self._types:
            raise Exception(f"Error: type of {value} must be one of {self._types}")

        self._value = value
        self._type = type(value)
    @property
    def type(self):
        return self._type
    #DEfinir un MutableEither que permita establecer value
    @property
    def value(self):
        return self._value
    @property
    def options(self):
        return self._types


class MutableEither(Either):    
    def __init__(self,value: Any,*types: List[type]):
        super().__init__(value,*types)
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self,newvalue):
        if type(newvalue) not in self._types:
            raise Exception(f"Error: type of new value must be one of {self._types}")
        self._value = newvalue
    


if __name__ == '__main__':
    iors = MutableEither(666,int,str,float)
    print(iors.type)
    print(iors.value)
    print(iors.options)
    iors.value = "xx"
    print(iors.value)
        