#-----------------------------------------------------------------
#   Utilidades para control de tipos y Python tipado en runtime
#-----------------------------------------------------------------

import sys
from typing import *


#Soporte para clases anonimas tipo registro----------------------------------------------
#Deberia ser inmutable?????
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
                        ) -> str:
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
    install : bool  --- Si es True, se instala la clase en globals() y es
                        instanciable. Si es True y file es distinto de "",
                        no se copia en el archivo.
    
    ### Valor de Retorno
  
    str --- Cadena de texto con el código generado.
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
        exec(typedTupleStr,globals())
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
                        ) -> str:
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
  
    str --- Cadena de texto con el código generado.
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
        exec(typedRegisterStr,globals())
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
                        ) -> str:
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
  
    str --- Cadena de texto con el código generado.
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
        exec(typedUnionStr,globals())
    else:
        if file != "":
            f = open(file,"w")
            f.write(typedUnionStr)
            f.close()        
    return typedUnionStr



#---------------------------------------------------------------------------------------------------------------------------------------




if __name__ == '__main__':

    r = anonymObjectFactory(a=90,b=80,c='tralari',square=lambda x : x*x)
    rp = anonymObjectFactory(**{'a':90,'b':80,'c':'tralari','square' : lambda x : x*x})
    print(r)
    print(r.c)
    print(r.square(9))
    print(rp)
    print(rp.c)
    #Classfactory
    def Rob_init(self, name):
        self.name = name

    Robot2 = classFactory("Robot2", 
              (), 
              {"counter":0, 
               "__init__": Rob_init,
               "sayHello": lambda self: "Hi, I am " + self.name})
    print(Robot2)
    bob = Robot2("Bob")
    bob.sayHello()
    #Pruebas de typed tuples
    tpl = typedTuplesFactory("IntStr",["intfld","strfld"],["int",'str'],file = "IntStr.py",install=True)
    print(tpl)
    #compile(tpl, "<string>" ,"exec")
    #exec(tpl,globals())
    tpl2 = IntStr(666,"arrepienetete")
    print(tpl2.intfld)
    print(tpl2.strfld)
    print(len(tpl2))
    for item in tpl2:
        print(item)
    print(tpl2[0])
    print(tpl2[1])
    print('----------------------')
    union = typedUnionFactory("IntOrStr",["intval","strval"],["int","str"],file ="IntOrStr.py",install = True)
    print(union)
    union1 = IntOrStr(989)
    print(union1)
    print(union1.type)
    print(union1.strval)
    print(union1.intval)
    print('----------------------')
    reg = typedRegisterFactory("PersonReg",["name","age","alive"],["str","int","bool"],file="PersonReg.py",install = True)
    reg1 = PersonReg(name = "Paco",age = 32,alive = True)
    print(reg1)
    print(reg1.name)
    print(reg1.age)
    print(reg1.alive)
    print(reg1.keys())
    print(reg1.values())