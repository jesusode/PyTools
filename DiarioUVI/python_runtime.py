#Funciones de utilidad
import sys
import types
import copy
import string
import codecs
import io
import math
import time
import ctypes
import locale
import functools
from functools import reduce
import abc
import bs4
import html

HY_AVAILABLE=0 #Gestionar carga de Hy con una directiva -lisp (es lento y entorpece el arranque)
TK_AVAILABLE=0 #Uso de formbox

import imp
#import md5
import platform
#import inspect
if not 'java' in sys.platform and not 'cli' in sys.platform:
    import cProfile
#import xml
if not 'java' in sys.platform:
    import json

#Soporte para subprocesos
import subprocess

#Revisar
import threading
import _thread
import socket
#No hay multiprocessing en jython ni iPad/iPhone
if not 'java' in sys.platform and not'iPad' in platform.platform() and not 'iPhone' in platform.platform():
    import multiprocessing

#Soporte para async (parece que funciona bien en jython y iPad/iPhone)
import concurrent.futures

#Soporte ADO en win32---------------
if 'win32' in sys.platform:
    if platform.python_implementation() not in ["PyPy"]:
        import minimal_ado
        import win32com
#-----------------------------------

#Soporte Tkinter para usar formbox-------------
if '-tk' in sys.argv:
    if not 'java' in sys.platform and not'iPad' in platform.platform() and not 'iPhone' in platform.platform():
        import tkinter
        import mini_tkbasic
        TK_AVAILABLE=1
    else:
        raise Exception("Error: Tkinter no esta disponible en esta plataforma")
#----------------------------------------------

#Ojo: esto peta si queremos un ejecutable con py2exe!!!----------------------------
# if '-math' in sys.argv:#??????????????
    # import sympy
#----------------------------------------------------------------------------------

if not 'os' in sys.modules:
     os=__import__('os')
else:
    os=sys.modules['os']
if not 'os.path' in sys.modules:
     os.path=__import__('os.path')
else:
     os.path=sys.modules['os.path']
if not 'inspect' in sys.modules:
     inspect=__import__('inspect')
else:
     inspect=sys.modules['inspect']
if not 'itertools' in sys.modules:
     itertools=__import__('itertools')
else:
     itertools=sys.modules['itertools']
if not 're' in sys.modules:
     re=__import__('re')
else:
     re=sys.modules['re']
if not 'glob' in sys.modules:
     glob=__import__('glob')
else:
     glob=sys.modules['glob']
if not 'fnmatch' in sys.modules:
     fnmatch=__import__('fnmatch') 
else:
     fnmatch=sys.modules['fnmatch']
#import xml.dom.minidom as minidom
try:
    if not 'sqlite3' in sys.modules:
         sqlite3=__import__('sqlite3')
    else:
         sqlite3=sys.modules['sqlite3']
    SQLITE=1
except:
    SQLITE=0
if not 'prologpy' in sys.modules: 
     prologpy=__import__('prologpy')
else:
     prologpy=sys.modules['prologpy']
if not 'heapq' in sys.modules:
     heapq=__import__('heapq')
else:
     heapq=sys.modules['heapq']
if not 'urllib' in sys.modules:
    urllib=__import__('urllib')
else:
    urllib=sys.modules['urllib']
# if not 'requests' in sys.modules:
    # requests=__import__('requests')
# else:
    # request=sys.modules['requests']
if not 'shutil' in sys.modules:
     shutil=__import__('shutil')
else:
     shutil=sys.modules['shutil']

if not 'inspect' in sys.modules:
    inspect=__import__('inspect')
else:
    inspect=sys.modules['inspect']

if not 'pickle' in sys.modules:
    pickle=__import__('pickle')
else:
    pickle=sys.modules['pickle']

#if not 'lispy' in sys.modules:
#    lispy=__import__('lispy')
#else:
#    lispy=sys.modules['lispy']

import io
import collections
import requests
#------------------------------------------------------------------------------
#Clase que envuelve un StringBuffer
#El contenido del buffer se obtiene con una llamada al mismo sin argumentos
#Para poner strings en el buffer se pude usar el operador +
# que admite un string o bien otro StringBuffer,
#o un llamada con tantos argumentos como se quieran meter en el buffer
#------------------------------------------------------------------------------ 
class StringBuffer:
    def __init__(self,*vals):
        self._sb= io.StringIO()
        self._encoding='utf-8'
        if vals!=(): 
            for item in vals:
                if type(item)==str:
                    self._sb.write(item)
                elif isinstance(item,StringBuffer):
                    self._sb.write(item._collect())
                else:
                    self._sb.write(str(item))
        self.__canCollect=True

    def getEncoding(self):
        return self._encoding

    def setEncoding(self,enc):
        self._encoding=enc

    def _canCollect(self):
        return self.__canCollect

    def __add__(self,astr):
        if self._canCollect():
            if type(astr) in [str,str]:
                self._sb.write(str(astr))
            elif isinstance(astr,StringBuffer):
                self._sb.write(str(astr._collect()))
            else:
                self._sb.write(str(astr))

    def __call__(self,*args):
        if args!=():
            for item in args:
                if type(item) in [str,str]:
                    self._sb.write(str(item))
                elif isinstance(item,StringBuffer):
                    self._sb.write(str(item._collect()))
                else:
                    self._sb.write(str(item))
            return ""
        else:
            return self._collect()

    def _collect(self):
        if self._canCollect():
            self.__canCollect=False
            return self._sb.getvalue()
        else:
            raise Exception("Error: This StringBuffer has been collected yet!")

#---------------------------------------------------------------------------------------------------


#codigo multiplataforma para getch() Usar getchar con ctypes????
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            if 'darwin' in sys.platform:
                #self.impl=_GetchMacCarbon()
                self.impl=_GetchIOS()
            else:
                self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchIOS:
    def __call__(self):
        return ""

class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        import Carbon
        Carbon.Evt #see if it has this (in Unix, it doesn't)

    def __call__(self):
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            #
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned
            #
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


_getch = _Getch()

#Probar si funciona en Mac------------------------------------------------------
def getch():
    """
    Interrupting program until pressed any key
    """
    try:
        import msvcrt
        return msvcrt.getch()

    except ImportError:
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch 
#-------------------------------------------------------------------------------


#Para usar BeautifulSoup--------------------------------------------------------------
from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
try: #Usar lxml si esta disponible y si no, ElementTree
    import lxml

    def _getxmldoc(string,encoding='utf-8'):
        return lxml.etree.fromstring(bytes(string,encoding))

    def _xpath(element_source,xpath_expression,encoding='utf-8'):
        root=None
        #print(type(element_source))
        if type(element_source) in [str,bytes]:
            root = lxml.etree.fromstring(bytes(element_source,encoding))
        else:
            root= element_source
        #print(root)
        return root.xpath(xpath_expression)

    def _insertInXpath(doc,xpath,elem):
        root=None
        if type(doc)==str:
            root = lxml.etree.fromstring(doc)
        else:
            root= doc
        root=lxml.etree.ElementTree(root)
        for item in root.xpath(xpath):
            if type(elem)==str:
                el = lxml.etree.fromstring(elem)
            else:
                el= elem
            item.append(el)
        return root

    def _toxml(lxmlelem,encoding="utf-8",errors="replace"):
        return html.unescape(lxml.etree.tostring(lxmlelem,pretty_print=True).decode(encoding,errors))

except: #Si no hay lxml, nos vamos al que viene con python
    import xml.etree.ElementTree as ET

    def _getxmldoc(string):
        return ET.fromstring(string)

    def _xpath(element_source,xpath_expression): #No hay xpath con minidom
        root=None
        if type(element_source) in [str,bytes]:
            root = ET.fromstring(element_source)
        else:
            root= element_source
        return root.findall(xpath_expression)

    def _insertInXpath(doc,xpath,elem):#No hay xpath con minidom
        root=None
        if type(doc)==str:
            root = ET.fromstring(doc)
        else:
            root= doc
        for item in root.findall(xpath):
            if type(elem)==str:
                el = ET.fromstring(elem)
            else:
                el= elem
            item.append(el)
        return root

    def _toxml(xmlelem,encoding="utf-8",errors="replace"):
        return ET.tostring(xmlelem).decode(encoding,errors)

#Para usar xmltodict----------------------------------
if not 'cli' in sys.platform and not 'java' in sys.platform:
    if not 'xmltodict' in sys.modules:
         xmltodict=__import__('xmltodict')
    else:
        xmltodict=sys.modules['xmltodict']
#-------------------------------------------------------------------------------------

#Soporte para codigo C via TCC------------------------------------------------
if not 'iPad' in platform.platform() and not 'iPhone' in platform.platform():
    import minimal_cc
#-----------------------------------------------------------------------------

#Contiene los nombres de las clases declaradas como final class...--------
__sealed__=[]
#-------------------------------------------------------------------------


#Soporte para pattern match para Python----------------------------------------------
#import pprint
def installVars(mod_name,seq,*_vars):
    __this=sys.modules[mod_name]
    for i in range(len(_vars)):
        if not _vars[i] in __this.__dict__:
            setattr(__this, _vars[i], seq[i])
    return True

def installVars2(mod_name,seq,h,t):
    __this=sys.modules[mod_name]
    if not h in __this.__dict__:
        setattr(__this, h, seq[0])
    if not t in __this.__dict__:
        setattr(__this, t, seq[1:])
    return True
#-----------------------------------cls--------------------------------------------------

#Soporte para clases anonimas tipo registro----------------------------------------------
#Deberia ser inmutable?????
class anonym(object):
    def __init__(self,**fields):
        for item in fields:
            setattr(self,item,fields[item])
    def __repr__(self):
        return ">>Bridge anonym object: %s"%self.__dict__

def anonymObjectFactory(**fields):
    return anonym(**fields)

#Para uso en codigo
_anonymObjectFactory=anonymObjectFactory

#----------------------------------------------------------------------------------------


#Base de las clases de minimal------------------------
class MiniMetaClass(type,metaclass=abc.ABCMeta):
    def __new__(meta, name, bases, dct):
        global __sealed__
        for base in bases:
           #print 'mirando base: %s' % base.__name__
           if base.__name__ in __sealed__:
               raise Exception('Error: la clase "%s" esta sellada y no se puede heredar de ella'%base.__name__)
        return super(MiniMetaClass, meta).__new__(meta, name, bases, dct)
    def __init__(cls, name, bases, dct):
        super(MiniMetaClass, cls).__init__(name, bases, dct)
#--------------------------------------------------------

#Base de las clases de bridge-------------------------
class MiniObject(object,metaclass=MiniMetaClass):
    #Handles "missing" attributes
    def __getattr__(self,name): 
       return self.missing(name)
    def missing(self,name):
        raise Exception('Error: El campo "%s" no esta definido en la clase "%s"'%(name,self))
#-----------------------------------------------------

#Soporte para control de tipos------------------------------------------------------------

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

#Creador de clases dinamicas
def classfactory(classname,bases,attributes):
    return type(classname,bases,attributes)

_classfactory=classfactory

#Funcion que mete metodos como si fueran de instancia de clase
def addMethodsToClassOrInstance(instance,methods):
    for method in methods:
        setattr(instance,method.__name__,method)
    return instance

_addMethodsToClassOrInstance=addMethodsToClassOrInstance

#Clase comodin para tipos
class any(object):pass

#Decorador
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

#Esta version puede comprobar si es un subtipo del tipo a comprobar
def ensureType ( obj, typ,strict=False,cond_fun=None):
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

#Para usarlo como funcion estandar
_ensureType=ensureType

def checkType ( obj, typ,strict=False,cond_fun=None):
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

#Para usarlo como funcion estandar
_checkType=checkType

def ensureTypeInUnion ( obj, typelist,strict=False,cond_fun=None):
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

#Para usarlo como funcion estandar
_ensureTypeInUnion=ensureTypeInUnion

def checkTypeInUnion ( obj, typelist,strict=False,cond_fun=None):
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

#Para usarlo como funcion estandar
_checkTypeInUnion=checkTypeInUnion

#Decorador         
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

#Decorador
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

#para usar en codigo
_applySignature=applySignature


#Fin soporte para control de tipos-----------------------------------------------------------------------------------------------------------------------------

#from http://code.activestate.com/recipes/576366-y-combinator/
'''
Implementation of the fixed point combinator Y. 
-----------------------------------------------

The Y combinator is a higher order function that suffices following relation:

      Y(F) = F(Y(F))

From the fixed point property we can get an idea on how to implement a recursive 
anonymous function.

The function F passed to Y has to be a function that takes a single function argument 
f and produces another function g ( i.e. Y(F) ). 

Suppose g calls f again. In a simple case where g takes also only one argument we 
can write:

     g = lambda n: ... f( ... n )

A concrete example of g we use to proceed the discussion is:

     g = lambda n: (1 if n<2 else n*f(n-1))

If g is returned by F(f) we can write:

     F = lambda f: lambda n: (1 if n<2 else n*f(n-1))

Now we call F passing Y(F):

     Y(F) = F(Y(F)) = lambda n: (1 if n<2 else n*Y(F)(n-1))
     
Finally we state:

     Y(F)(k) = (1 if k<2 else k*Y(F)(k-1))           
'''
Y = lambda g: (lambda f: g(lambda arg: f(f)(arg))) (lambda f: g(lambda arg: f(f)(arg)))
_Y=Y

#Soporte para comparar elementos de dos listas de forma recursiva: None es el comodin
def compareLists(problem,pattern):
    assert len(problem)==len(pattern)
    assert type(problem)==list
    assert type(pattern)==list
    for i in range(len(problem)):
        if pattern[i]==None: continue
        if type(problem[i])!=list and problem[i]!=pattern[i]:
            return False
        else:
            if type(problem[i])==list and compareLists(problem[i],pattern[i])==False:
                return False
            else:
                continue
    return True

_compareLists=compareLists

def ireduce(func, iterable, init=None): #??
    if init is None:
        iterable = iter(iterable)
        curr = next(iterable)
    else:
        curr = init
    for x in iterable:
        curr = func(curr, x)
        yield curr

def weave(*iterables):
    "Intersperse several iterables, until all are exhausted"
    iterables = list(map(iter, iterables))
    while iterables:
        for i, it in enumerate(iterables):
            try:
                yield next(it)
            except StopIteration:
                del iterables[i]

def tramp(gen, *args, **kwargs):
    g = gen(*args, **kwargs)
    while isinstance(g, types.GeneratorType):
        g=next(g)
    return g

def copy_func(f, name=None):
    return types.FunctionType(f.__code__, f.__globals__, name or f.__name__,f.__defaults__, f.__closure__)

def _check_py_bases(bases):
    for item in bases:
        if not inspect.isclass(item):
            raise Exception('Error: el tipo "%s" no se corresponde con una clase Python valida'%item)


def _get_files(patlist,srclist):
    all=[]
    filter=[]
    for item in srclist:
        if os.path.isfile(item):
            all.append(item)
        elif os.path.isdir(item):
            for root,dirs,files in os.walk(item):
                all+=[root + '/' + i for i in files]
        else:
            raise Exception('Error: debe ser un archivo o directorio')
    #filtrar ahora los que nos interesan
    for pat in patlist:
        filter+=fnmatch.filter(all,pat)
    return filter
     
    
def _get_directories(srclist):
    all=[]
    for item in srclist:
        if os.path.isdir(item):
            for root,dirs,files in os.walk(item):
                all.append(root)
                all+=dirs
        else:
            raise Exception('Error: debe ser un directorio')
    return all


def _itermix(*iters):
    return list(weave(*iters));

def _trampoline(gen,*args,**kwargs):
    return tramp(gen,*args,**kwargs);

class TailRecurseException(BaseException):
  def __init__(self, args, kwargs):
    self.args = args
    self.kwargs = kwargs

def tail_call_optimized(g):
  """
  This function decorates a function with tail call
  optimization. It does this by throwing an exception
  if it is it's own grandparent, and catching such
  exceptions to fake the tail call optimization.
  
  This function fails if the decorated
  function recurses in a non-tail context.
  """
  def func(*args, **kwargs):
    f = sys._getframe()
    if f.f_back and f.f_back.f_back \
        and f.f_back.f_back.f_code == f.f_code:
      raise TailRecurseException(args, kwargs)
    else:
      while 1:
        try:
          return g(*args, **kwargs)
        except TailRecurseException as e:
          args = e.args
          kwargs = e.kwargs
  func.__doc__ = g.__doc__
  return func


#Ojo curry funciona siempre por la izquierda
class curry(object): #en js es .bind()
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.fun(*(self.pending + args), **kw)

#Ojo curry_right funciona siempre por la derecha
class curry_right(object):
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.fun(*(args + self.pending), **kw)

class curry_positional(object):
    def __init__(self, fun, pos_args):
        self.fun = fun
        self.pos_args = pos_args

    def __call__(self, *args, **kwargs):
        kw = kwargs
        #Asumimos que el num args es los guardados mas los pasados
        new_args = [None]*(len(args) + len(self.pos_args))
        #Colocar los argumentos en sus posiciones
        for item in self.pos_args.items():
            new_args[item[0]]=item[1]
        for item in args:
            for i in range(len(new_args)):
                if new_args[i]==None:
                    new_args[i]=item
        print('NEW_ARGS in curry_positional: %s'%new_args)
        return self.fun(*new_args, **kw)


class closure(object): #??
    def __init__(self, fun, **kwargs):
        self.fun = fun
        self.kwargs = kwargs
        for item in kwargs:
           setattr(self,item,kwargs[item])

    def __setattr__(self,attr,value):
        object.__setattr__(self,attr,value)
        if hasattr(self,"kwargs") and attr!="kwargs":
            self.kwargs[attr]=value

    def __call__(self, **kwargs):
        #actualizar las variables pasadas
        kw=None
        for item in kwargs:
            if item in self.kwargs:
               self.kwargs[item]=kwargs[item]
               setattr(self,item,kwargs[item]) 
        kw=copy.deepcopy(self.kwargs)
        kw.update(kwargs)
        if kw!={}:
            return self.fun(**kw)
        else:
            return self.fun()



class compose(object):
    def __init__(self, funs):
        self.funs = list(funs)
        self.funs.reverse()
        
    def __call__(self, *args):
        t=args
        for f in self.funs:
            if type(t) in [list,tuple]:
                t=f(*t)
            else:
                t=f(t)
        return t
            

def _fcopy(f):
    if isinstance(f,(curry,compose,closure)):
        return copy.deepcopy(f)
    else:
        return copy_func(f)


def _decorate(f,**kwargs):
    for item in list(kwargs.keys()):
        setattr(f, item , kwargs[item])
    return f


def _flat(lst):
    flatted=[]
    #print("lst in _flat: %s"%repr(lst))
    for el in lst:
        #print ("type(el) in flat: %s"%type(el))
        if type(el)==list or isinstance(el,list):
            for item in _flat(el):
                flatted.append(item)
        else:
            flatted.append(el)
    return flatted

def _getSystem():
    #return sys.platform
    return platform.platform()

def _cmdline(start=2):
    return sys.argv[start:]

def _profilepy(code):
    return cProfile.run(code)

def _pause(ms):
    time.sleep(ms)


#Longitud de un archivo
def _filesize(fpath):
   return  os.path.getsize(fpath)


#Funciones para consola de windows

def _setWinConsoleCodePage(codepage): #Necesario en Python3????
    if os.name == 'nt':
        res=ctypes.windll.kernel32.SetConsoleCP(_toint(codepage))
        res=ctypes.windll.kernel32.SetConsoleOutputCP(_toint(codepage))

def _print(x,encoding='utf-8',redirected=None,end='\n'):
    #print("type(x) en print: %s"%type(x))
    if redirected!=None:
        print(x, file=redirected,end=end)
        return
    if x==None:
        print('null',end=end,file=redirected)
    elif type(x)==bool:
        #print 'Imprimiendo un bool'
        if x==True:
            print('true',end=end,file=redirected)
        else:
            print('false',end=end,file=redirected)
    elif _type(x) not in [str,bytes]:
        print(str(x),end=end,file=redirected)
    else:
        if type(x)==str:#unicode
            try:
                print(x,end=end,file=redirected)
            except:
                print(bytes(x,encoding=encoding,errors='replace'),end=end,file=redirected)
        else:
            print(x.decode(encoding=encoding,errors='replace'),end=end,file=redirected)

def _input(x="",endline='\n'):
   return input(x).strip()

#funciones para obtener stdin,stdout y stderr-----------------------------
def _getStdin():
    return sys.__stdin__

def _getStdout():
    return sys.__stdout__

def _getStderr():
    return sys.__stderr__
#--------------------------------------------------------------------------

#getchar multiplataforma(verlo: en Mac no funciona)
def _getchar():
    return getch()
   
def _eval(x):
   return eval(x)
   
def _exec(x):
   exec(x,globals())
   return 1

def _del(x):
    del x
    return 1

def _type(x):
    return type(x)

def _tostring(x):
    return str(x)

def _lower(x):
    return x.lower()

def _upper(x):
    return x.upper()

def _capitalize(x):
    return x.capitalize()

def _adjust(x,numchars,lrc,fillchar=None):
    if lrc=="l":
        if fillchar!=None:
            return x.ljust(numchars,fillchar)
        else:
            return x.ljust(numchars)
    elif lrc=='r':
        if fillchar!=None:
            return x.rjust(numchars,fillchar)
        else:
            return x.rjust(numchars)
    else:
        if fillchar!=None:
            return x.center(numchars,fillchar)
        else:
            return x.center(numchars)

#Version de format mas pobre que no usa la de Python(porque da problemas si en la cadena hay {})
#pero es mas homogenea con el resto de lenguajes(REVISAR)
def _format(cad,lst):
    n= cad
    #print("lst: %s" % lst)
    #print( "cad: " + cad)
    for i in range(len(lst)):
       p='\{' + str(i) + '\}'
       #print('VALOR DE P: %s' % p)
       n= re.sub(re.compile(p),str(lst[i]),n)
       #n= re.sub(re.compile(p),_tostring(lst[i]),n)
       #print ("valor de n: " + n)
    return n


#Math functions	
def _mod(x,y):
    return int(x%y)

def _divmod(x,y):
    return divmod(x,y)

def _floor(x):
    return math.floor(x)

def _ceil(x):
    return math.ceil(x)

def _round(x,digits):
    return round(x,digits)

def _fact(x):
    return math.factorial(x)

def _sqrt(x):
    return math.sqrt(x)

def _exp(x):
    return math.exp(x)

def _ln(x):
    return math.log(x,math.e)

def _log(x,base=None):
    if base!=None:
        return math.log(x,base)
    else:
        return math.log10(x)

def _sin(x):
    return math.sin(x)

def _asin(x):
    return math.asin(x)

def _cos(x):
    return math.cos(x)

def _acos(x):
    return math.acos(x)

def _tan(x):
    return math.tan(x)

def _atan(x):
    return math.atan(x)

def _sinh(x):
    return math.sinh(x)

def _asinh(x):
    return math.asinh(x)

def _cosh(x):
    return math.cosh(x)

def _acosh(x):
    return math.acosh(x)

def _tanh(x):
    return math.tanh(x)

def _atanh(x):
    return math.atanh(x)

#List functions
def _append(x,y):
    y.append(x)

def _append2(x,y):
    y.append(x)
    return y

def _extend(x,y):
    y.extend(x)
    return y

def _apply(f,*args):
    return f(args)

def _reverse(x):
    #x.reverse()
    return list(reversed(x))

def _cons(x,y):
    return [x]+y

def _car(x):
    return x[0]

def _last(x):
    return x[-1]

def _butlast(x):
    return x[0:-1]

def _cdr(x):
    return x[1:]

def _index(el,lst):
    return lst.index(el)

def _sublist(s,b,e=None):
    if e:
        return s[b:e]
    else:
        return s[b:]

def _insert(lst,idx,obj):
    lst.insert(idx,obj)
    return lst

#Functional utils
def _curry(f,*args,**kwargs):
    return curry(f,*args,**kwargs)

def _curry_right(f,*args,**kwargs):
    return curry_right(f,*args,**kwargs)

def _curry_positional(f,pos_table):
    return curry_positional(f,pos_table)

def _closure(f,*args,**kwargs):
    return closure(f,*args,**kwargs)
    
def _compose(*funs):
    return compose(funs)

#Alternativa con funciones para todas las formas funcionales del lenguaje--------
def _slice(s,b,e=None):
    if e:
        return s[b::e]
    else:
        return s[b::]

def _foreach(seq,fun):
    for i in range(len(seq)):
        seq[i]=fun(seq[i])

#RESTO PENDIENTE!!!!!
#------------------------------------------------------------------------------------

#Soporte para transacciones-----------------------------------------------------
def Memento(obj, deep=False):
   state = (copy.copy, copy.deepcopy)[bool(deep)](obj.__dict__)
   def Restore():
      obj.__dict__.clear()
      obj.__dict__.update(state)
   return Restore

class Transaction:
   """A transaction guard. This is realy just 
      syntactic suggar arount a memento closure.
   """
   deep = False
   def __init__(self, *targets):
      self.targets = targets
      self.Commit()
   def Commit(self):
      self.states = [Memento(target, self.deep) for target in self.targets]
   def Rollback(self):
      for state in self.states:
         state()

class transactional(object):
   """Adds transactional semantics to methods. Methods decorated 
      with @transactional will rollback to entry state upon exceptions.
   """
   def __init__(self, method):
      self.method = method
   def __get__(self, obj, T):
      def transaction(*args, **kwargs):
         state = Memento(obj)
         try:
            return self.method(obj, *args, **kwargs)
         except:
            state()
            raise
      return transaction

def _transaction(*objs):
    return Transaction(*objs)
def _rollback(*transactions):
    for t in transactions:
        t.Rollback()
    return 1
#-----------------------------------------------------------------------------------------

#Soporte para synchronized-----------------------------------------------------------------
#(decorador @synchronized)
def synchronized(func):
    func.__lock__ = threading.Lock()
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)
    return synced_func
#-------------------------------------------------------------------------------------------

def _split(s,tk):
    return s.split(tk)

def _strip(s,it=None):
    if it==None:
        return s.strip()
    else:
        return s.strip(it)

def _join(el,lst):
    return el.join(lst)

def _replace(s,old,new):
    return s.replace(old,new)

def _find(s,el,begin=0,end=None):
    if end==None:
        end=len(s)
    return s.find(el,begin,end)

#Funciones Python imprescindibles
_list=list
#_split=string.split
#_strip=string.strip
#_join=string.join
_size=len
_abs=abs
_toint=int #long??
_tofloat=float
_system=os.system
_copy=copy.deepcopy
#_replace=string.replace #_replace(old,new[,max_replaces])
#_find=string.find #find(str, beg=0, end=len(string))
_tuple=tuple
_set=set
_namedtuple=collections.namedtuple
_enumerate=enumerate

def _strinsert(cad,new,start,end):#??????????
    cad[start:end]=new
    return cad

#Utilidades para diccionarios
def _keys(dic):
    return list(dic.keys())

def _values(dic):
    return list(dic.values())

def _pairs(dic):
    return [list(el) for el in list(dic.items())]

def _filterdict(d,pred):
    sd={}
    for k in d.keys():
        if pred(x):
            sd[k]=d[k]
    return sd

def _splitDictByPred(d,pred):
    yes={}
    no={}
    for k in d.keys():
        if pred(k):
            yes[k]=d[k]
        else:
            no[k]=d[k]
    return [yes,no]

def _splitDictByPreds(d,predlist):
    results=[]
    for el in predlist:
        results.append({})
    for k in d.keys():
        for i in range(len(predlist)):
            if predlist[i](k):
                results[i][k]=d[k]
    return results



#Expresiones regulares
def _rematch(exp,cad,flags=0):
    return re.findall(exp,cad,flags)

def _rereplace(cad,old,new,flags=0):
    return re.sub(old,new,cad,flags)

def _resplit(cad,exp,flags=0):
    return re.split(exp,cad,flags)

def _regroups(exp,cad,n=-1,flags=0):
    if n==-1:
        return [[x.group(),x.start(),x.end()] for x in re.finditer(exp,cad,flags=0)]
    else:
        return [[x.group(n),x.start(n),x.end(n)] for x in re.finditer(exp,cad,flags=0)]

def _isclass(el):
    #return type(el) not in [str,bytes,int,float,set,tuple,list,dict]
    return inspect.isclass(el)

def _count(el,seq): 
    return seq.count(el)

def _histogram(seq):
    hist = {};
    def f(a):
        if a in hist:
            hist[a]+=1
        else:
            hist[a]=1
    list(map(f,seq))
    return hist;

def _indexof(el,seq): 
    return seq.index(el)

#Cambia el encoding por defecto
#Peligroso????
def _setencoding(encoding):
    imp.reload(sys)
    sys.setdefaultencoding(encoding)
    return encoding

def _open(path,mode='r',encoding='utf-8',errors='ignore'):
    if not 'b' in mode:
        return io.open(path,mode,encoding=encoding,errors=errors)
    else:
        return open(path,mode)

def _close(fhandle):
    fhandle.close()

def _readf(f,encoding='utf-8',errors='replace'): 
    #io.open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)
    return io.open(f,'r',encoding=encoding,errors=errors).read()

def _readflines(f,encoding='utf-8',errors='replace'): 
    return io.open(f,'r',encoding=encoding,errors=errors).readlines()

def _readflist(flist,encoding='utf-8',errors='ignore'):
    texts=[]
    for item in flist:
        texts.append(_readf(item,encoding,errors))
    return texts

#Escritura en archivos de texto que acepta un encoding
def _writef(fl,_bytes,encoding='utf-8',append=1): 
    f=None
    if append==0:
        f= io.open(fl,'w',encoding=encoding)
    else:
        f= io.open(fl,'a',encoding=encoding)
    b=str(_bytes)
    f.write(b)
    f.close()
    return 1

def _writeflines(fl,lines,encoding='utf-8',append=1): 
    f=None
    if append==0:
        f= io.open(fl,'w',encoding=encoding)
    else:
        f= io.open(fl,'a',encoding=encoding)
    for line in lines:
        f.write(line)
    f.close()
    return 1

#Funciones de utilidad del modulo itertools---------
_chain=itertools.chain
#_zip=itertools.izip
def _zip(*seqs):
    return [list(x) for x in zip(*seqs)]
def _enumerate(seq):
    return [list(x) for x in list(enumerate(seq))]
def _cartessian(*seqs):
    return [list(x) for x in list(itertools.product(*seqs))]
def _combinations(seq,n):
    return [list(x) for x in list(itertools.combinations(seq,n))]
def _combinations_with_r(seq,n):
    return [list(x) for x in list(itertools.combinations_with_replacement(seq,n))]
def _permutations(seq,n):
    return [list(x) for x in list(itertools.permutations(seq,n))]
def _starmap(f,seq):
    for item in seq:
        yield f(*item)
def _cycle(seq):
    i=0
    while i<len(seq)+1:
        if i==len(seq): i=0
        yield seq[i]
        i+=1

#xml-------------------------------------------------------------------
def _xmltod(xml):
    return xmltodict.parse(xml)

def _dtoxml(dict): #falla a veces. Revisar
    return xmltodict.unparse(dict)

# def _xmlstr(_xml):
    # if _xml.nodeType == 4: #CDATA
        # return _xml.data
    # elif not isinstance(_xml,xml.dom.minidom.Attr) and hasattr(_xml,'toxml'):
        # return _xml.toxml()
    # elif hasattr(_xml,'value'):
        # return _xml.value
    # else:
        # return ''
#Condicional porque no todos los sistemas tienen lxml
#Ojo: La transformacion DEBE producir xhtml VALIDO, o no funciona bien
try:
    import lxml.etree as ET

    def _applyXSLT(_xml,xsl):
        #dom = ET.parse(xml)
        #xslt = ET.parse(xsl)
        dom = ET.XML(_xml)
        xslt = ET.XML(xsl)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        return ET.tostring(newdom, pretty_print=True)
except:
    def _applyXSLT(xml,xsl):
        return xml
#----------------------------------------------------------------------

#Coger contenido de una url---------------------------------------------
def _geturl(url): 
    return getPathText(url)
#-----------------------------------------------------------------------

#Llamadas asincronas-----------------------------------------------------------
def asyncall(fn,callb,*args,**kwargs):#firma de callb: callb(future)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future=executor.submit(fn,*args,**kwargs)
        for future in concurrent.futures.as_completed([future]):
            data = future.result()
    retval=callb(data)
    return retval

def asynfun(fn,*args,**kwargs):
    executor=concurrent.futures.ThreadPoolExecutor(max_workers=3)
    future=executor.submit(fn,*args,**kwargs)
    return future
#-------------------------------------------------------------------------------

#----------------------------------------------------------------
#Funcion que evalua una S-expresion
def _scheme(sexpr):
   x=lispy.parse(sexpr.strip())
   if x is lispy.eof_object: return ''
   val=lispy.eval(x)
   return lispy.to_string(val) 

def _lisp(sexpr):
    if 'hy' in sys.modules:
        f=open('hytemp.hy','w')
        f.write(sexpr.strip())
        f.close()
        sys.modules['hy'].cmdline.run_file('hytemp.hy')
        return 1
    else:
        return 0


def _lispModule(mod_name,sexpr):
    #global HY_AVAILABLE
    #if HY_AVAILABLE==0: raise Exception('Error: el modulo Hy(lisp) no esta disponible en la plataforma "%s"'%sys.platform)
    if 'hy' in sys.modules:
        f=open(mod_name + '.hy','w')
        f.write(sexpr.strip())
        f.close()
        sys.modules[mod_name]=__import__ (mod_name)
        return 1
    else:
        return 0

#Ojo, retrasa la carga del programa(1M de codigo)
def _clojure(sexpr):
    if 'clojure' in sys.modules:
        f=open('cljtemp.clj','w')
        f.write(sexpr.strip())
        f.close()
        return sys.modules['clojure'].main.hack_for_minimal('cljtemp.clj') 
    return None


#Soporte para codigo C via TCC------------------------------------------
def _C(code,target,*dlls):
    dll=minimal_cc.C(code,target,*dlls)
    return dll

def _getC(dll,fun):
    return minimal_cc.getC(dll,fun)
#------------------------------------------------------------------------

#Soporte para gui Tk via formbox(a demanda)-----------
if TK_AVAILABLE==1:
    def _formbox(app_dict,label_list,label_types,data_dict,cancellable,noclose,menu_labels,menu_dict):
        return mini_tkbasic.formBox(app_dict,label_list,label_types,data_dict,cancellable,noclose,menu_labels,menu_dict)
    # def _message(title,message,type,icon):
       # return mini_tkbasic.messageBox(title,message,type,icon)
    # def _color(title):
       # return mini_tkbasic.getTkColor(title)
    # def _file(title,mode):
        # return mini_tkbasic.getTkFile(title,mode)
    # def _files(title):
        # return mini_tkbasic.getTkFiles(title)
    # def _dir(title):
        #return mini_tkbasic.getTkDir(title)
    def _getFormItemValue(form,item):
        return mini_tkbasic.getFormItemValue(form,item)
    def _setFormItemValue(form,item,value):
        return mini_tkbasic.setFormItemValue(form,item,value)
    def _getFormItem(form,item):
        return mini_tkbasic.getFormItem(form,item)
    def _callFormItem(form,item_name,func_name,args_list):
        return mini_tkbasic.callFormItem(form,item_name,func_name,args_list)
    def _setFormItemFont(form,item_name,font_descriptor):
        return mini_tkbasic.setFormItemFont(form,item_name,font_descriptor)
    def _tcl(code):
        tcl=tkinter.Tcl()
        return tcl.eval(code)
else:
    def _formbox(*args):
        return {}
    # def _message(*args):
        # return 0
    # def _color(*args):
        # return 0
    # def _file(*args):
        # return 0
    # def _files(*args):
        # return 0
    # def _dir(*args):
        # return 0
    def _getFormItemValue(*args):
        return 0
    def _setFormItemValue(*args):
        return 0
    def _getFormItem(*args):
        return 0
    def _callFormItem(*args):
        return 0
    def _setFormItemFont(*args):
        return 0
    def _tcl(*args):
        return 0
#--------------------------------------------------------

#Soporte JSON--------------------------------------------
def _tojson(elem):
    return json.dumps(elem)

def _fromjson(cad):
    return json.loads(cad)
#-------------------------------------------------------

#Funciones de soporte para sockets TCP cliente y servidor
def _socket_server(host,port,thread_func,maxconns=10):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host,port))
    except:
        raise Exception("Socket error: Unable to connect to %s : %s"%(host,port))
    s.listen(maxconns)
    while 1:
        conn,addr=s.accept()
        _thread.start_new_thread(thread_func ,(conn,))
    s.close()


def _socket_client(host,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host,port))
    except:
        raise Exception("Socket error: Unable to connect to %s : %s"%(host,port))
    return s


#Funciones web--------------------------------------------------------------------
_urlencode=urllib.parse.quote_plus
_urldecode=urllib.parse.unquote_plus

def _queryADO(constr,query,encoding='latin-1'):
    if 'win32' in sys.platform:
        return minimal_ado.minimalQuery(constr,query,encoding)
    else:
        return []

def _getDBADOinfo(constr):#????????
    if 'win32' in sys.platform:
        info=[]
        catalog=minimal_ado.DbInfo()
        conn=win32com.client.Dispatch("ADODB.Connection")
        conn.Open(constr)
        catalog.setConnection(conn)
        return catalog.getDbTables()
        
    else:
        return []

def genRange(start,end,step=1):
    if type(step) in [type(0),type(0)]:
        return list(range(start,end,step))
    else:
        resul=[]
        while start<end :
            resul.append(start)
            start+=step
        return resul

def doSort(x,func,reverse=0):
    try:
        # print 'al entrar: %s' % repr(list(x) )
        # print 'ordenada: %s' %sorted(list(x),key=func,reverse=reverse)
        # print sorted(x,key=func,reverse=reverse)
        return sorted(list(x),key=func,reverse=reverse)
    except:
        raise Exception('Error: "%s" no es una lista' %str(x))

def doFormat(template,plist):
    return _format(template,plist)

def doSerialize(id,dest=''):
    if dest: #and os.path.exists(dest) and os.path.isfile(dest):
        pickle.dump(id,open(dest,'wb'))
        return 1
    else:
        return pickle.dumps(id)

def doDeserialize(dest):
    #print("Valor de dest en deserizalize: %s" % dest)
    #if os.path.exists(dest) and os.path.isfile(dest):
    #    return pickle.load(open(dest,'rb'))
    #else:
    #    return pickle.loads(dest)
    try:
        return pickle.loads(dest)
    except:
        return pickle.load(open(dest,'rb'))

def doAddition(elem1,elem2):
    '''El operador + esta sobrecargado, reglas:
       si los dos son numeros: sumarlos
       si los dos son cadenas, combinarlas
       numero+cadena: cad + str(num)
       lista+lista: combinarlas
       lista+ cualquiera o cualquiera + lista: meter cualquiera en lista
       dict + dict: combinarlos
       al principio o al final
    '''
    if type(elem1) in [type(0),type(0),type(0.0)] and type(elem1) in [type(0),type(0),type(0.0)]:
        return elem1 + elem2
    elif type(elem1) in [type(0),type(0),type(0.0)] and type(elem2) in [type(''),type('')]:
        return str(elem1) + elem2
    elif type(elem2) in [type(0),type(0),type(0.0)] and type(elem1) in [type(''),type('')]:
        return elem1 + str(elem2)
    elif type(elem2) in [type(''),type('')] and type(elem1) in [type(''),type('')]:
        return elem1 + elem2
    elif type(elem2)==type([]) and type(elem1)==type([]):
        return elem1 + elem2
    elif type(elem2)==type([]) and type(elem1)!=type([]):
        elem2.append(elem1)
        return elem2
    elif type(elem1)==type([]) and type(elem2)!=type([]):
        elem1.append(elem2)
        return elem1
    elif type(elem2)==type({}) and type(elem1)==type({}):
        elem1.update(elem2)
        return elem1
    else:#cualquier otra combinacion es un error, si no esta definido como operador de una clase
        try:
          return elem1 + elem2
        except:
            raise Exception("Error: El operador '+' no esta definido para estos dos tipos de operando:\n  '%s  de tipo: %s'\n y\n  '%s  de tipo: %s'\n"%(elem1,type(elem1),elem2,type(elem2)))

def doGroup(seqs,func):
    res={}
    for s in seqs:
        if func(s) in res:
            res[func(s)].append(s)
        else:
            res[func(s)]=[s]
    return res

def doGroup2(func,seqs):
    return doGroup(seqs,func)

def doCopy(files,dest,dirs=0):
    if type(files)==type([]):
        if dirs==0:
            for f in files:
                if os.path.exists(f) and os.path.isdir(f):
                    #dest aqui debe ser un directorio
                    shutil.copy2(f,dest + '/' + os.path.basename(f))
                else:
                    shutil.copy2(f,dest)
        else:
            for f in files:
                if os.path.exists(f) and os.path.isdir(f):
                    shutil.copytree(f,dest)
    else:
        if dirs==0:
            if os.path.exists(files) and os.path.isfile(files):
                #Crear dest si no existe
                if not os.path.exists(dest):
                    open(dest,'w').close()
                    shutil.copy2(files,dest)
                else:
                    if os.path.exists(dest) and os.path.isdir(dest):
                        shutil.copy2(files,dest + '/' + os.path.basename(files))
                    else:
                        shutil.copy2(files,dest)
        else:
            if os.path.exists(files) and os.path.isdir(files):
                shutil.copytree(files,dest)

def doDelete(files,dirs=0):
    if type(files)==type([]):
        if dirs==0:
            for f in files:
                if os.path.exists(f) and os.path.isfile(f):
                    shutil.rmtree(f)
        else:
            for f in files:
                if os.path.exists(f) and os.path.isdir(f):
                    shutil.rmtree(f)
    else:
        if dirs==0:
            if os.path.exists(files) and os.path.isfile(files):
                shutil.rmtree(files)
        else:
            if os.path.exists(files) and os.path.isdir(files):
                shutil.rmtree(files)


#Funcion de utilidad que lee un archivo de texto o una url
#Si getlines es 1, se devuelve como lista de lineas
def getPathText(path,getlines=0,encoding='utf-8',errors='replace'):
    if path.lower().find('http://')==0 or path.lower().find('https://')==0:
        if getlines==0:
            #Esto devuelve bytes, hay que convertir en str??????
            #return urllib.request.urlopen(path).read()
            return requests.get(path).text
        else:
            #return urllib.request.urlopen(path).read().split('\r\n') 
            return requests.get(path).text.split('\r\n') 
    else:
        if getlines==0:
            if os.path.exists(path) and os.path.isfile(path):
                return open(path,'r',encoding=encoding,errors=errors).read()
            else:
                return path
        else:
            if os.path.exists(path) and os.path.isfile(path):
                return open(path,'r').readlines()
            else:
                return path

def getPathTextBinary(path):
    if path.lower().find('http://')==0:
        return urllib.request.urlopen(path).read()
    else:
        if os.path.exists(path) and os.path.isfile(path):
            return open(path,'rb').read()
        else:
            return path

def getBinaryChunk(path,start,end):
    if os.path.exists(path) and os.path.isfile(path):
        f=open(path,'rb')
        f.seek(start)
        if start!=0:
            return f.read(end-start)
        else:
            return f.read(start)
    else:
        return 0

def appendBinaryChunk(path,bytes):
    if os.path.exists(path) and os.path.isfile(path):
        f=open(path,'ab+')
        f.write(bytes)
        return len(bytes)

#Nuevo soporte para html
import pprint #quitar esto
def _html(selector,source):
    #Buscar el mejor parser disponible
    parser= "lxml" if "lxml" in sys.modules else "html.parser"
    #print("html parser: %s" %parser)
    parts= selector.strip().split(',')
    #print("parts: %s"%parts)
    html=bs4.BeautifulSoup(source,parser)
    #print('html: %s'%html)
    if parts==[]:
        return []
    resul=[]
    #Cada parte puede ser un solo elemento(la mayoria) o varios(p div a)
    for part in parts:
        #print("procesando part: %s"%part)
        #print("resul aqui: %s"%resul)
        #print(' ' in part)
        if not ' ' in part: #Procesar un item no jerarquico
            #print("por el if")
            resul.append(list(filter(lambda x: x!=[] ,_flat(html.findAll(part)))))
            #print("resul aqui: %s"%resul)
        else:
            #print("por el else")
            childs=part.split(' ')
            #print("childs: %s"%childs)
            resul=list(filter(lambda x:x!=[],_flat(html.findAll(childs[0]))))
            #print("resul aqui: %s"%resul)
            for item in childs[1:]:
                #print("procesando item: %s"%item)
                resul= list(filter(lambda x: x!=[],_flat([x.findAll(item) for x in resul])))
                #print("resul en el for: %s"%resul)
            #pprint.pprint(resul)
            #pprint.pprint(_flat(resul))
    return _flat(resul)
    #return resul


if __name__=='__main__':
    html_doc = """
 <html><head><title>The Dormouse's story</title></head>
 <p class="title"><b>The Dormouse's story</b></p>
 <p class="story">Once upon a time there were three little sisters; and their names were
 <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
 <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
 <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
 and they lived at the bottom of a well.</p>
 <p class="story">...</p>
 """
    print(_html("p a", html_doc))
    print("-----------------------")
    #print(_html("title", html_doc)[0].string)
    print(_html("title", html_doc))
    print("-----------------------")
    print(_html("title,a", html_doc))
    print("-----------------------")


