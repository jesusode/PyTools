
#GLOBALES

from typing import *

#Flag que indica que estamos probando las reglas
__TRYING : bool =True

def isTrying():
    'Devuelve el valor de __TRYING'
    return __TRYING

def setTrying(value : bool) -> bool:
    'Cambia el valor de __TRYING'
    global __TRYING
    __TRYING = value
    return __TRYING

#Tabla para los caches de cada regla
__MEMOS_TABLE : Dict[str,Dict[int,bool]] = {}

def addToMemos(rule_name):
    'Mete una regla en memos'
    global __MEMOS_TABLE
    if not rule_name in __MEMOS_TABLE:
        __MEMOS_TABLE[rule_name] = {}

def getMemos():
    'Devuelve __MEMOS_TABLE'
    return __MEMOS_TABLE

def memoize(rule_name : str, pos:int, success : bool) -> None:
    'Guarda la posicion en la que se invoco la regla la ultima vez y si se consiguió ejecutarla.'
    global __MEMOS_TABLE
    if rule_name in __MEMOS_TABLE:
        __MEMOS_TABLE[rule_name][pos] = success

def alreadyParsed(rule_name: str,pos:int) -> Union[bool,None]:
    'Doc'
    global __MEMOS_TABLE
    if pos in __MEMOS_TABLE[rule_name]:
        return __MEMOS_TABLE[rule_name][pos]
    else:
        return None




import lexer
from taglist import *

lexx = lexer.Lexer()

_table= [
    ["\\s+","WHITESPACES",None,False],
    ["\\+|\\-","PLUSMIN",None,False],
    ["\\*|/","TIMESDIV",None,False],
    ["\\^","EXP",None,False],
    ["\(","LPAREN",None,False],
    ["\)","RPAREN",None,False],
    ["\[","LBRACK",None,False],
    ["\]","RBRACK",None,False],
    ["\{","LCURLY",None,False],
    ["\}","RCURLY",None,False],
    ["[0-9]+","NUMBER",None,False],
    [",","COMMA",None,False],
    [":","COLON",None,False],
    ["\\.","DOT",None,False],
    ["and","AND",None,False],
    ["or","OR",None,False],
    ["not","NOT",None,False],
    ["<=|>=|>|<|==|!=<|>","BOOLOP",None,False],
    ["[a-zA-Z_][a-zA-Z_0-9]*(\\.[a-zA-Z0-9_]+)*","ID",None,False],
    ['''\\"[^\\"]+\\"''',"STRING",None,False],
    [";","SEMI",None,False]
]




lexx.setTable(_table)

#Codigo de inicio de usuario

import re
import sys
import io


#Codigo de callbacks


#Codigo del parser
addToMemos('prog')



def prog():
    #Obtener el indice de la entrada para backtrack
    _index = lexx.getIndex()
    _success = alreadyParsed('prog',_index)
    #Si no estamos probando y success es True, ejecutarla
    if _success == True:
        if not isTrying():
            _resul = _prog()
            return _resul
        else:
            print("Using cache for rule prog true")
            return            
    elif _success == False:
        #Si ya se ha visto,
        print("Using cache for rule prog false")
        #return
        raise Exception(f"Yet parsed rule prog at index {_index} without success")
    else:
        try:
            print("Trying rule prog")
            _prog()
            _success = True
        except:
            #Rewind
            print("Failed parsing of rule prog: Backtrack")
            _success = False
        finally:
            print("Memoizing rule prog with success: " + str(_success))
            memoize('prog',_index,_success)
            print(getMemos())
            return

def _prog():

    '''
    prog : ( sentence {{print("Code repetitivo")}} ) +
    '''
    prog_values = TagList('prog')
    if isTrying():
        expr()
    else:
        prog_values.append(expr())
        print("Code repetitivo")
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF':
        prog_values.append(expr())
        print("Code repetitivo")
    return prog_values
addToMemos('sentence')



def sentence():
    #Obtener el indice de la entrada para backtrack
    _index = lexx.getIndex()
    _success = alreadyParsed('sentence',_index)
    #Si no estamos probando y success es True, ejecutarla
    if _success == True:
        if not isTrying():
            _resul = _sentence()
            return _resul
        else:
            print("Using cache for rule sentence true")
            return            
    elif _success == False:
        #Si ya se ha visto,
        print("Using cache for rule sentence false")
        return
    else:
        try:
            print("Trying rule sentence")
            _sentence()
            _success = True
        except:
            #Rewind
            print("Failed parsing of rule sentence: Backtrack")
            _success = False
        finally:
            print("Memoizing rule sentence with success: " + str(_success))
            memoize('sentence',_index,_success)
            print(getMemos())
            return

def _sentence():

    '''
    sentence : | ( expr SEMI ) | ( expr DOT )
    '''
    sentence_values = TagList('sentence')
    try:
        if isTrying():
                expr()
                lexx.nextToken('SEMI')
                return
        else:
                sentence_values.append(expr())
                sentence_values.append(lexx.nextToken('SEMI'))
                return sentence_values
    except:
        pass
    try:
        if isTrying():
                expr()
                lexx.nextToken('DOT')
                return
        else:
                sentence_values.append(expr())
                sentence_values.append(lexx.nextToken('DOT'))
                return sentence_values
    except:
        pass
        return sentence_values
addToMemos('expr')



def expr():
    #Obtener el indice de la entrada para backtrack
    _index = lexx.getIndex()
    _success = alreadyParsed('expr',_index)
    #Si no estamos probando y success es True, ejecutarla
    if _success == True:
        if not isTrying():
            print(f"Ejecutando expr con _index: {_index}")
            _resul = _expr()
            return _resul
        else:
            print("Using cache for rule expr true")
            return            
    elif _success == False:
        #Si ya se ha visto,
        print("Using cache for rule expr false")
        #return
        raise Exception(f"Yet parsed rule expr at {_index} without success")
    else:
        try:
            print("Trying rule expr")
            _expr()
            _success = True
        except:
            #Rewind
            print("Failed parsing of rule expr: Backtrack")
            _success = False
        finally:
            print("Memoizing rule expr with success: " + str(_success))
            memoize('expr',_index,_success)
            print(getMemos())
            return

def _expr():

    '''
    expr : NUMBER PLUSMIN NUMBER DOT
    '''
    expr_values = TagList('expr')
    if isTrying():
        lexx.nextToken('NUMBER')
        lexx.nextToken('PLUSMIN')
        lexx.nextToken('NUMBER')
        lexx.nextToken('DOT')
        return
    else:
        expr_values.append(lexx.nextToken('NUMBER'))
        expr_values.append(lexx.nextToken('PLUSMIN'))
        expr_values.append(lexx.nextToken('NUMBER'))
        expr_values.append(lexx.nextToken('DOT'))
        return expr_values


#Codigo de usuario


def startPackrat():
    'Inicia la cadena de try'
    setTrying(True)
    prog()
    print("-----Try completado----------")
    if alreadyParsed("prog",0) in [None,False]:
        raise Exception("Error: el parser no puede reconocer la entrada!!")
    else:
        setTrying(False)
        lexx.setIndex(0)
        return prog()



import pprint
if __name__ == '__main__':
    input = "56-9098.4444+090908.200+3.4-5."
    lexx.setInput(input)
    #pprint.pprint(boolexp())
    print(startPackrat())


