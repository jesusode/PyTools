#Soporte para control de tipos------------------------------------------------------------

import sys
sys.path.append('.')

from typing import *
import inspect
import copy

from functypes import *



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
                raise Exception("Type Error in ensureType: Expected type %s in parameter %s. Found type %s" %(typ,obj,type(obj)))
        else:
            raise Exception("Type Error in ensureType with option strict: Expected type %s in parameter %s. Found type %s" %(typ,obj,type(obj)))
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
                    raise Exception("Type Error. Expected type %s in function %s, parameter %s:(%s).Found type %s" % (typelist[i],f.__name__,i,args[i],type(args[i])))
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
                    raise Exception("Type Error in returnType: Expected return type %s in function %s. Found type %s" % (typ,f.__name__,type(result)))
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
              raise Exception("""assertion error in funSignature: 'len(args) == len(typelist)' is false""")
            i = 0
            while i < len(args) :
                if typelist[i]!= any and type(args[i]) != typelist[i] : 
                    raise Exception("Type Error in funSignature. Expected type %s in function %s, parameter %s:(%s).Found type %s" % (typelist[i],f.__name__,i,args[i],type(args[i])))
                i+=1
            result = f(*args)
            if returntype!= any and type(result) != returntype : 
                raise Exception("Type Error in funSignature: Expected return type %s in function %s. Found type %s" % (returntype,f.__name__,type(result)))
            return result
        wrapper = function4
        return wrapper
    decorator = function5
    return decorator


def applySignature(fun,argstypes,rettype):
    _decorator=funSignature(argstypes,rettype)
    return _decorator(fun)

#Comprueba que las anotaciones de tipos coinciden con los tipos
#de los argumentos pasados
def annotsSignature(fun : Callable) -> Callable:
    assert(callable(fun))
    annots = fun.__annotations__
    #print(f"annots:{annots}")
    #print(type(Dict))
    names = list(annots.keys())
    def wrapper(*args) :
        i=0
        while i < len(args) :
            #print(f"analizando argumento {args[i]}, i:{i}, len(names):{len(names)}")
            if annots!={} and i<len(names) and isinstance(annots[names[i]],Type) and type(args[i]) != annots[names[i]] : 
                raise Exception("Type Error in annotsSignature. Expected type %s in function %s, parameter %s:(%s).Found type %s" % (annots[names[i]],f.__name__,i,args[i],type(args[i])))
            i+=1
        result = fun(*args)
        if annots!={}  and 'return' in annots and isinstance(annots['return'],Type) and type(result) != annots['return'] : 
            raise Exception("Type Error in annotsSignature: Expected return type %s in function %s. Found type %s" % (annots['return'],f.__name__,type(result)))
        return result
    return wrapper

def applyAnnotsSignature(f :Callable,typeslist :List[Type],rettype:Type = None):
    #f puede o no tener anotaciones ya
    olds = f.__annotations__
    sign = inspect.signature(f)
    params = sign.parameters
    assert(len(typeslist) <= len(params))
    retval = inspect.signature(f).return_annotation
    #Ponemos las anotaciones en params por orden
    cont = 0
    newpars_list=[]
    for par in params:
        if cont == len(typeslist): break
        newpars_list.append(inspect.Parameter(params[par].name,params[par].kind,annotation=typeslist[cont]))
        f.__annotations__[par]=typeslist[cont]
        #params[par].annotation = typeslist[cont]
    #Si hay rettype, lo ponemos
    new_sign = None
    if rettype != None:
        new_sign = sign.replace(parameters=newpars_list,return_annotation = rettype)
    else:
        new_sign = sign.replace(parameters=newpars_list)
        if 'return' in f.__annotations__:
            del f.__annotations__['return']
    f.__signature__ = new_sign
    #print(f.__signature__)
    #print(f.__annotations__)
    #Y devolvemos el wrapper
    return annotsSignature(f)

#-------------------------------------------------------------------------------------------


#Clase comodin para tipos----------------------
class any(object): pass
#----------------------------------------------

#Definimos unit como el tipo de None-----------
nulltype = type(None)
#----------------------------------------------



#Clases para construir comprobadores de tipos(composite de TypeCheckers)
class TypeChecker(object):
    def __init__ ( self, typl):
      self.typ = typl[0]
    def checkType ( self, x):
      return True if type(x) == self.typ else False


#class ClassTypeChecker(object):
#    def __init__ ( self, typl):
#      self.typ = typl[0]
#    def checkType ( self, x):
#      return checkType(x,typl)

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
    #@annotsSignature
    def f(a:int,b:int)->int:
        return a+b
    print(f.__annotations__)
    f.__annotations__['b'] = float
    print(f.__annotations__)    
    print(inspect.signature(f).parameters)
    print(inspect.signature(f).return_annotation)
    f(8,9)
    g = applyAnnotsSignature(f,[int,int],int)
    print(g.__annotations__)
    g(8,9)