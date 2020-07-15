#-----------------------------------------------------------------
#   Utilidades para control de tipos y Python tipado en runtime
#-----------------------------------------------------------------

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