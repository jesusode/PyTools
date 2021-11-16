#Tipos funcionales para Python

import sys
sys.path.append('.')

import inspect
import copy

from typing import *

from typecheckers import *

#El Objeto nulo. Mas seguro que None
class NullValue:
    '''
    Objeto nulo inmutable. Más seguro que None
    '''
    def __init__(self):
        pass
    def __setattr__(self,name,value):
        raise Exception("NullValue Error: Can't set or rebind attribute. NullValues are inmutable.")
    def __delattr__(self, *args):
        raise AttributeError("NullValue Error: attributes of NullValue object cannot be deleted")
    def __getattribute__(self, name):
        if name == 'value':
            return None
        else:
            raise Exception("NullValue Error: NullValue has only one attribute: value")
    def __repr__(self):
        return "<<NullValue class>>"


class Value:
    '''
    Value representa un valor no nulo inmutable.
    Sin control de tipo.
    '''
    def __init__(self,value):
        if value == None:
            raise Exception("Value Error: Value must be not None")
        object.__setattr__(self,"value",value)
    def __setattr__(self,name,value):
        raise Exception("Value Error: Can't set or rebind attribute.Values are inmutable.")
    def __delattr__(self, *args):
        raise AttributeError("Value Error: attributes of Value object cannot be deleted")
    def __getattribute__(self, name):
        if name == 'value':
            #Hay que usar object.__getattr__ o entra en recursion infinita
            attr=object.__getattribute__(self,name)
            #Si es una instancia de clase o list,set o dict, devolvemos una copia
            #y si es un valor, ya devuelve una copia
            if inspect.isclass(attr) or type(attr) in [list,dict,set]:
                return copy.deepcopy(attr)
            else:
                return attr
        else:
            raise Exception("Value Error: Value has only one attribute: value")
    def __repr__(self):
        return "<<Value class with value = %s>>"%self.value


class MutableValue:
    '''
    MutableValue representa un valor no nulo mutable.
    Sin control de tipo.
    '''
    def __init__(self,value):
        if value == None:
            raise Exception("MutableValue Error: Value must be not None")
        object.__setattr__(self,"value",value)
    def __setattr__(self,name,value):
        if name == "value":
            object.__setattr__(self,name,value)
        else:
            raise Exception("MutableValue Error: the only attribute in MutableValue is value.")
    def __delattr__(self, *args):
        raise AttributeError("MutableValue Error: attributes of Value object cannot be deleted")
    def __getattribute__(self, name):
        if name == 'value':
            #Hay que usar object.__getattr__ o entra en recursion infinita
            attr=object.__getattribute__(self,name)
            #Si es una instancia de clase o list,set o dict, devolvemos una copia
            #y si es un valor, ya devuelve una copia
            if inspect.isclass(attr) or type(attr) in [list,dict,set]:
                return copy.deepcopy(attr)
            else:
                return attr
        else:
            raise Exception("MutableValue Error: Value has only one attribute: value")
    def __repr__(self):
        return "<<MutableValue class with value = %s>>"%self.value


class OptionalValue:
    '''
    OptionalValue representa un valor inmutable sin un tipo
    predefinido que puede ser None.
    '''
    def __init__(self,value=None):
        object.__setattr__(self,"value",value)
    def __setattr__(self,name,value):
        raise Exception("OptionalValue Error: Can't set or rebind attribute.OptionalTypedValues are inmutable.")
    def __delattr__(self, *args):
        raise AttributeError("OptionalValue Error: attributes of OptionalTypedValue object cannot be deleted")
    def __getattribute__(self, name):
        #Hay que usar object.__getattr__ o entra en recursion infinita
        attr=object.__getattribute__(self,name)
        #Si es una instancia de clase o list,set o dict, devolvemos una copia
        #y si es un valor, ya devuelve una copia
        if inspect.isclass(attr) or type(attr) in [list,dict,set]:
            return copy.deepcopy(attr)
        else:
            return attr
    def __repr__(self):
        return "<<OptionalValue class with  value = %s>>"%self.value
    def hasValue(self):
        if object.__getattribute__(self,"value")==None:
            return False
        else:
            return True


class MutableOptionalValue(OptionalValue):
    '''
    MutableOptionalValue representa un valor mutable sin un tipo
    predefinido que puede ser None.
    '''
    def __init__(self,value=None):
        super().__init__(value)
    def __setattr__(self,name,value):
        if name != "value":
            raise Exception("MutableOptionalValue Error: MutableOptionalValue has only value attribute.")
        object.__setattr__(self,"value",value)          
    def __repr__(self):
        return "<<MutableOptionalValue class with  value = %s>>"%self.value


class TypedValue:
    '''
    TypedValue representa un valor inmutable con un tipo
    predefinido. No puede ser None.
    '''
    def __init__(self,value,typ):
        if not checkType(value,typ):
            raise Exception("TypedValue Error: expected type of value %s, found %s"%(typ,type(value)))
        object.__setattr__(self,"value",value)
        object.__setattr__(self,"type",typ)
    def __setattr__(self,name,value):
        raise Exception("TypedValue Error: Can't set or rebind attribute.TypedValues are inmutable.")
    def __delattr__(self, *args):
        raise AttributeError("TypedValue Error: attributes of TypedValue object cannot be deleted")
    def __getattribute__(self, name):
        #Hay que usar object.__getattr__ o entra en recursion infinita
        attr=object.__getattribute__(self,name)
        #Si es una instancia de clase o list,set o dict, devolvemos una copia
        #y si es un valor, ya devuelve una copia
        if inspect.isclass(attr) or type(attr) in [list,dict,set]:
            return copy.deepcopy(attr)
        else:
            return attr
    def __repr__(self):
        return "<<TypedValue class with type = %s and value = %s>>"%(self.type,self.value)


class MutableTypedValue(TypedValue):
    '''
    MutableTypedValue representa un valor mutable con un tipo
    predefinido. No puede ser None.
    '''
    def __init__(self,value,typ):
        super().__init__(value,typ)
    def __setattr__(self,name,value):
        if name == "value":
            if not checkType(value,self.type):
                raise Exception("MutableTypedValue Error: expected type of value %s, found %s"%(self.type,type(value)))
            object.__setattr__(self,name,value)
        else:
            raise Exception("MutableTypedValue Error: the only attribute modifiable in MutableTypedValue is value.")
    def __repr__(self):
        return "<<MutableTypedValue class with type = %s and value = %s>>"%(self.type,self.value)


class OptionalTypedValue:
    '''
    OptionalTypedValue representa un valor inmutable con un tipo
    predefinido que puede ser None.
    '''
    def __init__(self,typ,value=None):
        if value!=None and not checkType(value,typ):
            raise Exception("OptionalTypedValue Error: expected type of value %s or None, found %s"%(typ,type(value)))
        object.__setattr__(self,"value",value)
        object.__setattr__(self,"type",typ)
    def __setattr__(self,name,value):
        raise Exception("OptionalTypedValue Error: Can't set or rebind attribute.OptionalTypedValues are inmutable.")
    def __delattr__(self, *args):
        raise AttributeError("OptionalTypedValue Error: attributes of OptionalTypedValue object cannot be deleted")
    def __getattribute__(self, name):
        #Hay que usar object.__getattr__ o entra en recursion infinita
        attr=object.__getattribute__(self,name)
        #Si es una instancia de clase o list,set o dict, devolvemos una copia
        #y si es un valor, ya devuelve una copia
        if inspect.isclass(attr) or type(attr) in [list,dict,set]:
            return copy.deepcopy(attr)
        else:
            return attr
    def __repr__(self):
        return "<<OptionalTypedValue class with type = %s and value = %s>>"%(self.type,self.value)
    def hasValue(self):
        if object.__getattribute__(self,"value")==None:
            return False
        else:
            return True


class MutableOptionalTypedValue(OptionalTypedValue):
    '''
    MutableOptionalTypedValue representa un valor mutable con un tipo
    predefinido que puede ser None.
    '''
    def __init__(self,typ,value=None):
        super().__init__(value,typ)

    def __setattr__(self,name,value):
        if name == "value":
            if value is not None:
                if not checkType(value,self.type):
                    raise Exception("MutableTypedValue Error: expected type of value %s, found %s"%(self.type,type(value)))
                object.__setattr__(self,name,value)
        else:
            raise Exception("MutableTypedValue Error: the only attribute modifiable in MutableOptionalTypedValue is value.")

    def __repr__(self):
        return "<<MutableOptionalTypedValue class with type = %s and value = %s>>"%(self.type,self.value)


class AutoTypedValue:
    '''
    AutoTypedValue representa un valor no nulo inmutable,
    cuyo tipo es el del valor suministrado al constructor.
    '''
    def __init__(self,value):
        if value is None:
            raise Exception("AutoTypedValue Error: value must not be None")
        object.__setattr__(self,"value",value)
        object.__setattr__(self,"type",type(value))
    def __setattr__(self,name,value):
        raise Exception("AutopTypedValue Error: Can't set or rebind attribute. AutoTypedValues are inmutable.")
    def __delattr__(self, *args):
        raise AttributeError("AitoTypedValue Error: attributes of AutoTypedValue object cannot be deleted")
    def __getattribute__(self, name):
        if name in ['value','type']:
            #Hay que usar object.__getattr__ o entra en recursion infinita
            attr=object.__getattribute__(self,name)
            #Si es una instancia de clase o list,set o dict, devolvemos una copia
            #y si es un valor, ya devuelve una copia
            if inspect.isclass(attr) or type(attr) in [list,dict,set]:
                return copy.deepcopy(attr)
            else:
                return attr
        else:
            raise Exception("AutoTypedValue Error: AutoTypedValue has only value and type attributes")
    def __repr__(self):
        return "<<AutoTypedValue class with value = %s and type= %s>>"%(self.value,self.type)


class MutableAutoTypedValue(AutoTypedValue):
    '''
    MutableAutoTypedValue representa un valor no nulo mutable,
    cuyo tipo es el del valor suministrado al constructor.
    '''
    def __init__(self,value):
        super().__init__(value)
    def __setattr__(self,name,value):
        if name == "value":
            if not checkType(value,self.type):
                raise Exception("MutableAutoTypedValue Error: expected type of value %s, found %s"%(self.type,type(value)))
            object.__setattr__(self,name,value)
        else:
            raise Exception("MutableAutoTypedValue Error: the only attribute modifiable in MutableAutoTypedValue is value.")
    def __repr__(self):
        return "<<MutableAutoTypedValue class with value = %s and type= %s>>"%(self.value,self.type)


class EitherValue:
    '''
    EitherValue representa un valor inmutable que puede ser una de
    dos opciones con tipo. En cuanto se elija una de ellas,
    la otra vale None.
    '''
    def __init__(self,value,ltype,rtype):
        object.__setattr__(self,"_types",[ltype,rtype])
        object.__setattr__(self,"left",None)
        object.__setattr__(self,"right",None)
        types = object.__getattribute__(self,"_types")
        if value == None:
            raise Exception("EitherValue Error: value cannot be None")
        if type(value) not in types:
            raise Exception(f"EitherValue Error: value type must be one of {types}")
        if type(value) == types[0]:
            object.__setattr__(self,"left",value)
        else:
            object.__setattr__(self,"right",value)
    def __getattribute__(self, name):
        if name not in ["left","right","hasLeft","hasRight"]:
            raise Exception("EitherValue error: EitherValue only has left and right attributes")
        #Hay que usar object.__getattr__ o entra en recursion infinita
        attr=object.__getattribute__(self,name)
        #Si es una instancia de clase o list,set o dict, devolvemos una copia
        #y si es un valor, ya devuelve una copia
        if inspect.isclass(attr) or type(attr) in [list,dict,set]:
            return copy.deepcopy(attr)
        else:
            return attr
    def __repr__(self):
        return "<<EitherValue class with left = %s and right = %s>>"%(object.__getattribute__(self,"left"),object.__getattribute__(self,"right"))
    def hasLeft(self):
        return object.__getattribute__(self,'left') != None
    def hasRight(self):
        return not self.hasLeft()
    

class MutableEitherValue(EitherValue):
    '''
    EitherValue representa un valor inmutable que puede ser una de
    dos opciones con tipo. En cuanto se elija una de ellas,
    la otra vale None.
    '''    
    def __init__(self,value,ltype,rtype):
        super().__init__(value,ltype,rtype)
    def __setattr__(self,name,value):
        if name not in ["left","right"]:
            raise Exception("MutableEither Error: MutableEither has only left and right attributes.")
        types = object.__getattribute__(self,"_types")
        if value == None:
            raise Exception("MutableEitherValue Error: value cannot be None")
        if type(value) not in types:
            raise Exception(f"MutableEitherValue Error: value type must be one of {types}")
        if type(value) == types[0]:
            if name == 'right':
                raise Exception(f"MutableEitherValue Error: type for right must be {types[1]}")
            object.__setattr__(self,"left",value)
            object.__setattr__(self,"right",None)            
        else:
            if name == 'left':
                raise Exception(f"MutableEitherValue Error: type for left must be {types[0]}")
            object.__setattr__(self,"right",value)
            object.__setattr__(self,"left",None)
    
      
class OneOfValue:
    '''
    OneOfValue representa un valor no nulo inmutable con un tipo
    predefinido que tiene que ser uno de los que se le pasan al constructor.
    '''
    def __init__(self: object,value:Any,*types: List[type]):
        self._types: List[type]= types
        self._type: type=None
        self._value: Any =None
        if value is None:
            raise Exception("OneOfValue Error: value for OneOfValue must not be None")
        if type(value) not in self._types:
            raise Exception(f"OneOfValue Error: type of {value} must be one of {self._types}")
        self._value = value
        self._type = type(value)

    def __delattr__(self, *args):
        raise AttributeError("OneOfValue Error: attributes of OneOfValue object cannot be deleted")
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


class MutableOneOfValue(OneOfValue):
    '''
    OneOfValue representa un valor no nulo mutable con un tipo
    predefinido que tiene que ser uno de los que se le pasan al constructor.
    Al cambiar el valor se debe respetar que tenga uno de los tipos admitidos.
    '''    
    def __init__(self,value: Any,*types: List[type]):
        super().__init__(value,*types)
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self,newvalue):
        if type(newvalue) not in self._types:
            raise Exception(f"MutableOneOfValue Error: type of new value must be one of {self._types}")
        self._value = newvalue


class TypedFunction:
    '''
    TypedFunction representa una funcion con control de
    tipos tanto de los parametros como del valor de retorno.
    '''
    def __init__(self,fun,argstypes,rettype):
        object.__setattr__(self,"_fun",fun)
        if not callable(object.__getattribute__(self,"_fun")):
            raise Exception("TypedFunction Error: fun parameter in __init__ is not a function.")
        if not len(object.__getattribute__(self,"_fun").__code__.co_varnames)==len(argstypes):
            raise Exception("TypedFunction Error: fun parameter count (%s) is different form argstypes count (%s)."%(len(object.__getattribute__(self,"_fun").__code__.co_varnames),len(argstypes)))
        object.__setattr__(self,"_argstypes",argstypes)
        if not type(object.__getattribute__(self,"_argstypes"))==list:
            raise Exception("TypedFunction Error: argstypes parameter in __init__ is not a list.")
        object.__setattr__(self,"_fname",fun.__name__)
        object.__setattr__(self,"_argsnames",list(fun.__code__.co_varnames))
        object.__setattr__(self,"_rettype",rettype)
        #Cambiamos la funcion por el decorador
        object.__setattr__(self,"_fun",applySignature(
                                          object.__getattribute__(self,"_fun"),
                                          object.__getattribute__(self,"_argstypes"),
                                          object.__getattribute__(self,"_rettype")))
    def __setattr__(self,name,value):
        raise Exception("TypedFunction Error: TypedFunctions are inmutable. You cannot set an attribute.")
    def __delattr__(self, *args):
        raise AttributeError("TypedFunction Error: attributes cannot be deleted.")
    def __getattribute__(self, name):
        if name not in ['getArgsTypes','getArgsNames','getFunName','getRetType','getSignature','printSignature']:
            raise Exception(f"TypedFunction Error: You cannot get attribute {name}.")
        else:
            return object.__getattribute__(self,name)
    def __call__(self,*args):
        try:
            return object.__getattribute__(self,"_fun")(*args)
        except Exception as  err:
            print("Error calling function in TypedFunction instance: %s"%sys.exc_info()[1])
            raise
    def __repr__(self):
        fn=object.__getattribute__(self,"_fname")
        argtps=object.__getattribute__(self,"_argstypes")
        argnms=object.__getattribute__(self,"_argsnames")
        ret=object.__getattribute__(self,"_rettype")
        return "<<TypedFunction class with fun = %s, arguments = %s and rettype = %s>>"%(fn,[list(el) for el in zip(argnms,argtps)],ret)

    def getArgsTypes(self):
        return object.__getattribute__(self,"_argstypes")

    def getArgsNames(self):
        return object.__getattribute__(self,"_argsnames")

    def getFunName(self):
        return object.__getattribute__(self,"_fname")

    def getRetType(self):
        return object.__getattribute__(self,"_rettype")

    def getSignature(self):
        return [copy.deepcopy(object.__getattribute__(self,"_argstypes")),copy.deepcopy(object.__getattribute__(self,"_rettype"))]

    def printSignature(self):
        return ' -> '.join([str(x) for x in object.__getattribute__(self,"_argstypes")]) + ' -> ' + str(object.__getattribute__(self,"_rettype"))

