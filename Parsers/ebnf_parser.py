'''
--------------------------------------------------------------------------------------------
Parser para gramaticas descritas en una forma similar a la EBNF
--------------------------------------------------------------------------------------------

grammar : COMMENT? GRAMMAR nonterm ignore? discard? CALLBACK? ALL? CODE? tokens rule+ CODE? END
tokens  : COMMENT? TOKENS (terminal ARROW STRING)+ END
discard : DISCARD (terminal)+ END
rule (PARAMS CODE)? (RETURNS CODE)? :   COMMENT? nonterm COLON CODE? elem+ CODE? SEMI
elem :   terminal
       | nonterm
       | options 
       | group
       | empty
options : ( PIPE elem CODE?)+
group : LPAREN (elem)+  extra_tokens_checks? CODE? RPAREN closure CODE?
closure : MULT | PLUS | QUESTION | empty
extra_token_checks : LBRACK (terminal)+ RBRACK

NOTA: empty es un token, optional no admite empty como elem

TOKENS: ID,LPAREN,RPAREN,LBRACK,RBRACK,MULT,PLUS,COLON,GRAMMAR,TOKENS,
        DISCARD,END,CODE,TREE,ARROW,COMMENT,LOOKAHEAD,RETURNS,PARAMS,empty
Admite gramaticas LL(k). El parser calcula el Lookahead necesario.
Notas: En options, TODAS las opciones deben ir como group.
---------------------------------------------------------------------------------------------
'''

'''
PENDIENTE:

- MECANISMO DE IMPORTACION DE OTRAS GRAMATICAS (COMO Y QUE)
- POSIBILIDAD DE CREAR UN VISITOR PARA EL ARBOL??
- QUITAR CODE DE LOS DOCSTRINGS
- SEPARAR EL CODIGO EN VARIOS MODULOS

'''

__version__ = 1.0

import lexer
import io
from typing import *


#Funciones auxiliares

from flat import flat

from dictutils import groupby,multiGroup
import syntaxanaltable

def indent(code,indent = ""):
    val=''
    for it in code.split('\n'):
        val+=indent + it + '\n'
    return val

#Template para parsers
parser_template = '''
import lexer
from taglist import *

lexx = lexer.Lexer()

_table= %%tokens%%

%%to_ignore%%

lexx.setTable(_table)

#Codigo de inicio de usuario
%%user_init_code%%

#Codigo de callbacks
%%callbacks_code%%

#Codigo del parser
%%parser_code%%

#Codigo de usuario
%%user_end_code%%

'''

callbacks_template='''
def on_{0}_{1}({2}):
    #Put your code here
    print("{0}ing {1} with %s" % {2})
    return {2}

'''

callbacks_code= io.StringIO()


tok = None
lexx = lexer.Lexer()

#lookahead a 1 por defecto.
LA=1
#lista de [exp_reg,type,callback_func,ignore]
#La expresion regular funciona para los comentarios tipo C (sacada de internet)
table=[
    ["\s+","WHITESPACE",None,True],
    ["\(","lparen",None,False],
    ["\)","rparen",None,False],
    ["\[","lbrack",None,False],
    ["\]","rbrack",None,False],
    ["\*","mult",None,False],
    ["\+","plus",None,False],
    ["\?","question",None,False],
    [":","colon",None,False],
    [";","semi",None,False],
    [",","comma",None,False],
    ["\|","pipe",None,False],
    ["\->","arrow",None,False],
    ["empty","empty",None,False],
    ["\\bgrammar\\b","grammar",None,False],
    ["tokens","tokens",None,False],
    ["ignore","ignore",None,False],
    ["discard","discard",None,False],
    ["callbacks","callbacks",None,False],
    ["all","all",None,False],
    ["\\bend\\b","end",None,False],
    ["params","params",None,False],
    ["returns","returns",None,False],
    ["lookahead\s+[0-9]+","lookahead",None,False], #?????
    ["/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/","comment",None,False],
    #["/[^/]+/","regexp",None,False],
    ["<re>.+?</re>","regexp",None,False],
    ["[a-z][a-z_0-9]+","nonterm",None,False],
    ["[A-Z]+","terminal",None,False],
    #["{{.+?}}","code",None,False],
    ["{{[\s\S]+?}}","code",None,False],
    ["\^<[^\>]+>","tree",None,False]
]

lexx.setTable(table)

#Info global
ebnf_tree = []
toklist = []
gram_id = ""



#Parser con acciones 
# grammar : GRAMMAR nonterm tokens rule+ END
def grammar():
    global lexx,LA,ebnf_tree,toklist,gram_id,callbacks
    pre_code = ""
    post_code=""
    toks_to_discard = []
    toks_to_ignore = []
    #Flag para construir callbacks de E/S de reglas------
    callbacks = False #Por defecto, no.
    callbacks_all = False
    #----------------------------------------------------
    #print("Entrando a grammar")

    #Coger comentario de entrada si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment":
        #print("Comment:")
        c = lexx.nextToken("comment")
        #print(c)

    lexx.nextToken("grammar")
    gram_id=lexx.nextToken("nonterm").value


    #Ver si hay tokens a ignorar por el lexer
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="ignore":
        toks_to_ignore = ignore()

    #Ver si hay tokens a descartar para las listas que genera el parser
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="discard":
        toks_to_discard = discard()
        print(f"DISCARD:{toks_to_discard}")

    #Ver si hay que construir callbacks
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="callbacks":
        lexx.nextToken("callbacks")
        callbacks = True

    #Ver si hay que construir callbacks
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="all":
        lexx.nextToken("all")
        callbacks_all = True

    #Coger pre_code si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code":
        pre_code = lexx.nextToken("code")

    #Coger comentario antes de tokens si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment":
        #print("Comment antes de tokens:")
        c = lexx.nextToken("comment")
        #print(c)

    #coger tokens
    toklist = tokens()

    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type not in ["end","code"]:
        ebnf_tree.append(rule())

    #Coger post_code si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code":
        post_code = lexx.nextToken("code")

    lexx.nextToken("end")
    return [gram_id,toklist,ebnf_tree,pre_code,post_code,toks_to_ignore,toks_to_discard,callbacks,callbacks_all]


# IGNORE (terminal|nonterm)+ END ?????????
def ignore():
    global lexx
    toks_to_ignore = []
    lexx.nextToken("ignore")
    toks_to_ignore.append("'" + lexx.nextToken("terminal").value + "'")
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="end":
        toks_to_ignore.append("'" + lexx.nextToken("terminal").value + "'")
    lexx.nextToken("end")
    return toks_to_ignore


# DISCARD (terminal)+ END
def discard():
    global lexx
    toks_to_discard = []
    lexx.nextToken("discard")
    toks_to_discard.append(lexx.nextToken("terminal").value)
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="end":
        toks_to_discard.append(lexx.nextToken("terminal").value)
    lexx.nextToken("end")
    return toks_to_discard

# tokens  : (terminal ARROW STRING)+ END
def tokens():
    global lexx
    toks="[\n"
    lexx.nextToken("tokens")
    while lexx.lookahead(3)!=[] and lexx.lookahead(1)[0].type!="end":
        t="\"" +  lexx.nextToken("terminal").value + "\""
        lexx.nextToken("arrow")
        s= lexx.nextToken("regexp").value
        #toks= toks + margin + "[" + _tostring(s.replace("/","\"")) + "," + t + ",None,False],\n"
        toks= toks + "    " + "[" + str(s.replace("<re>",("\"" if not "\"" in s else "'''")).replace("</re>",("\"" if not "\"" in s else "'''"))) + "," + t + ",None,False],\n"
    toks=toks.strip().strip(",") + "\n]\n"
    lexx.nextToken("end")
    #print("TOKENS definidos: " + toks)
    #raise Exception("Parada temporal")
    return toks

# rule :  nonterm [(nonterm)+] COLON elem+ SEMI
def rule():
    global lexx
    rule_items=[]
    #Coger comentario si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment":
        #print("Rule Comment:")
        c = lexx.nextToken("comment")
        #print(c)
    #print("Buscando un no terminal...")
    id=lexx.nextToken("nonterm")
    rule_items.append(id)

    #Coger parametros de la regla si los hay
    if lexx.lookahead(2)!=[] and lexx.lookahead(1)[0].type=="params":
        rule_items.append(lexx.nextToken("params"))
        rule_items.append(lexx.nextToken("code"))

    #Coger codigo de retorno de la regla si lo hay
    if lexx.lookahead(2)!=[] and lexx.lookahead(1)[0].type=="returns":
        rule_items.append(lexx.nextToken("returns"))
        rule_items.append(lexx.nextToken("code"))

    print("\n--->PROCESANDO REGLA: "  + id.value)

    #print("Buscando un colon...")
    #rule_items.append(lexx.nextToken("colon"))
    lexx.nextToken("colon")

    #Coger codigo preproceso si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code":
        rule_items.append(lexx.nextToken("code"))

    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="semi":
        rule_items.append(elem())

    #Coger codigo postproceso si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code":
        rule_items.append(lexx.nextToken("code"))

    lexx.nextToken("semi")

    print("\n--->TERMINADA REGLA: "  + id.value)
    return rule_items


# elem : terminal | nonterm | options  | groupet | empty
def elem():
    global lexx

    #print(f"LOOKAHEAD 1 en elem: {lexx.lookahead(1)[0]}")

    if lexx.lookahead(1)[0].type == "lparen":
        #print("Yendo por group")
        return group()

    elif lexx.lookahead(1)[0].type == "pipe":
        #print("Yendo por options")
        return options()

    elif lexx.lookahead(1)[0].type == "nonterm":
        #print("Yendo por nonterm")
        return  lexx.nextToken("nonterm")

    elif lexx.lookahead(1)[0].type == "terminal":
        #print("Yendo por terminal")
        return lexx.nextToken("terminal")

    elif lexx.lookahead(1)[0].type == "code":
        #print("Yendo por code")
        return lexx.nextToken("code")

    elif lexx.lookahead(1)[0].type == "lbrack":
        #print("Yendo por extra_tokens_check")
        return extra_tokens_check()

    else:
        #print("Yendo por empty")
        return lexx.nextToken("empty")

#Working
def options():
    global lexx
    options_els=[]
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="EOF" and lexx.lookahead(1)[0].type in ["pipe","code"]:
        #Cambio para coger el code final si lo hay
        nxt = lexx.nextToken()
        #print(f"VALOR DE NEXT: {nxt}")
        options_els.append(nxt)
        if nxt.type == "code": break
        options_els.append(elem())
    return options_els     

# group : LPAREN elem+ RPAREN closure
def group():
    global lexx
    group_els = []
    #print("Entrando a group")
    group_els.append(lexx.nextToken("lparen"))
    #Coger el valor del primer token si es no terminal
    #que servira para poder procesar el groupet sin que llegue al final de manera incorrecta**/
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="EOF" and lexx.lookahead(1)[0].type not in ["rparen","code"]:
        group_els.append(elem())

    #mirar si hay tokens extra a comprobar para el lookahead
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="lbrack":
        group_els.append(elem())

    #Coger code si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code":
        group_els.append(lexx.nextToken("code"))

    group_els.append(lexx.nextToken("rparen"))

    #Mirar si es closure
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="EOF":
        cls = closure()
        if type(cls) == lexer.Token:
            group_els.append(cls)

    #Coger code final si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code":
        group_els.append(lexx.nextToken("code"))
    #print(f"GROUP_ELS:{group_els}")
    return group_els


def extra_tokens_check():
    #mirar si hay tokens extra a comprobar para el lookahead
    toks_extra = []
    if lexx.lookahead(1)!=[]:
        toks_extra.append(lexx.nextToken())
        while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="EOF" and lexx.lookahead(1)[0].type=="terminal":
            toks_extra.append(elem())  
        #Asegurarse de que se cierra la lista
        toks_extra.append(lexx.nextToken("rbrack"))
    #print(f"toks_extra: {toks_extra}")
    return toks_extra


#MULT | PLUS | QUESTION | empty
def closure():
    global lexx
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="EOF" and lexx.lookahead(1)[0].type in ["mult","plus","question","empty"]:
        return lexx.nextToken()
    else:
        return ""

def empty():
    return ""

