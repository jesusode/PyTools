#Utilidades para manejar gramaticas

import re
from typing import *


import syntaxanaltable

from collections import deque

import pprint

def _sublist(s,b,e=None):
    if e:
        return s[b:e]
    else:
        return s[b:]


def _count(el,seq): 
    return list(seq).count(el)



#Reformar esto para manejar otros simbolos aparte de las mayusculas
def isValidSymbol(symbol : str) -> bool: #?????????????
    '''
    function isValidSymbol
    '''
    if re.match ("^\(((([A-Z])+\s?)|(([a-z])+\s?))+\)\*$",symbol):
        return True
    else:
        if re.match("^[A-Z\+\-\*/]+$",symbol): #terminales
            return True
        else:
            if re.match("^[a-z]+$",symbol): #No terminales
                return True
            else:
                return False

def isTerminal(symbol : str) -> bool:
    if re.match("^[A-Z]+$",symbol): 
        return True
    else:
        return False

def isNonTerminal(symbol : str) ->bool:
    if re.match("^[a-z]+$",symbol): #No terminales
        return True
    else:
        return False

def isClosure(symbol : str) -> bool:
    if symbol.strip() in ["+","*","?"]:
        return True
    else:
        return False

def getClosureParts(cls : list) -> list:
        cls=_sublist(cls,1,-2)
        return list(map(lambda x : x.strip(),cls.split(" ")))



class GrammarRule:

    def __init__(self,id,lhs,rhs,priority=0):
        self.id=id
        self.lhs=lhs
        self.rhs= list(filter(lambda x: x !="",rhs))
        self.priority=priority
        self.options=[]
        self.getOptions()
        #print(self.toString())


    def getOptions(self):
        if not "|" in self.rhs: return []
        self.options= list(map(lambda x: x.strip().split(" ")," ".join(self.rhs).split("|")))
        return self.options


    def hasOptions(self):
        if self.options==[]:
            return False
        else:
            return True


    def toString(self):
        return "<<GrammarRule. id: {0}\n LHS: {1},\nRHS: {2},\n Priority: {3},\n Options: {4}\n >>".format(self.id,self.lhs,self.rhs,self.priority,self.options)


    def toText(self):
        return "{0} : {1}\n".format(self.lhs," ".join(self.rhs))



#No admite reglas multiples, especificarlas como opciones
class Grammar:
    def __init__(self,name,rules,start_symbol,empty_symbol):
        self.name=name
        self.rules=rules
        #print("self.rules en GRAMMAR: " + _tostring(self.rules))
        self.terminals= set()
        self.nonterminals= set()
        self.rules_by_id={}
        self.rules_by_lhs={}
        self.empty_symbol=empty_symbol
        self.nullable_rules=[]
        self.firsts={}
        self.follows={}
        #assert isValidSymbol(empty_symbol)
        start_symbol= start_symbol.strip()
        #assert isValidSymbol(start_symbol)
        self.start_symbol=start_symbol
        #Buscar conjuntos de terminales y no terminales
        for rule in self.rules:
            self.rules_by_id[rule.id]=rule
            self.rules_by_lhs[rule.lhs]=rule
            self.nonterminals.add(rule.lhs)
            for item in rule.rhs:
                #if isValidSymbol(item):
                if isTerminal(item):
                    self.terminals.add(item)
                if isNonTerminal(item) or isClosure(item):
                    self.nonterminals.add(item)

            #Aprovechamos para buscar las que tienen empty como produccion o como una opcion
            if rule.rhs==[self.empty_symbol]:
                self.nullable_rules.append(rule)
            if rule.options!=[]:
                for opt in rule.options:
                    if self.empty_symbol in opt:
                        self.nullable_rules.append(rule)
                        break

        assert self.start_symbol in self.nonterminals
        d= self.findDuplicates()
        #print(f"duplicates: {d}")
        if d!=[]:
            raise Exception("Error: Hay reglas duplicadas en la gramatica:\n {0} \nDeben combinarse para que no se repitan.".format("\n".join((map(lambda x :x.toText(),d)))))

        print(map(lambda x:x.toString(), self.nullable_rules))
        #Calcular el conjunto de primeros para todos los simbolos de la gramatica#
        self.calcFirsts()
        pprint.pprint(self.firsts)
        #Calcular el conjunto de siguientes para los no terminales de la gramatica
        self.calcFollows()
        pprint.pprint(self.follows)


    def isNullable(self,symbol):
        return True if symbol in map(lambda x:x.lhs, self.nullable_rules) else False


    def findLeftRecursiveRules(self): #busca : x: xby
        return list(map(lambda y : y.toString(), filter(lambda x : x.lhs==x.rhs[0],self.rules)))

    def findRightRecursiveRules(self): #busca : x: abx
        return list(map(lambda y :y.toString(),filter(lambda x: x.lhs==x.rhs[-1],self.rules)))

    def findDuplicates(self):
        lhss= map(lambda x :x.lhs, self.rules)
        f=filter(lambda y :y[0]>1, list(map(lambda x : [_count(x,lhss),x],lhss)))
        s= set()
        s.update(list(map(lambda x:x[1],f)))
        return list(filter(lambda x : x.lhs in s, self.rules))

    
    def calcFirsts(self):
        for sym in self.terminals:
            self.findFirsts(sym)

        for sym in self.nonterminals:
            if sym==self.empty_symbol: continue
            self.findFirsts(sym)


    #esto debe manejar los closures: (xyz)* 
    def findFirsts(self,symbol): #
        #assert isValidSymbol(symbol)
        #print("ENTRANDO A FINDFIRST CON SYMBOL: " + symbol)
        #Primero comprobar que no exista ya----------
        if symbol in self.firsts.keys():
            #print("-->Devolviendo desde el cache")
            return self.firsts[symbol]
        #--------------------------------------------
        #print("clave inexistente en firsts")
        firsts= set()
        maxnullables=0
        nullables=0
        #assert (symbol in self.terminals) or (symbol in self.nonterminals)
        #PRIM(eps)={eps}.Regla 0
        if symbol==self.empty_symbol:
            firsts.add(self.empty_symbol)
        #PRIM(terminal)={terminal}.Regla 1
        if symbol in self.terminals:
            firsts.add(symbol)
        #PRIM(no terminal) con produccion s->eps: meter empty.Regla 2
        if symbol in self.nonterminals and symbol in self.rules_by_lhs.keys():
            if self.rules_by_lhs[symbol].hasOptions():
                #print("Regla con opciones: proceder para cada opcion!!")
                for option in self.rules_by_lhs[symbol].options:
                    print("Mirando option: " + str(option))
                    for sym in option:
                        #print("Mirando simbolo de opcion: " + sym)
                        #Si terminal: meterlo y parar
                        if sym==self.empty_symbol:
                            firsts.add(sym)
                            break
                        if sym in self.terminals:
                            firsts.add(sym)
                            break
                        else: 
                            #Si [no terminal con opcion vacia], hacer union con primeros(sym) y seguir. Si no, parar
                            if sym in map(lambda x :x.lhs,self.nullable_rules):
                                #print("LLAMADA RECURSIVA!!!")
                                firsts=firsts.union(self.findFirsts(sym))
                            else:
                                #Si hay una regla con lhs =sym y un primer rhs terminal, cogerlo
                                #print("Probando primer rhs no terminal!!!")
                                #print( "hay una regla que coincide en lhs" if sym in _keys(self.rules_by_lhs) else "no coincide ningun lhs")
                                #print( "el primer simbolo de rhs es terminal" if self.rules_by_lhs[sym].rhs[0] in self.getTerminals() else "el primer simbolo de rhs es no terminal")
                                #print(self.rules_by_lhs[sym].rhs[0])
                                if sym in self.rules_by_lhs.keys() and self.rules_by_lhs[sym].rhs[0] in self.getTerminals():
                                    firsts=firsts.union(self.findFirsts(sym))
                                    #print(firsts)
                                #print("BREAK!!!")
                                break
                    #print("Terminamos con opcion: " + _tostring(option))
                #Si firsts contiene el simbolo vacio, sacarlo si ninguna de las opciones es anulable directamente
                if self.empty_symbol in firsts:
                    #print("FIRSTS CONTIENE EL SIMBOLO VACIO. REVISANDO SI REGLA ES NULLABLE")
                    #print("symbol: " + symbol)
                    #print(_tostring(self.isNullable(symbol)))
                    if not self.isNullable(symbol):
                        firsts.delete(self.empty_symbol)
            else:
                maxnullables= len(self.rules_by_lhs[symbol].rhs)
                #print("maxnullables en el ciclo: " + maxnullables)
                cont=0
                for sym in self.rules_by_lhs[symbol].rhs:
                    #Si terminal: meterlo y parar
                    #print("Mirando simbolo sin opcion : " + sym)
                    if sym in self.terminals:
                        firsts.add(sym)
                        break
                    else:
                        #Si es no terminal y es el primero, usarlo. Regla 3.
                        #Si [no terminal con opcion vacia], hacer union con primeros(sym) y seguir. Si no, parar
                        if cont==0 or sym in map(lambda x :x.lhs, self.nullable_rules):
                            firsts=firsts.union(self.findFirsts(sym))
                            if cont==0: break
                            #print("valor de nullables : " + nullables)
                            nullables+=1
                        else:
                            #Si hay una regla con lhs =sym y un primer rhs terminal, cogerlo
                            if sym in self.rules_by_lhs.keys() and self.rules_by_lhs[sym].rhs[0] in self.getTerminals():
                                firsts=firsts.union(self.findFirsts(sym))
                                #print(firsts)
                            #print("BREAK!!!")
                            break
                        cont+=1
            #end
            #print("Firsts al salir: " + firsts.toString())
            #Aqui ultimo paso: revisar si hay que meter o no el simbolo vacio
            #ESTO ESTA MAL!!!!!!!!!!!!
            if nullables!=0 and nullables==maxnullables:
                #print("maxnullables: " + maxnullables)
                #print("nullables: " + nullables)
                firsts.add(self.empty_symbol)
                #print("Metiendo simbolo vacio porque todas las opciones son nullables")
        #Guardar lo calculado
        self.firsts[symbol]=firsts
        return firsts

    def calcFollows(self):
        #inicializar conjuntos de siguientes
        for sym in self.nonterminals:
            if sym==self.empty_symbol: continue
            self.follows[sym]= set()
            if sym==self.start_symbol:
                self.follows[sym].add("$")
        #Reglas para siguientes:
        #    (Regla 2) a->alfa b beta  => meter en sig(b) first(beta) sin empty
        #    (Reglas 3 y 4) a->alfa b o bien a-> alfa b beta y primeros(beta) tiene empty
        #    => meter en sig(b) los elementos de sig(a)
        for sym in self.nonterminals:
            if sym==self.empty_symbol: continue
            for rule in self.rules:
                if rule.hasOptions():
                #coger todos los que queden en la opcion y meter los primeros siempre que sean anulables
                    for opt in rule.getOptions():
                        if sym in opt:
                            print( "{0} esta en {1} en {2}".format(sym,str(opt),opt.index(sym)))
                            #Implementamos regla 2
                            pos=opt.index(sym)
                            if pos!= len(opt)-1:
                                toconsider= opt[pos+1:]
                                print("Resto a considerar: " + str(toconsider))
                                nullcont=0
                                for item in toconsider:
                                    print("item considerado: " + item)
                                    print(self.isNullable(item))
                                    print(toconsider.index(item))
                                    self.follows[sym]=self.follows[sym].union(self.firsts[item])
                                    if self.empty_symbol in self.follows[sym]:
                                        self.follows[sym].remove(self.empty_symbol)
                                    print("Ejecutada union con " + str(self.firsts[item]))
                                    if self.isNullable(item): nullcont+=1
                                #Implementacion de Regla 4: todos los primeros de beta son nullables
                                if nullcont== len(toconsider):
                                    self.follows[sym]= self.follows[sym].union(self.follows[rule.lhs])
                                    print("Ejecutada union con rule.lhs: {0} segun regla 4!!".format(rule.lhs))
                            else:
                                print("Codigo para cuando coincide en la ultima posicion!!!")
                                #Implementacion de Regla 3(esto asume que existe follows[rule.lhs])
                                self.follows[sym]=self.follows[sym].union(self.follows[rule.lhs])
                                print("Ejecutada union con follows[rule.lhs]:{0} ".format(rule.lhs + str(self.follows[rule.lhs])))

                else:
                    if sym in rule.rhs:
                        print("{0} esta en {1} sin opciones en {2}".format(sym,str(rule.rhs),rule.rhs.index(sym)))
                        print("hay que implementar lo mismo que para cuando hay opciones!!!!")
                        print("{0} esta en {1} en {2}".format(sym,str(rule.rhs),rule.rhs.index(sym)))
                        #Implementamos regla 2
                        pos= rule.rhs.index(sym)
                        if pos!=len(rule.rhs)-1:
                            toconsider2= rule.rhs[pos+1:]
                            print("Resto a considerar: " + str(toconsider2))
                            nullcont2=0
                            for item in toconsider2:
                                print("item considerado: " + item)
                                print(self.isNullable(item))
                                print(toconsider2.index(item))
                                self.follows[sym]=self.follows[sym].union(self.firsts[item])
                                if self.empty_symbol in self.follows[sym]:
                                    self.follows[sym].delete(self.empty_symbol)
                                print("Ejecutada union2 con " + str(self.firsts[item]))
                                if self.isNullable(item): nullcont2+=1
                            #Implementacion de Regla 4: todos los primeros de beta son nullables
                            if nullcont2== len(toconsider2):
                                self.follows[sym]= self.follows[sym].union(self.follows[rule.lhs])
                                print("Ejecutada union2 con rule.lhs: {0} segun regla 4!!".format(rule.lhs))
                        else:
                            print("Codigo para cuando coincide en la ultima posicion!!!")
                            #Implementacion de Regla 3(esto asume que existe follows[rule.lhs])
                            self.follows[sym]=self.follows[sym].union(self.follows[rule.lhs])
                            print("Ejecutada union2 con follows[rule.lhs]:{0} ".format(rule.lhs) + str(self.follows[rule.lhs]))
        return self.follows


    def toString(self):
        rulelst= map(lambda x : x.toString(),self.rules)
        return "<<Grammar {0}.\nStart Symbol: {1}\nTerminals: {2}.\nNon Terminals: {3}\n Rules:\n {4}.\nView:\n{5} >>".format(self.name,self.start_symbol,str(self.terminals),str(self.nonterminals),"\n".join(rulelst),"\n".join(map(lambda x : str(x.id) + ". " + x.toText(),self.rules)))


    def getTerminals(self):
        return self.terminals


    def getNonTerminals(self):
        return self.nonterminals


    def getNullableRules(self):
        return self.nullable_rules



def buildGrammar(source,name,start_symbol,empty="empty"):
    '''
    Construye una gramatica asumiendo que
    cada línea contiene una regla.
    Necesita un nombre para ella y un símbolo
    de comienzo.
    '''
    rules=source.strip().split("\n")
    print("RULES: " + str(rules))
    ruleset=[]
    cont=1
    for rule in rules:
        parts= rule.split(":")
        print("parts: " + str(parts))
        ruleset.append(GrammarRule(cont,parts[0].strip(),map (lambda x : x.strip(),parts[1].split(" ")),0))
        cont+=1
    return Grammar(name,ruleset,start_symbol,empty)


#Pruebas
gsource="""
expr : expr * expr | expr + expr | value
value : INT
"""
#print(isValidSymbol("expr"))
#print(isValidSymbol("(term EXPR)*"))
print(getClosureParts("(term expr DOT PLUS)*"))
print("--------------------------")
g=buildGrammar(gsource,"gramatica1","expr")
print(g.toString())

print("Terminales: " + str(g.terminals))
print("No Terminales: " + str(g.nonterminals))
print("LeftRecursives: "  + str(g.findLeftRecursiveRules()))
'''
print(isTerminal("INT"))
print(isTerminal("K"))
print(isNonTerminal("expr"))
print(isNonTerminal("JJGGGC"))
'''
print("--------------------------")
gsource2="""
exp : exp PLUS term | term | empty
term : term TIMES factor | factor
factor : ID | NUM | LPAREN exp RPAREN | empty
"""
gsource2="""
exp : term expprime | empty
expprime :  PLUS term expprime
term : factor termprime | empty
termprime :  TIMES factor termprime
factor : LPAREN exp RPAREN | ID
"""
gsource2="""
exp : term expprime
expprime :  PLUS term expprime | empty
term : factor termprime
termprime :  TIMES factor termprime | empty
factor : LPAREN exp RPAREN | ID
"""
gsource2="""
a : a A | b c d
b : B | empty
c : C | empty
d : D | c E
"""

'''
#g2=buildGrammar(gsource2,"gramatica2","exp")
g2=buildGrammar(gsource2,"gramatica2","a")
#g2=buildGrammar(gsource2,"gramatica2","exp")
print(g2.getNullableRules())
print(g2.toString())
print("--------------------------------------")
print("Terminales: " + str(g2.terminals))
print("--------------------------------------")
print("No Terminales: " + str(g2.nonterminals))
print("--------------------------------------")
print("LeftRecursives: "  + str(g2.findLeftRecursiveRules()))
print("--------------------------------------")
print("Nullable Rules: "  + str(map(lambda x :x.toString(),g2.getNullableRules())))
print("--------------------------------------")
print("Duplicate Rules: "  + str(map(lambda x : x.toString(),g2.findDuplicates())))
print("--------------------------------------")
print(g2.rules[0].toText())
tanal= syntaxanaltable.SyntaxAnalTable(g2.getNonTerminals(),g2.getTerminals())
pprint.pprint(tanal.table)
print(tanal.lookup("exp","PLUS"))
tanal.entry("exp","PLUS","tralari")
pprint.pprint(tanal.table)
print(tanal.lookup("exp","PLUS"))
print("--------------------------------------")
print(g2.findFirsts("PLUS"))
print("--------------------------------------")
print("Primeros de exp")
print("--------------------------------------")
print(g2.findFirsts("exp"))
print("--------------------------------------")
print("Primeros de expprime")
print("--------------------------------------")
print(g2.findFirsts("expprime"))
print("--------------------------------------")
print("Primeros de term")
print("--------------------------------------")
print(g2.findFirsts("term"))
print("--------------------------------------")
print("Primeros de termprime")
print("--------------------------------------")
print(g2.findFirsts("termprime"))
print("--------------------------------------")
print("Primeros de factor")
print("--------------------------------------")
print(g2.findFirsts("factor"))
'''

print("OK")