import sys
from typing import *
from types import FunctionType,CodeType
import io #Para StringIO en Python 3+


def importCode(code:str, name : str, add_to_sys_modules : bool = False) -> CodeType:
    """ Code can be any object containing code -string, file object, or
       compiled code object-. Returns a new module object initialized
       by dynamically importing the given code and optionally adds it
       to sys.modules under the given name.
    """
    import imp
    module = imp.new_module(name)

    if add_to_sys_modules:
        import sys
        sys.modules[name] = module
    exec(code,module.__dict__)

    return module

#Factoria para @dataclass??????

#Soporte para clases anonimas tipo registro----------------------------------------------
class anonym(object):
    def __init__(self,**fields):
        for item in fields:
            setattr(self,item,fields[item])
    def __repr__(self):
        return ">>anonym object: %s"  %self.__dict__

def anonymObjectFactory(**fields):
    return anonym(**fields)
#----------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------
#Creador de clases dinamicas
def classFactory(classname : str,bases : Tuple,attributes : Dict[str,Any]) -> type:
    '''
    Envoltorio sobre type()
    '''
    return type(classname,bases,attributes)

#Funcion que mete metodos como si fueran de instancia de clase
def addMethodsToClassOrInstance(instance,methods):
    for method in methods:
        setattr(instance,method.__name__,method)
    return instance

#----------------------------------------------------------------------------------------


#Crean variables en modulos de Python----------------------------------------------
#import pprint
def installVars(mod_name,seq,*_vars):
    this=sys.modules[mod_name]
    for i in range(len(_vars)):
        if not _vars[i] in this.__dict__:
            setattr(this, _vars[i], seq[i])
    return True

def installVars2(mod_name,seq,h,t):
    this=sys.modules[mod_name]
    if not h in this.__dict__:
        setattr(this, h, seq[0])
    if not t in this.__dict__:
        setattr(this, t, seq[1:])
    return True
#-----------------------------------cls--------------------------------------------------

#Class template factory---------------------------------------------------------------------------------

#Permitir tambien versiones mutables de las tres!!!!!!!

typed_tuple_template='''
from typecheckers import *
class %%name%%:
    def __init__(self,*values):
        object.__setattr__(self,"_cont",0)
        object.__setattr__(self,"types_",%%types%%)
        object.__setattr__(self,"names",%%fnames%%)
        object.__setattr__(self,"conditions",%%conditions%%)
        object.__setattr__(self,"elems",{})
        object.__setattr__(self,"elems_list",[])
        #Precondiciones
        assert(len(%%types%%) == len(%%fnames%%))
        assert(len(values) == len(%%fnames%%))
        for i in range(len(%%types%%)):
            if isinstance(self.types_[i],TypeChecker):
                if not self.types_[i].checkType(values[i]):
                    raise Exception("Type Error in class %s: expected %s , found %s"%(self.__class__.__name__,self.types_[i],type(values[i])))
            else:
                ensureType(values[i],self.types_[i],cond_fun=self.conditions[i] if self.conditions!=[] else None)
            self.elems[self.names[i]]=[values[i],self.types_[i]]
            self.elems_list.append(values[i])
    def __setattr__(self,name,value):
        if name == "_cont":
            #Hay que hacerlo asi para evitar problemas de recursion
            object.__setattr__(self,"_cont",value) 
        else:
            raise Exception("Error: Can't set attribute '%s' in class %s."%(name,self.__class__.__name__))
    def __getattr__(self,name):
        if name in self.names:
            return self.elems[name][0]
        else:
            raise Exception("Error: Can't get attribute '%s' in class %s"%(name,self.__class__.__name__))
    #Protocolo para acceso por posicion----------------------
    def __len__(self):
        return len(self.elems)

    def __getitem__(self, key):
        if type(key) in [int,float]:
            if int(key)>=0 and int(key) < len(self.elems_list):
                return self.elems_list[key]
            else:
                raise Exception('Error: invalid position for attribute')
        else:
            raise Exception('Error: index for access must be numeric')

    def __setitem__(self, key, value):
        raise Exception("Error: can't set items in a typed tuple class. Typed tuples are inmutable.")

    def __delitem__(self, key):
        raise Exception("Error: can't delete items in a typed tuple class. Typed tuples are inmutable.")
    
    #Protocolo de iterador
    def __iter__(self):
        return self

    def __next__(self):
        if self._cont < len(self.elems):
            self._cont += 1
            return self.elems_list[self._cont-1]
        else:
            raise StopIteration

'''

def typedTuplesFactory(name : str,
                        fnames : List[str],
                        _types : List[str],
                        conditions : List[Callable[[Any],bool]] = [],
                        file: str = "",
                        install = False
                        ) -> Any: #str|code
    '''
    Crea una plantilla que contiene el código de una clase
    que representa una tupla de elementos con tipo.
    La tupla es iterable y sus elementos se pueden acceder
    por nombre o por posición.

    ### Argumentos
    
    name : str     --- Nombre que tendrá la clase
    fnames : List[str]  --- Lista de nombres de los campos
    _types : List[str]   --- Lista de tipos de los campos
    conditions : List[Callable[[any],bool]] --- lista de predicados
                 para control fino de los tipos.
    file : str  --- Archivo donde copiar el código generado.
    install : bool  --- Si es True, se instala la clase en un module
                        de nombre name y es instanciable desde el.
                        Si es True y file es distinto de "",
                        no se copia en el archivo.
    
    ### Valor de Retorno
  
    str | Code --- Cadena de texto o módulo con el código generado.
    '''
    typedTupleStr = typed_tuple_template
    typedTupleStr = typedTupleStr.replace("%%name%%",name)
    typedTupleStr = typedTupleStr.replace("%%fnames%%",str(fnames))
    typedTupleStr = typedTupleStr.replace("%%types%%",str(_types).replace("'","").replace('"',"")) 
    if conditions != []:
            typedTupleStr = typedTupleStr.replace("%%conditions%%",str(conditions))
    else:
            typedTupleStr = typedTupleStr.replace("%%conditions%%","[]")
    if install == True:
        return importCode(typedTupleStr,name)
    else:
        if file != "":
            f = open(file,"w")
            f.write(typedTupleStr)
            f.close()        
    return typedTupleStr


typed_register_template='''
from typecheckers import *
class %%name%%:
    def __init__(self,**values):
        object.__setattr__(self,"types_",%%types%%)
        object.__setattr__(self,"names",%%fnames%%)
        object.__setattr__(self,"elems",{})
        object.__setattr__(self,"conditions",%%conditions%%)
        for i in range(len(%%types%%)):
            if isinstance(self.types_[i],TypeChecker):
                if not self.types_[i].checkType(values[self.names[i]]):
                    raise Exception("Type Error in class %s: expected %s , found %s"%(self.__class__.__name__,self.types_[i],type(values[self.names[i]])))
            else:
                ensureType(values[self.names[i]],self.types_[i],cond_fun=self.conditions[i] if self.conditions != [] else None)
            self.elems[self.names[i]]=[values[self.names[i]],self.types_[i]]
    def __setattr__(self,name,value):
        raise Exception("Error: Can't set attribute '%s' in class %s."%(name,self.__class__.__name__))
    def __getattr__(self,name):
        if name in self.names:
            return self.elems[name][0]
        else:
            raise Exception("Error: Can't get attribute '%s' in class %s"%(name,self.__class__.__name__))
    def keys(self):
        return self.names
    def values(self):
        return [x[0] for x in self.elems.values()]
'''

def typedRegisterFactory(name : str,
                        fnames : List[str],
                        _types : List[str],
                        conditions : List[Callable[[Any],bool]] = [],
                        file: str = "",
                        install = False
                        ) -> Any: #str | code
    '''
    Crea una plantilla que contiene el código de una clase
    que representa una registro inmutable de elementos con tipo.

    ### Argumentos
    
    name : str     --- Nombre que tendrá la clase
    fnames : List[str]  --- Lista de nombres de los campos
    _types : List[str]   --- Lista de tipos de los campos
    conditions : List[Callable[[any],bool]] --- lista de predicados
                 para control fino de los tipos.
    file : str  --- Archivo donde copiar el código generado.
    install : bool  --- Si es True, se instala la clase en globals() y es
                        instanciable. Si es True y file es distinto de "",
                        no se copia en el archivo.
    
    ### Valor de Retorno
  
    str | code --- Cadena de texto o módulo con el código generado.
    '''
    typedRegisterStr = typed_register_template
    typedRegisterStr = typedRegisterStr.replace("%%name%%",name)
    typedRegisterStr = typedRegisterStr.replace("%%fnames%%",str(fnames))
    typedRegisterStr = typedRegisterStr.replace("%%types%%",str(_types).replace("'","").replace('"',"")) 
    if conditions != []:
            typedRegisterStr = typedRegisterStr.replace("%%conditions%%",str(conditions))
    else:
            typedRegisterStr = typedRegisterStr.replace("%%conditions%%","[]")
    if install == True:
        return importCode(typedRegisterStr,name)
    else:
        if file != "":
            f = open(file,"w")
            f.write(typedRegisterStr)
            f.close()        
    return typedRegisterStr




typed_union_template='''
from typecheckers import *
class %%name%%:
    def __init__(self,value):
        object.__setattr__(self,"types_",%%types%%)
        object.__setattr__(self,"names",%%fnames%%)
        object.__setattr__(self,"elems",{})
        object.__setattr__(self,"type",type(None))
        object.__setattr__(self,"conditions",%%conditions%%)
        #any is not allowed as type or value
        if any in self.types_:
            raise Exception("Error: class %s don't permit any as type."%self.__class__.__name__)
        if type(value)==any:
            raise Exception("Error: class %s don't permit values of type."%self.__class__.__name__)
        found=False
        cont=0
        for typ in self.types_:
            if isinstance(typ,TypeChecker):
                if typ.checkType(value):
                    found=True
                    object.__setattr__(self,"type",typ)
                    break
            else:
                if type(value)==typ:
                    if self.conditions != [] and self.conditions[cont]!=None:
                        if self.conditions[cont](value)!=True:
                            raise Exception('Error: Condition function failed for value %s'%value)
                        else:
                            found=True
                            object.__setattr__(self,"type",typ)
                            break 
                    else:
                        found=True
                        object.__setattr__(self,"type",typ)
                        break 
            cont+=1
        if found==False: #No se ha encontrado el tipo.Excepcion
            raise Exception("Type Error in class %s: Expected types %s in value %s. Found type %s" %(%%name%%,' or '.join([str(x) for x in %%types%%]),str(value),type(value)))
        for i in range(len(%%types%%)):
            #if type(value)==self.types_[i]:
            if self.type==self.types_[i]:
                self.elems[self.names[i]]=[value,self.types_[i]]
                #Hay que usar object.__setattr para que no se meta en __setattr__
                #object.__setattr__(self,"type_",self.types_[i])
            else:
                self.elems[self.names[i]]=[None,self.types_[i]]
    def __setattr__(self,name,value):
        raise Exception("Error: Can't set attribute '%s' in class %s."%(name,self.__class__.__name__))
    def __getattr__(self,name):
        if name in self.names:
            return self.elems[name][0]
        else:
            raise Exception("Error: Can't get attribute '%s' in class %s"%(name,self.__class__.__name__))
'''

def typedUnionFactory(name : str,
                        fnames : List[str],
                        _types : List[str],
                        conditions : List[Callable[[Any],bool]] = [],
                        file: str = "",
                        install = False
                        ) -> Any: #str | code
    '''
    Crea una plantilla que contiene el código de una clase
    que representa una unión inmutable de elementos con tipo.

    ### Argumentos
    
    name : str     --- Nombre que tendrá la clase
    fnames : List[str]  --- Lista de nombres de los campos
    _types : List[str]   --- Lista de tipos de los campos
    conditions : List[Callable[[any],bool]] --- lista de predicados
                 para control fino de los tipos.
    file : str  --- Archivo donde copiar el código generado.
    install : bool  --- Si es True, se instala la clase en globals() y es
                        instanciable. Si es True y file es distinto de "",
                        no se copia en el archivo.
    
    ### Valor de Retorno
  
    str | code --- Cadena de texto o módulo con el código generado.
    '''
    typedUnionStr = typed_union_template
    typedUnionStr = typedUnionStr.replace("%%name%%",name)
    typedUnionStr = typedUnionStr.replace("%%fnames%%",str(fnames))
    typedUnionStr = typedUnionStr.replace("%%types%%",str(_types).replace("'","").replace('"',"")) 
    if conditions != []:
            typedUnionStr = typedUnionStr.replace("%%conditions%%",str(conditions))
    else:
            typedUnionStr = typedUnionStr.replace("%%conditions%%","[]")
    if install == True:
        return importCode(typedUnionStr,name)
    else:
        if file != "":
            f = open(file,"w")
            f.write(typedUnionStr)
            f.close()        
    return typedUnionStr



#Compila texto a codigo y devuelve un objeto ejecutable
def pyCompile(code) -> CodeType:
    '''
    Envoltorio simple sobre compile. Compila el texto
    contenido en code a codigo Python ejecutable por
    exec.
    '''
    return compile(code, "<string>" ,"exec")


#Crea funciones a partir de texto en runtime
def dynFunFactory(name,code,context={}) -> FunctionType:
    '''
    Compila code a una funcion que se puede ejecutar directamente
    en el codigo. Se le asignará name a la propiedad __name__ de la misma.
    Si se pasa context, se usará en vez de globals() para buscar los nombres
    de las variables no locales en ella.
    '''
    _code = compile(code, "<string>", "exec")
    return FunctionType(_code.co_consts[0], globals(), name)

def switchFactory(values : str,options : str,default : str ='') -> CodeType:
    '''
    Crea codigo dinamico para convertir una lista de condiciones, otra de
    opciones y un valor por defecto en un objeto de codigo if-elif-else
    que se compilará, creando un especie de switch para Python.
    '''
    assert(len(values) == len(options))

    switch_str :io.StringIO = io.StringIO()
    for i  in range(len(options)):
        if i==0:
            switch_str.write('if ' + values[i] + ': \n\t' + options[i] + "\n")
        else:
             switch_str.write('elif ' +  values[i] + ' : \n\t' + options[i] + "\n")
    if default!='':
        switch_str.write('else:\n\t' +  default)
    return compile(switch_str.getvalue(),"<string>","exec")


def switchFunFactory(varname : str,values : str,options : str,default : str ='') -> FunctionType:
    '''
    Crea codigo dinamico para convertir una lista de condiciones, otra de
    opciones y un valor por defecto en una funcion if-elif-else
    que se compilará, creando un especie de switch para Python.
    '''
    assert(len(values) == len(options))

    switch_str :io.StringIO = io.StringIO()
    switch_str.write("def switch_" + varname + '(' + varname + '):\n')
    for i  in range(len(options)):
        if i==0:
            switch_str.write('\tif ' + values[i] + ': \n\t\t' + options[i] + "\n")
        else:
             switch_str.write('\telif ' +  values[i] + ' : \n\t\t' + options[i] + "\n")
    if default!='':
        switch_str.write('\telse:\n\t\t' +  default)
    return dynFunFactory("switch_" + varname,switch_str.getvalue())