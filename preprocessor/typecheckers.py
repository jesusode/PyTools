#Soporte para control de tipos------------------------------------------------------------

from typing import *
import inspect
import copy



#Esta version puede comprobar si es un subtipo del tipo a comprobar
def ensureType ( obj : object, typ : Type ,strict : bool =False,cond_fun : Callable[[object],bool]=None) -> None:
    '''
    Comprueba que el tipo de obj sea typ o lanza una excepcion. Si strict
    es False, acepta que obj sea una subclase de typ, si es True no.
    Acepta una función de restricción de tipos, que acepta obj y devuelve un bool,
    que permite un ajuste fino  de la coincidencia. Si el tipo de obj es any, 
    nunca lanza la excepción.
    '''
    if type(obj)==any or typ==any: return True
    if type(obj) != typ :
        if strict==False:
            if inspect.isclass(obj) and isinstance(obj,typ):
                return True
            else:
                raise Exception("Type Error in ensureType: Expected type %s in parameter %s. Found type %s" %(typ,obj,_type(obj)))
        else:
            raise Exception("Type Error in ensureType with option strict: Expected type %s in parameter %s. Found type %s" %(typ,obj,_type(obj)))
    else:
        #Cambio para aplicar una funcion de restriccion al valor
        if cond_fun!=None:
            if cond_fun(obj)!=True:
                raise Exception('Error in ensureType: Expected True from the conditional function for %s and find False'% obj)
            else:
                return True
        else:
            return True


def checkType ( obj : object, typ : Type,strict : bool =False,cond_fun : Callable[[object],bool]=None) -> bool:
    '''
    Comprueba que el tipo de obj sea typ y devuelve True o False si falla. 
    Si strict es False, acepta que obj sea una subclase de typ, si es True no.
    Acepta una función de restricción de tipos, que acepta obj y devuelve un bool,
    que permite un ajuste fino  de la coincidencia. Si el tipo de obj es any, 
    siempre devuelve True.
    '''
    if type(obj)==any or typ==any: return True
    if type(obj) != typ :
        if strict==False:
            #print("obj:%s"%obj)
            #print("typ:%s:%s"%(typ,inspect.isclass(typ)))
            if inspect.isclass(obj) and isinstance(obj,typ):
                return True
            else:
                return False
        else:
            return False
    else:
        #Cambio para aplicar una funcion de restriccion al valor
        if cond_fun!=None:
            if cond_fun(obj)!=True:
                return False
            else:
                return True
        else:
            return True


def ensureTypeInUnion ( obj : object, typelist : List[Type],strict : bool =False,cond_fun : Callable[[object],bool]=None) -> None:
    if type(obj)==any or any in typelist: return True
    if type(obj) not in typelist :
        if strict==False:
            for typ in typelist:
                if isinstance(obj,typ):
                    return True
            raise Exception("Type Error in ensureTypeInUnion: Expected types %s in parameter %s. Found type %s" %(' or '.join([str(x) for x in typelist]),str(obj),type(obj)))
        else:
            raise Exception("Type Error in ensureTypeInUnion with option strict: Expected types %s in parameter %s. Found type %s" %(' or '.join([str(x) for x in typelist]),str(obj),type(obj)))
    else:
        #Cambio para aplicar una funcion de restriccion al valor
        if cond_fun!=None:
            if cond_fun(obj)!=True:
                raise Exception('Error in ensureType: Expected True from the conditional function for %s and find False'% obj)
            else:
                return True
        #return True


def checkTypeInUnion ( obj : object, typelist : List[Type],strict : bool=False,cond_fun : Callable[[object],bool]=None) -> bool:
    if type(obj)==any or any in typelist: return True
    if type(obj) not in typelist :
        if strict==False:
            for typ in typelist:
                if isinstance(obj,typ):
                    return True
            return False
        else:
            return False
    else:
        #Cambio para aplicar una funcion de restriccion al valor
        if cond_fun!=None:
            if cond_fun(obj)!=True:
                return False
            else:
                return True
        #return True


#--------------------Decoradores para control de tipos de funciones-------------------------

#Decorador @paramsTypes
def paramsTypes ( typelist):
    def function1(f) :
        def function0(*args) :
            if not len(args) == len(typelist):
                raise Exception("""assertion error in paramsTypes: 'len(args) == len(typelist)' is false""")
            i = 0
            while i < len(args) :
                #print("typelist[i]: %s"%typelist[i])
                if typelist[i]!=any and type(args[i]) != typelist[i] : 
                    raise Exception("Type Error. Expected type %s in function %s, parameter %s:(%s).Found type %s" % (typelist[i],f.__name__,i,args[i],_type(args[i])))
                i+=1
            return f(*args)
        wrapper = function0
        return wrapper
    decorator = function1
    return decorator

#Decorador  @returnType      
def returnType ( typ):
     def function3(f) :
          def function2(*args) :
               result = f(*args)
               if type(result) != typ: 
                    raise Exception("Type Error in returnType: Expected return type %s in function %s. Found type %s" % (typ,f.__name__,_type(result)))
               return result
          wrapper = function2
          return wrapper
     decorator = function3
     return decorator

#Decorador @funSignature
def funSignature ( typelist, returntype):
    def function5(f) :
        def function4(*args) :
            if not len(args) == len(typelist):
              raise Exception("""assertion error in funPrototype: 'len(args) == len(typelist)' is false""")
            i = 0
            while i < len(args) :
                if typelist[i]!= any and type(args[i]) != typelist[i] : 
                    raise Exception("Type Error in funPrototype. Expected type %s in function %s, parameter %s:(%s).Found type %s" % (typelist[i],f.__name__,i,args[i],_type(args[i])))
                i+=1
            result = f(*args)
            if returntype!= any and type(result) != returntype : 
                raise Exception("Type Error in funPrototype: Expected return type %s in function %s. Found type %s" % (returntype,f.__name__,_type(result)))
            return result
        wrapper = function4
        return wrapper
    decorator = function5
    return decorator


def applySignature(fun,argstypes,rettype):
    _decorator=funSignature(argstypes,rettype)
    return _decorator(fun)

#-------------------------------------------------------------------------------------------







#Clase comodin para tipos----------------------
class any(object):pass
#----------------------------------------------

#Definimos unit como el tipo de None-----------
nulltype=type(None)
#----------------------------------------------

class TypedValue:
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
        return "<<Bridge TypedValue class with type = %s and value = %s>>"%(self.type,self.value)


class OptionalTypedValue:
    def __init__(self,typ,value=None):
        if value!=None and not checkType(value,typ):
            raise Exception("OptionalTypedValue Error: expected type of value %s or null, found %s"%(typ,type(value)))
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
        return "<<Bridge OptionalTypedValue class with type = %s and value = %s>>"%(self.type,self.value)
    def hasValue(self):
        if object.__getattribute__(self,"value")==None:
            return False
        else:
            return True


class TypedFunction:
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
        object.__setattr__(self,"_fun",_applySignature(
                                          object.__getattribute__(self,"_fun"),
                                          object.__getattribute__(self,"_argstypes"),
                                          object.__getattribute__(self,"_rettype")))
    def __setattr__(self,name,value):
        raise Exception("TypedFunction Error: TypedFunctions are inmutable. You cannot set an attribute.")
    def __delattr__(self, *args):
        raise AttributeError("TypedFunction Error: attributes cannot be deleted.")
    def __getattribute__(self, name):
        if name not in ['getArgsTypes','getArgsNames','getFunName','getRetType','getSignature','printSignature']:
            raise Exception("TypedFunction Error: You cannot get an attribute.")
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
        return "<<Bridge TypedFunction class with fun = %s, arguments = %s and rettype = %s>>"%(fn,[list(el) for el in zip(argnms,argtps)],ret)

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


#Clases para construir comprobadores de tipos(composite de TypeCheckers)
class TypeChecker(object):
    def __init__ ( self, typl):
      self.typ = typl[0]
    def checkType ( self, x):
      return True if type(x) == self.typ else False


class ClassTypeChecker(object):
    def __init__ ( self, typl):
      self.typ = typl[0]
    def checkType ( self, x):
      return checkType(x,typl)

#FunctionTypeChecker devuelve True si lo que se le pasa es una funcion
#Y tiene el mismo numero de argumentos, con los mismos nombres
#y en el mismo orden
#Python no tiene tipos usables, no se puede comprobar la firma a no ser que se envuelva en un 
#decorador applySignature
class FunctionTypeChecker(TypeChecker):
    def __init__ ( self, typl):
        #Se le debe pasar [argnames]
        assert(type(typl)==list)
        self.typ=tuple(typl)
    def checkType ( self, x):
        #print(x.__code__.co_varnames)
        return True if callable(x) and x.__code__.co_varnames==self.typ else False


class TypedFunctionChecker(TypeChecker):
    def __init__ ( self, typl):
        #Se le debe pasar [argstypes_list,rettype]
        assert(type(typl)==list)
        assert(type(typl[0])==list)
        self.typ=typl
    def checkType ( self, x):
        return True if type(x)==TypedFunction and x.getSignature()==self.typ else False
      
      
class OneTypeOf(TypeChecker):
    def __init__ ( self, typ):
      if not type(typ) == list:
        raise Exception("""assertion error: 'type(typ) == list' is false""")
      self.typ = typ
      for item in self.typ: 
           if not isinstance(item,TypeChecker):
            raise Exception("""assertion error: 'isinstance(item,TypeChecker)' is false""")
    def checkType ( self, x):
      for item in self.typ: 
           t = item.checkType(x)
           if t == True : 
                return True
      return False
      
      
class ListOfType(TypeChecker):
   def __init__ ( self, typl):
        self.typ = typl[0]
   def checkType ( self, x):
        if not type(x) == list:
          raise Exception("""assertion error: 'type(x) == list' is false""")
        for item in x: 
           t = self.typ.checkType(item)
           if t == False : 
                return False
        return True


class TupleOfType(TypeChecker):
 def __init__ ( self, typl):
      self.typ = typ[0]
 def checkType ( self, x):
      if not type(x) == tuple:
        raise Exception("""assertion error: 'type(x) == tuple' is false""")
      for item in x: 
           t = self.typ.checkType(item)
           if t == False : 
                return False
      return True

class SetOfType(TypeChecker):
 def __init__ ( self, typl):
      self.typ = typl[0]
 def checkType ( self, x):
      if not type(x) == tuple:
        raise Exception("""assertion error: 'type(x) == set' is false""")
      for item in x: 
           t = self.typ.checkType(item)
           if t == False : 
                return False
      return True
      

class DictOfTypes(TypeChecker):
 def __init__ ( self, typl):
      self.typ,self.typ2=typl
 def checkType ( self, x):
      if not type(x) == dict:
       raise Exception("""assertion error: 'type(x) == dict' is false""")
      for item in x: 
           t = self.typ.checkType(item)
           if t == False : 
                return False
           t = self.typ2.checkType(x[item])
           if t == False : 
                return False
      return True
      
      
class ListOfTypes(TypeChecker):
 def __init__ ( self, typ):
      if not type(typ) == list:
        raise Exception("""assertion error: 'type(typ) == list' is false""")
      self.typ = typ
 def checkType ( self, x):
      if not type(x) == list:
        raise Exception("""assertion error: 'type(x) == list' is false""")
      if len(x) != len(self.typ) : 
           return False
      i = 0
      while i < len(x) :
           t = self.typ[i].checkType(x[i])
           if t == False : 
                return False
           i+=1
      return True

class SetOfTypes(TypeChecker):
 def __init__ ( self, typ):
      if not type(typ) == set:
        raise Exception("""assertion error: 'type(typ) == set' is false""")
      self.typ = typ
 def checkType ( self, x):
      if not type(x) == set:
        raise Exception("""assertion error: 'type(x) == set' is false""")
      if len(x) != len(self.typ) : 
           return False
      i = 0
      while i < len(x) :
           t = self.typ[i].checkType(x[i])
           if t == False : 
                return False
           i+=1
      return True

class TupleOfTypes(TypeChecker):
 def __init__ ( self, typ):
      if not type(typ) == tuple:
        raise Exception("""assertion error: 'type(typ) == tuple' is false""")
      self.typ = typ
 def checkType ( self, x):
      if not type(x) == tuple:
        raise Exception("""assertion error: 'type(x) == tuple' is false""")
      if len(x) != len(self.typ) : 
           return False
      i = 0
      while i < len(x) :
           t = self.typ[i].checkType(x[i])
           if t == False : 
                return False
           i+=1
      return True


if __name__ == '__main__':

    print( checkType("ssstr",str,cond_fun= lambda x : len(x) < 3))
    print( ensureType("ssstr",str,cond_fun= lambda x : len(x) < 8))