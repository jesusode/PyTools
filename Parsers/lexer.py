import re
import pprint
from collections import deque
from typing import *


class Token:
    '''
    Clase que representa un Token.
    ------------------------------
    Modificarlo para que si se pasa la cadena fuente, no guarde value sino que lo coja de ella
    (mas rapido y menos consumo de memoria)
    '''
    def __init__(self,id="",type="undefined",value=None):
        self.id=id
        self.type=type
        self.value=value
        self.lin=0
        self.col=0
    
    #Representacion como cadena
    def toString(self):
        return f"<Token -> type: {self.type}, value: {self.value} >"
    
    #solo python
    def __repr__(self): 
        return self.toString()

    #Para que funcione con set(). Si no, cada instancia es diferente
    #y se repiten.
    def __hash__(self):
        return hash((self.type,self.value))

    #Para ==
    def __eq__(self,other):
        if not isinstance(other, type(self)): return NotImplemented
        if self.type == other.type and self.value == other.value:
            return True
        else:
            return False
    
    
#Funcion factoria de Tokens
def tokenFactory(type,value,id=""):
    return Token(id,type,value)


#Mejoras: deberia poder soportar varias tablas que se pueden activar/desactivar usando una pila
#Sistema de canales de ANTLR
#Implementar iterable
class Lexer:
    '''
    Lexer controlado por tabla
    --------------------------
    La tabla es una lista de listas con la siguiente
    estructura:
    [[regex,fun or None,ignore]...]
    '''
    def __init__(self): #,toklist=[]):
        #self.toklist=[]
        self.__current=None
        self.__input=""
        self.__index=0
        #Por defecto no se elimina el espacio en blanco
        self.__whitespace=False
        self.__table={}
        self.__curline=0
        self.__curpos=0
        self.__toignore=[]
        self.stack= deque()
        self.lookahead_memo = {}

    def setInput(self, inp):
        self.__input=inp
        self.__index=0

    def getInput(self):
        return self.__input

    def setIgnore(self,ign_lst):
        self.__toignore=ign_lst

    def getIgnore(self):
        return self.__toignore

    def getRest(self):
        return self.__input[self.__index:]

    def isEOF(self):
        if self.__index > len(self.__input) :
            return True
        else:
            return False
    
    def setIndex(self,idx):
        self.__index=idx

    def getIndex(self):
        return self.__index

    def ignoreWhitespace(self,tf):
        assert tf in [True,False]
        self.__whitespace=tf

    #table={"name": [regex,token_type,optional fun(match),ignore]}
    def setTable(self,table):
        self.__table=table
        #meter los tipos de Token a ignorar en toignore
        for item in self.__table: 
            if item[3]==True : 
                self.__toignore.append(item[1])
        
    #print("self.__toignore: " + _tostring(self.__toignore))

    def nextToken(self,expected=None,ignore_nomatch=False):
        '''
        Si expected se pasa, lo encuentra o excepcion.
        Si ignore_nomatch es True, sigue avanzando e ignorando
        la enrada hasta encontrar un match o EOF.
        '''
        #print("En lexx.nextToken buscando: " + str(expected))
        self.__current=self.__next(expected,ignore_nomatch)
        return self.__current
    #No hay control de linea:pos!!!!!

    def __next(self,expected=None,ignore_nomatch=False):
        assert self.__table!=[]
        #print(f"EXPECTED:{expected}")
        fn = None #None por defecto
        if self.__input=="" or self.__index==len(self.__input) :
            #print("Devolviendo EOF")
            t=Token(type="EOF",value="EOF")
            #Si se ha pasado expected, comprobar que el tipo corresponde con el pasado
            if expected!=None and t.type!=expected :
                raise Exception(f"Lexer Error: Se esperaba un Token de tipo {expected} y se ha encontrado {t.type}")
            return t
        
        #Quitar posible blancos al comienzo
        #cont=0
        if self.__whitespace==True :
            self.__input=self.__input.strip()
        
        for item in self.__table:
            kind=item[1]
            #print(kind)
            #print(repr(self.__input))
            #Cambio para permitir ejecutar codigo en los matches(una funcion que acepta el match)
            fn=item[2]
            #print("buscando: " + item[0])
            #print("en: " + repr(self.__input[self.__index:50]))
            if self.__whitespace==True :
                #print("QUITANDO WHITESTPACE")
                self.__input=self.__input.strip()#.strip("\n")
            
            rest=self.__input[self.__index:]
            #if rest=="" : return None 
            if rest == "" : return Token(type="EOF",value="EOF")
            m=re.search(item[0],rest,re.MULTILINE)
            if m and m.start()==0 :
                val=rest[m.start():m.end()]
                #print("Encontrado: " + val)
                #Actualizar indice
                self.__index= self.__index + m.end()
                t= Token(type=kind,value=val)
                #print(f"encontrado: {t}")
                #si es uno de los tokens a ignorar,continuar
                #print(t,t.type in self.__toignore)
                if t.type in self.__toignore : 
                    #print(f"ignorando token: {t}")
                    continue 
                #Si se ha pasado expected, comprobar que el tipo corresponde con el pasado
                if expected!=None and t.type!=expected :
                    raise Exception(f"Error: Se esperaba un Token de tipo {expected} y se ha encontrado {t.type}")
                
                #self.toklist.append(t)

                #Cambio para aprovechar item[2]----------------------------------------------------
                #-Si es callable, la llamamos con el Token encontrado.
                #-Si es una lista, usarla como nueva tabla de tokens.
                #-Si es 'pop', sacar la ultima tabla de la pila y usarla.
                if fn!=None :
                    if callable(fn) :
                        fn(val)
                    else:
                        if type(fn)==list :
                            self.changeTable(fn)
                        else:
                            if fn== "pop" :
                                self.popTable()
                            else:
                                raise Exception("Error: no es una funcion ni una lista ni 'pop'")
                #------------------------------------------------------------------------------------
                return t
        #cont++
        #if cont==20 : break 
        if ignore_nomatch == False:
            raise Exception("Invalid input value: no Token match.")
        else:
            self.__index+=1 
            return self.__next(expected,ignore_nomatch)


    def lookahead(self,n):
        '''
        Obtiene una lista de los n siguientes tokens
        sin avanzar el puntero a la cadena fuente.
        Cacheable.
        '''
        #Hacer una copia de self.__index para luego recuperarlo
        old= self.__index
        #print("old en lookahead: " + old)

        #Este cache debe ser configurable!!!!!!!!!
        #Poner un mecanismo para borrarla si crece mucho!!
        #Usar cache si procede???--------------------------------------
        if (self.__index + n,n) in self.lookahead_memo :
            #print(f"====> USANDO CACHE EN LOKAHEAD: {self.lookahead_memo[(self.__index + n,n)]} <====") 
            return self.lookahead_memo[(self.__index + n,n)]

        #print("resto en lookahead: " + _sublist(self.__input,self.__index,40))
        #print("Esto es lookahead------------------------------------")
        toks_seen=[]
        try:
            for i in range(n):
                nxt=self.nextToken()
                #print(f"nxt en lookahead: {nxt}")
                #if nxt!=None :
                if nxt!= Token(type="EOF",value="EOF") :
                    toks_seen.append(nxt)
        except:
            toks_seen=[]
        
        #Guardar memo del ultimo par indice,n visto??-------------
        if toks_seen != []:
            self.lookahead_memo[(self.__index,n)] = toks_seen[:]
        #---------------------------------------------------------
        
        self.__index=old
        #print("index recuperado en lookahead: " + self.__index)
        #print("resto despues de lookahead: " + _sublist(self.__input,self.__index,40))
        #print("fin de llokahead---------------------------------------")
        return toks_seen


    def tokenize(self,input : str,ignore_nomatch : bool =False):
        tokens=[]
        self.setInput(input)
        while True:
            t = self.nextToken(ignore_nomatch = ignore_nomatch)
            tokens.append(t)
            if t.type=="EOF" : break 
        return tokens


    def changeTable(self,newtable):
        self.stack.append(self.table)
        self.__table= newtable


    def popTable(self):
        self.__table=self.stack.pop()
