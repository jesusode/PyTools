'''
--------------------------------------------------------------------------------------------
Parser para gramaticas descritas en una forma similar a la EBNF
Crea un parser para la gramatica descrita
--------------------------------------------------------------------------------------------

grammar : [COMMENT] GRAMMAR nonterm tokens ignore [LOOKAHEAD] [CODE] rule+ END
tokens  : [COMMENT] TOKENS (terminal ARROW STRING)+ END
ignore :  [COMMENT] IGNORE (terminal)* END
discard : DISCARD (terminal)* END
rule :    [COMMENT] nonterm [(nonterm)+] [ RETURNS nonterm]  COLON
        [ CODE ] elem+  [ CODE ] [ TREE ] SEMI
elem : terminal code tree 
       | nonterm code tree 
       | optional code tree 
       | options code tree 
       | groupet code tree | empty
optional : LBRACK elem RBRACK
options : ( PIPE elem)+ 
groupet : LPAREN (elem)+ RPAREN closure #Deberia ir code tree aqui?????
closure : MULT | PLUS | empty

NOTA: empty es un token, optional no admite empty como elem

TOKENS: ID,LPAREN,RPAREN,LBRACK,RBRACK,MULT,PLUS,COLON,GRAMMAR,TOKENS,
        IGNORE,END,CODE,TREE,ARROW,COMMENT,LOOKAHEAD,RETURNS,empty
Admite gramaticas LL(k).

Permite que las reglas, de manera opcional, tengan parametros de llamada.

Permite que las reglas, de manera opcional,devuelvan un valor.

Informa de errores de lookahead.(?)

Admite un comentario tipo C antes de grammar,tokens,ignore y antes de cada regla. 
  Fuera de estas localizaciones, un comentario genera un error.
---------------------------------------------------------------------------------------------
'''

import lexer
import simple_ast
import sys

import  pprint

from typing import *
import functools
import re
import io

#Funciones auxiliares

def _indent(code):
    indent="    "
    indented=""
    for item in code.split("\n"):
        indented= indented + indent + item + "\n"

    #indented= indented + "\n"
    return indented

def _checkLeftRecursive(rule,options):
    for item in options:
        if options[0][0][0].value==rule:
            raise f"Error: la regla {rule} es recursiva por la izquierda"


def _primeros3(options):
    assert type(options)==type([])
    assert type(options[0])==type([])
    #range= 0 to len(options)
    primeros=[]
    first_valid=None
    #considerar primero que options sea una sola opcion o dos, con una siendo empty
    #en ese caso devolver el primer terminal o no terminal de la no empty
    #print("OPTIONS EN PRIMEROS3: ")
    #pprint.pprint(options)
    #print("---------------------------------------")
    #first_valid x[0] o x[1]
    primeros= list(map(lambda x: [(x[0][0].value if x[0][0].value!="(" else x[0][1].value),
                    (x[0] if x[0][0].value!="(" else  x[0][1:-1]),
                        len(x[0]), #Esto se usa para algo?????????
                        0,
                        x[-1],
                        0],options))
    #Calcular el numero de no terminales reales en las opciones,
    #ignorando los que puedan estar en grupetos(tb en optionals????)
    tmp=list(map(lambda x:x[1],primeros))
    for j in range(len(tmp)):
        #print("cambio de item......")
        cont=0
        offset=0
        ignore=False
        for i in range(len(tmp[j])):
            #print("Viendo token: " + _tostring(tmp[j][i]))
            if tmp[j][i].value=="(":
                ignore=True
                i+=1#Python no admite bucle for!!
                continue
            if tmp[j][i].value==")":
                ignore=False
                i+=1#Python no admite bucle for!!
                continue
            if tmp[j][i].type=="nonterm" and ignore==False:
                cont+=1
            #else
                if primeros[j][-1]==0:
                    #print("PONIENDO OFFSET a " + i)
                    primeros[j][-1]=i
        #print("Valor de cont: " + cont)
        primeros[j][3]=cont
        #print(primeros[j])
    #pprint.pprint(primeros)
    if len(options)==1:
        raise Exception("Error: Una opcion debe tener al menos dos alternativas.")
    return primeros	



def _histogram(seq):
    hist = {}
    def f(a):
        if a in hist:
            hist[a]+=1
        else:
            hist[a]=1
    list(map(f,seq))
    return hist

tok = None
lexx = lexer.Lexer()
#lookahead a 1 por defecto.
LA=1
margin="    "
comments=[]
rules_parts=[]
rule_items=[]
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
    [":","colon",None,False],
    [";","semi",None,False],
    [",","comma",None,False],
    ["\|","pipe",None,False],
    ["\->","arrow",None,False],
    ["empty","empty",None,False],
    ["grammar","grammar",None,False],
    ["tokens","tokens",None,False],
    ["ignore","ignore",None,False],
    ["discard","discard",None,False],
    ["end","end",None,False],
    ["returns","returns",None,False],
    ["lookahead\s+[0-9]+","lookahead",None,False],
    ["/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/","comment",None,False],
    #["/[^/]+/","regexp",None,False],
    ["<re>.+?</re>","regexp",None,False],
    ["[a-z][a-z_0-9]+","nonterm",None,False],
    ["[A-Z]+","terminal",None,False],
    #["{{.+?}}","code",None,False],
    ["{{[\s\S]+?}}","code",None,False],
    ["\^<[^\>]+>","tree",None,False]

]
#Tabla de info de reglas y no terminales
rule_info={}
lexx.setTable(table)
cur_rule=""
memos=[]
callback_str=""
groupet_first=""
groupet_last=""
discard_list=[]

#------------------------------------------------------------------------
#Opciones configurables directivas de linea de comandos
#-callb: construir funciones de callback al entrar y salir de cada regla
#-stree: construir un arbol sintactico
#-info: generar traza de lo que va haciendo el parser
#-------------------------------------------------------------------------
build_callback=0
if "-callb" in sys.argv:
    build_callback=1

build_syntax_tree=0#????????
if "-stree" in sys.argv:
    build_syntax_tree=1

build_debug_info=1
if "-info" in sys.argv:
    build_debug_info=1


parser_report="" #log de lo que ha hecho el parser
#    l=[gram_id,toklist,str(ignore_toks),parser,pre_code,post_code,memo_str,"begin\n" + callback_str + "\nendsec\n" if build_callback==1 else ""]
parser_template="""
#Grammar {0}

import stack
import parserskit
#Funciones auxiliares para parsers con bactracking y memoizing

def clear_memos():
    global memos
    memos={6}

def _alreadyParsed(memo,pos):
    if pos in memo.keys():
        return memo[pos]
    else:
        return None

def _memoize(memo,start,stop):
    global memos
    print("Memos antes de _memoize: " + str(memos))
    memo[start]=stop
    print("Memos despues de _memoize: " + str(memos))


memos={6}
lexx = Lexer()
_AST = None
_stack = Stack()
#Tokens table
table={1}
lexx.setTable(table)
ignore_list={2}
lexx.setIgnore(ignore_list)

#start code for on_enter,on_exit rules
{7} 
#end code for on_enter,on_exit rules

#start pre_code
{4} 
#end pre_code


{3}


#start post_code
{5}
#end post_code

print("Put your code here")
"""

rule_template="""
def {0}({1}):
    {0}_values=[]
    {2}
    """

callback_template_enter="""
def on_enter_{0}(rule_values):
    global lexx
    {1}
    print("REST: " + lexx.getRest())
    """
callback_template_exit="""
def on_exit_{0}(rule_values):
    global lexx
    {1}
    print("REST: " + lexx.getRest())
    """

#Parser con acciones 
# grammar : GRAMMAR nonterm tokens ignore [LOOKAHEAD] [CODE] rule+ END
def grammar():
    global lexx,parser_template,rule_info,LA,comments,memos,rules_parts,discard_list,build_callback
    parser=""
    pre_code=""
    post_code=""
    _tree=""
    memo_str=""
    print("Entrando a grammar")
    #print(f"lokahead : {lexx.lookahead(1)}")
    #raise Exception("PARADA TEMPORAL")
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment": 
        comments.append(lexx.nextToken("comment").value)

    lexx.nextToken("grammar")
    gram_id=lexx.nextToken("nonterm").value
    toklist=tokens()
    ignore_toks=ignore()
    #Coger lista de tokens a no meter en las listas de las reglas si la hay-------
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="discard": 
        discard_list=discard()

    #------------------------------------------------------------------------------
    #Coger lookahead si se ha definido
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="lookahead": 
        LA = LA + int(lexx.nextToken("lookahead").value.split(" ")[1])
        print("--->LOOKAHEAD PUESTO A: " + str(LA))#ESTO SE USA?????????

    #Garantizamos 2 al menos (corresponde a 1, pero options tiene en cuenta
    #los pipes al calcular los indices de las opciones
    if LA < 2: LA=2
    #Coger codigo de entrada o inicializacion si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
        #pre_code=_indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
        pre_code= lexx.nextToken("code").value.strip("{{").strip("}}")

    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="end":
        parser= parser + rule()

    lexx.nextToken("end")
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment": 
        comments.append(lexx.nextToken("comment").value)

    #Coger codigo de salida si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
        #post_code=_indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
        post_code= lexx.nextToken("code").value.strip("{{").strip("}}")

    #Crear la cadena para memos
    memo_str= "{" + ",".join(memos) + "}\n"
    l=[gram_id,toklist,str(ignore_toks),parser,pre_code,post_code,memo_str,"\n" + callback_str + "\n" if build_callback==1 else ""]
    #print("\n\n\n=========================")
    #print("COMENTARIOS: " + _tostring(comments))
    #print("Partes de las reglas: " + str(rules_parts))
    #print(format parser_template with l)
    #raise Exception("Parada temporal!!")
    return parser_template.format(*l)

# tokens  : (terminal ARROW STRING)+ END
def tokens():
    global lexx,comments,margin
    toks="[\n"
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment": 
        comments.append(lexx.nextToken("comment").value)
    lexx.nextToken("tokens")
    while lexx.lookahead(3)!=[] and lexx.lookahead(1)[0].type!="end":
        t="\"" +  lexx.nextToken("terminal").value + "\""
        lexx.nextToken("arrow")
        s= lexx.nextToken("regexp").value
        #toks= toks + margin + "[" + _tostring(s.replace("/","\"")) + "," + t + ",None,False],\n"
        toks= toks + margin + "[" + str(s.replace("<re>","\"").replace("</re>","\"")) + "," + t + ",None,False],\n"
    toks=toks.strip().strip(",") + "\n]\n"
    lexx.nextToken("end")
    #print("TOKENS definidos: " + toks)
    #raise Exception("Parada temporal")
    return toks

# ignore : IGNORE (terminal)* END
def ignore():
    global lexx,comments
    ignore_list=[] 
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment": 
        comments.append(lexx.nextToken("comment").value)
    lexx.nextToken("ignore")
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="end":
        #Asegurarse de que son comillas dobles y no simples!!!
        ignore_list.append("\"" + str(lexx.nextToken("terminal").value).replace("'","\"") + "\"")
    lexx.nextToken("end")
    return ignore_list

# ignore : DISCARD (terminal)* END
def discard():
    global lexx,comments
    to_discard=[] 
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment": 
        comments.append(lexx.nextToken("comment").value)
    lexx.nextToken("discard")
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="end":
        #Asegurarse de que son comillas dobles y no simples!!!
        to_discard.append(lexx.nextToken("terminal").value)
    lexx.nextToken("end")
    return to_discard

# rule : nonterm [LPAREN nonterm (COMMA nonterm)+ RPAREN] [ RETURNS nonterm]  COLON elem+  [ CODE ] [ TREE ] SEMI
def rule():
    global lexx,rule_template,rule_info,comments,cur_rule,build_callback,callback_str,callback_template,rules_parts,rule_items
    ruleid = ""
    rulecode=""
    _tree=""
    _args=""
    _retval=""
    exception_str=""
    arglist=[]
    print("Entrando a rule")
    #print("Valor de rule_info: " + _tostring(rule_info))
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comment": 
        comments.append(lexx.nextToken("comment").value)
    #print("Buscando un no terminal...")
    id=lexx.nextToken("nonterm")
    ruleid=id.value
    rule_items.append(id)
    print("\n--->PROCESANDO REGLA: "  + ruleid)
    #crear funciones de callback si se ha pedido asi
    if build_callback==1:
        rulecode=rulecode + _indent("\non_enter_" + ruleid + "(" + ruleid + "_values)\n")
        callback_str= callback_str + callback_template_enter.format(ruleid,"print(\"enter " + ruleid + " callback code\")")
    cur_rule=ruleid
    #print("lookahead(1): " + str(lexx.lookahead(1)))
    #Buscar lista de argumentos si la hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="lparen":
        #print("Procesando lista de argumentos")
        lexx.nextToken("lparen")
        arglist.append(lexx.nextToken("nonterm").value)
        #print("lookahead(1): " + _tostring(lexx.lookahead(1)))
        while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="comma":
            lexx.nextToken("comma")
            arglist.append(lexx.nextToken("nonterm").value)
            #print("arglist: " + _tostring(arglist))
        lexx.nextToken("rparen")
    #print("Valor de arglist: " + _tostring(arglist))
    #Buscar valor de retorno si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="lbrack":
        #print("Procesando valor de retorno")
        lexx.nextToken("lbrack")
        lexx.nextToken("returns")
        _retval=lexx.nextToken("nonterm").value
        #print("retval: " + _retval)
        lexx.nextToken("rbrack")
    #print("Buscando un colon...")
    lexx.nextToken("colon")
    #Coger codigo de entrada a la regla si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
        rulecode= rulecode + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="semi":
        rule_items.append(lexx.lookahead(1)[0])
        rulecode= rulecode + elem()

    rules_parts.append(rule_items)
    #Coger codigo si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
        rulecode= rulecode + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
    #Crear AST si se ha indicado ???????
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
        _tree=lexx.nextToken("tree").value
        print("Building AST in rule!")
    lexx.nextToken("semi")
    if len(arglist) != 0: 
        rule_info[ruleid]=arglist 
        #print("RULE INFO: " + _tostring(rule_info))
        _args= functools.reduce( lambda x,y : x + "," + y,arglist)
    #llamar funciones de callback a la salida si se ha pedido asi
    if build_callback==1:
        rulecode=rulecode + _indent("on_exit_" + ruleid + "(" + ruleid + "_values)\n")
        callback_str= callback_str + callback_template_exit.format(ruleid,"print(\"exit "  + ruleid + " callback code\")")
    if _retval!= "":
        rulecode= rulecode + _indent("\nreturn " + _retval + "\n")
    else:
        rulecode= rulecode + _indent("\nreturn " + ruleid + "_values\n")
    #Resetear rule_items
    rule_items=[]
    print("\n--->TERMINADA REGLA: "  + ruleid)
    #return rule_template.format(ruleid,_args,_indent(rulecode))
    return rule_template.format(ruleid,_args,rulecode)



# elem : terminal code tree | nonterm code tree | optional code tree | options code tree | groupet code tree | empty
def elem():
    global lexx,margin,cur_rule,groupet_first,groupet_last,rule_items
    tree=""
    #print("Entrando a elem con: " + str(lexx.lookahead(1)[0]))
    code=""
    aux=""
    if lexx.lookahead(1)[0].type  == "lbrack":
        print("Yendo por optional")
        code=optional()
        #Coger codigo si lo hay
        #Crear AST si se ha indicado ???????
        #print("SALIENDO DE ELEM POR OPTIONAL!!!")
        return code
    elif lexx.lookahead(1)[0].type == "lparen":
        print("Yendo por groupet")
        #print("VALOR de groupet_first: " + groupet_first)
        code=groupet()
        print("Code devuelto por groupet():\n " + code)
        limit=lexx.lookahead(1)[0].value
        if code[-1] == "+": 
            code= code.strip("+")
            #Coger codigo si lo hay
            if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
                aux= _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
                #print("COGEMOS CODIGO EN AUX: " + aux)
                #limit=lexx.lookahead(1)[0].value
            #Crear AST si se ha indicado ???????
            if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
                _tree=lexx.nextToken("tree").value
                print("Building AST in elem!")
            limit= "!=\"" + lexx.lookahead(1)[0].value
            #Cambio para groupets terminales: usamos como limite el primer terminal del grupo si lo hay
            if groupet_first!="":
                limit="==\"" + groupet_first
                #groupet_first=""
                #print("VALOR DE LIMIT AHORA: " + limit)
            #code= code + "\n" + margin + "while lexx.lookahead(1)[0].type!=\"EOF\" "
            wp= "\n" + margin + "while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!=\"EOF\" "
            #print("groupet_first: " + groupet_first)
            #print("lexx.lookahead(1)[0].value: " + lexx.lookahead(1)[0].value)
            #raise "parada temporal"
            if groupet_first=="" and lexx.lookahead(1)[0].value=="":
                code=code + wp +  "\n " + _indent(code) + "\n" + margin + "\n"
            else:
                if groupet_last!="":
                    #print("Incorporando codigo para groupet_last!!!")
                    code= code + "while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!=\"" + groupet_last +"\" " + ":\n " + _indent(code) + "\n" + margin + "\n"
                else:
                    code= code + wp + "\n" + margin + "and lexx.lookahead(1)[0].type " + limit + "\" :\n" + _indent(code) + "\n" + margin + "\n"
            code=code + aux
            groupet_first=""
        elif code[-1] == "*":
            code= code.strip("*")
            #Coger codigo si lo hay
            if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
                aux= _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
                #print("COGEMOS CODIGO EN AUX: " + aux)
                #limit=lexx.lookahead(1)[0].value
            #Crear AST si se ha indicado ???????
            if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
                _tree=lexx.nextToken("tree").value
                print("Building AST in elem!")
            limit= "!=\"" + lexx.lookahead(1)[0].value
            if groupet_first!="":
                limit="==\"" + groupet_first
                #groupet_first=""
                #print("VALOR DE LIMIT AHORA: " + limit)
            #code= "\n" + margin + "while lexx.lookahead(1)[0].type!=\"EOF\" and lexx.lookahead(1)[0].type " + limit + "\" do\n" + _indent(code) + "\n" + margin + "end\n" 
            #code= code + "\n" + margin + "while lexx.lookahead(1)[0].type!=\"EOF\" "
            wp= "\n" + margin + "while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!=\"EOF\" "
            #print("groupet_first: " + groupet_first)
            #print("lexx.lookahead(1)[0].value: " + lexx.lookahead(1)[0].value)
            #raise "parada temporal"
            if groupet_first=="" and lexx.lookahead(1)[0].value=="":
                code= wp +  ":\n " + _indent(code) + "\n" + margin + "\n"
            else:  
                code= wp + "and lexx.lookahead(1)[0].type " + limit + "\" :\n" + _indent(code) + "\n" + margin + "\n"
            code=code + aux
            #Coger codigo si lo hay
            if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
                code= code + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
            #Crear AST si se ha indicado ???????
            if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
                _tree=lexx.nextToken("tree").value
                print("Building AST in rule!")
            groupet_first=""
        else:
            code= code + ""

        #print("salgo de elem!!!!!!!!!!")
        return code
    elif lexx.lookahead(1)[0].type == "pipe":
        print("Yendo por options")
        #code= "cond lexx.lookahead(1)[0].type\n"
        code= code + _indent(options())
        #code = code + margin + margin + "else do\nraise \"Error: field no permitido\"\nend\n"
        #Coger codigo si lo hay
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
            code= code + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
        #Crear AST si se ha indicado ???????
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
            _tree=lexx.nextToken("tree").value
            print("Building AST in rule!")
        return code
    elif lexx.lookahead(1)[0].type == "nonterm":
        print("Yendo por nonterm")
        nt= lexx.nextToken("nonterm").value
        #Comprobar recursividad por la izquierda(????)
        #if nt==cur_rule:
        #    raise format "Error: la regla {0} es recursiva por la izquierda." with [cur_rule]
        #end
        code= _indent(cur_rule + "_values.append( "  + nt + "())\n")
        #code= cur_rule + "_values.append( "  + nt + "())\n"
        #Coger codigo si lo hay
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
            code= code + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
        #Crear AST si se ha indicado ???????
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
            _tree=lexx.nextToken("tree").value
            print("Building AST in rule!")
        return code
    elif lexx.lookahead(1)[0].type == "terminal":
        print("Yendo por terminal")
        t=lexx.nextToken("terminal")
        #Cogemos los terminales si no estan en discard_list
        #print("DISCARD_LIST: " + _tostring(discard_list))
        #print("t.value: " + t.value)
        if t.value not in discard_list:
            code= _indent(cur_rule + "_values.append( "  + "lexx.nextToken(\"" + t.value + "\"))\n")
        else:
            code= _indent("lexx.nextToken(\"" + t.value + "\")\n")
        #Coger codigo si lo hay
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
            code= code + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
            #print("valor de code en terminal: " + code)
        #Crear AST si se ha indicado ???????
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
            _tree=lexx.nextToken("tree").value
            print("Building AST in rule!")
        return code
    else:
        print("Yendo por empty")
        t=lexx.nextToken("empty")
        #Coger codigo si lo hay
        if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
            code= code + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
            #print("valor de code en empty: " + code)
        return empty() + code #aceptamos empty, asi que lo consumimos

# optional : LBRACK elem+ RBRACK
def optional():
    global lexx,rule_items
    #print("Entrando a optional")
    lexx.nextToken("lbrack")
    #e ="if lexx.lookahead(1)[0].type==\"" + lexx.lookahead(1)[0].value  + "\":\n"
    #e= e + elem() + "\nend\n"
    #Cambio
    #code="if lexx.lookahead(1)[0].type==\"" + lexx.lookahead(1)[0].value  + "\":\n"
    #Cambio para que no coja el "(" de los groupets si se pone
    sure_tok=lexx.lookahead(1)[0].value if lexx.lookahead(1)[0].value!="(" else lexx.lookahead(2)[1].value
    print("VALOR DE TOKEN SEGURO: " + sure_tok)
    code="if lexx.lookahead(1)[0].type==\"" + sure_tok  + "\":\n"
    while lexx.lookahead(1)[0].type!="rbrack":
        code=code + _indent(elem())
    code= code + "\n"
    #Coger codigo si lo hay
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="code": 
        code= code + _indent(lexx.nextToken("code").value.strip("{{").strip("}}"))
    #Crear AST si se ha indicado ???????
    if lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="tree": 
        _tree=lexx.nextToken("tree").value
        print("Building AST in optional!")
    lexx.nextToken("rbrack")
    #print("Code al salir de optional: " + code)
    #raise "PARADA TEMPORAL!!"
    return code

#Working
def options():
    global lexx,margin,LA,cur_rule,memos,rule_items
    code="if lexx.lookahead(1)!=[]:\ncond  lexx.lookahead(1)[0].type\n"
    #print("Entrando a options")
    options_code=""
    code=""
    opts_idxs=[]
    primeros=[]
    cont=1
    opts_elems={}
    buffer=[]
    last_opt=cont-1
    tk=None

    #1.- Coger todos los tokens de la opcion para calcular primeros, pero
    #SIN AVANZAR el puntero a la cadena de entrada.

    #Este while busca los pipes de cambio de opcion y mete los tokens encontrados
    #en opts_elems, sin coger code ni tree

    while lexx.lookahead(cont)!=[] and lexx.lookahead(cont)[cont-1].type!="semi":
        print("Entrando al while en options")
        la=lexx.lookahead(cont)
        tk=la[cont-1]
        if tk.type!="pipe":
            buffer.append(tk)
            #print("Guardando token")
        else:
            if last_opt != (cont-1): 
                #Quitar de buffer los code y tree
                #Meter tokens,len,num. de no terminales que tienen e indice de opcion
                buffer= list(filter(lambda x :x.type not in ["code","tree"], buffer))
                opts_elems[last_opt]= [buffer[:],len(buffer),len(list(filter(lambda x: x.type=="nonterm",buffer))),last_opt]
                buffer=[]
                last_opt=cont-1
        cont+=1
        #print("Valor de cont: " + cont)
    #print("-----------------------------------------------------")
    if buffer!=[]: #Coger lo que queda en buffer
        #Quitar de buffer los code y tree
        buffer= list(filter(lambda x:x.type not in ["code","tree"],buffer))
        opts_elems[last_opt]= [(buffer[:]),len(buffer),len(list(filter(lambda x: x.type=="nonterm",buffer))),last_opt]

    #print("OPTS_ELEMS:")
    #pprint.pprint(opts_elems)
    #print("-----------------------------------------")
    #temp_la=1 #???
    checked=[]
    cont=0
    #Obtener un lista ordenada de los valores de los indices(es necesario tener los indices de las opciones)
    ordered_opts= list(opts_elems.values())
    ordered_opts.sort(key = lambda x:x[1])


    #Asegurarse de que no hay recursividad por la izquierda
    #cur_rule es una global que contiene la regla en curso
    #_checkLeftRecursive(cur_rule,ordered_opts)

    #Calcular primeros para las opciones obtenidas
    primeros=_primeros3(ordered_opts)

    #====================================================================================================
    #Una vez tenemos primeros, hay que ordenarlos por el quinto item, que es el indice de la opcion.
    #Esto es imprescindible porque hay que desarrollar los elementos de primeros en el orden en que
    #se especifican en el fichero fuente, porque vamos cogiendo los codes y el resto por orden de aparicion
    #======================================================================================================

    primeros.sort(key = lambda x:x[4])
    print("PRIMEROS ORDENADOS:")
    print("---------------------------")
    pprint.pprint(primeros)
    print("---------------------------")
    if len(primeros)!=len(ordered_opts):
        raise Exception("Error: No se ha podido encontrar un conjunto de primeros para separar las opciones de la regla " + cur_rule)
    #Tabla que indica cuantas veces esta cada opcion en el conjunto de primeros
    opts_histo= _histogram(map(lambda x:x[0],primeros))
    pprint.pprint(opts_histo)
    #Proceder segun numero de no terminales en primeros:
    ends=""
    ifs_str=""
    ifs_ends=""
    try_str=""
    try_ends=""
    finally_str=""
    parsing_empty=0
    #num_nonterms= reduce |(x,y): x if x>y[3] else y[3]| in primeros with 0
    num_nonterms= len(list(filter(lambda x : x[1][0].type=="nonterm", primeros)))
    print("Numero de no terminales en opciones de primeros primeros: " + str(num_nonterms))

    #1.- Si el tercer campo de cada opcion es False para todos
    #generar cadena de if-else para cada opcion como antes
    #Todos terminales: generar cadena de if-else
    if num_nonterms == 0:
        #print("GENERANDO CADENA DE IF-ELSE")
        #raise "Parada temporal!! :)!"
        cont=0
        while lexx.lookahead(1)!=[] and (lexx.lookahead(1)[0].type=="pipe" or lexx.lookahead(1)[0].type=="code" or lexx.lookahead(1)[0].type=="tree"):
            andstr= ""
            #print("TOKEN antes de next(pipe): " + _tostring(lexx.lookahead(1)[0]))
            #Coger el token de codigo y el de tree si se especifica
            _break=0
            if lexx.lookahead(1)[0].type=="tree": 
                lexx.nextToken("tree")
                _break=1
            if lexx.lookahead(1)[0].type=="code": 
                options_code= lexx.nextToken("code").value.strip("{{").strip("}}")
                _break=1
            if _break==1: break
            if lexx.lookahead(1)[0].type!="code" and lexx.lookahead(1)[0].type!="tree": 
                lexx.nextToken("pipe")

            #CAMBIAR TODO A PARTIR DE AQUI PARA USAR LA ESTRUCTURA QUE GENERA PRIMEROS
            #t es el lookahead necesario para discriminar cada opcion
            t=(primeros[cont][-1] - primeros[cont][3]) if primeros[cont][-1]>0 else 1

            if primeros[cont][0]!="empty":
                #Montar cadena de ands si procede
                #print(format "valor de t: {0} , primeros[cont][0]: {1}" with [t,primeros[cont][0]])
                if (t > 1 and primeros[cont][1][t-1].type=="terminal") or (opts_histo[primeros[cont][0]] > 1 and len(primeros[cont][1])>1):
                    #print("===>aqui hay que generar una cadena de ands")
                    #if primeros[cont][0] in _keys(opts_histo): t = opts_histo[primeros[cont][0]]-1 end
                    t = (opts_histo[primeros[cont][0]]-1) if opts_histo[primeros[cont][0]] > 2 else opts_histo[primeros[cont][0]]
                    #-------------------------------------------------------------------------------------------
                    #OJO: t no puede ser mayor que len(primeros[cont][1])!!
                    if t > len(primeros[cont][1])-1: t= len(primeros[cont][1])
                    #-------------------------------------------------------------------------------------------
                    cnt=0
                    while cnt< t:
                        #No poner no terminales en la cadena de ands
                        #OJO: cnt no puede ser mayor que len([primeros[cont]-1)!!!!!-------
                        if cnt > len(primeros[cont][1])-1: break
                        #--------------------------------------------------------------------
                        if primeros[cont][1][cnt].type!="nonterm":
                            pre= "if " if cnt==0 else " and "
                            andstr= andstr + pre + " lexx.lookahead(" + str(t) + ")[" + str(cnt) + "].type==\"" + primeros[cont][1][cnt].value + "\" "
                        cnt+=1
                    print("==>andstr: " + andstr)
                    code=code + andstr + ": \n"
                else:
                    code =  code + "if lexx.lookahead("
                    #Asegurarse de que t vale al menos 1!!
                    if t==0:
                        t=1
                    code = code + str(t)  + ")[" + str(t-1) + "].type==\"" + primeros[cont][0] + "\": \n"
                    print("Code generado para opcion sencilla: " + code)
                code= code + margin + elem()
                code= code + margin +  "else:\n"
                ends= ends + "\n"
            else:
                code= code + margin + elem()
                parsing_empty=1
            if lexx.lookahead(1)[0].type not in ["code","tree"]: cont+=1
        if parsing_empty==0: 
            code = code + "raise Exception(\"Error parsing options: No viable alternative for discriminate this options.\")"
        code=code+ends
    #Un solo no terminal: generar cadena de if-else y llamar al no terminal al final(Revisar esto: puede fallar
    #si se necesita lookahead > 2 para alguno y pasa por un no terminal->DEBERIA COMPROBARLO!)
    elif num_nonterms == 1:
        cont=0
        last_code=""
        empty_code=""
        #while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="pipe" do
        while lexx.lookahead(1)!=[] and (lexx.lookahead(1)[0].type=="pipe" or lexx.lookahead(1)[0].type=="code" or lexx.lookahead(1)[0].type=="tree"):
            andstr=""
            #print("TOKEN para case==1 antes de next(pipe): " + _tostring(lexx.lookahead(1)[0]))
            #Coger el token de codigo y el de tree si se especifica
            _break=0
            if lexx.lookahead(1)[0].type=="tree": 
                lexx.nextToken("tree")
                _break=1
            if lexx.lookahead(1)[0].type=="code": 
                options_code= lexx.nextToken("code").value.strip("{{").strip("}}")
                _break=1
            if _break==1: break
            if lexx.lookahead(1)[0].type!="code" and lexx.lookahead(1)[0].type!="tree": 
                lexx.nextToken("pipe")

            #t es el lookahead necesario para discriminar cada opcion
            t=(primeros[cont][-1] - primeros[cont][3]) if primeros[cont][-1]>0 else 1

            #Coger el no terminal
            if primeros[cont][2]==1: 
                last_code= last_code + margin + elem()
            else:
                if primeros[cont][0]!="empty": 
                    if (t > 1 and primeros[cont][1][t-1].type=="terminal") or (opts_histo[primeros[cont][0]] > 1 and len(primeros[cont][1])>1):
                        #print("===>aqui hay que generar una cadena de ands en 1 nonterm")
                        t = (opts_histo[primeros[cont][0]]-1) if opts_histo[primeros[cont][0]] > 2 else opts_histo[primeros[cont][0]]
                        #-------------------------------------------------------------------------------------------
                        #OJO: t no puede ser mayor que len(primeros[cont][1])!!
                        if t > len(primeros[cont][1])-1: t= len(primeros[cont][1])
                        #-------------------------------------------------------------------------------------------
                        cnt=0
                        while cnt< t:
                            #OJO: cnt no puede ser mayor que len([primeros[cont]-1)!!!!!-------
                            if cnt > len(primeros[cont][1])-1: break
                            #--------------------------------------------------------------------
                            #No poner no terminales en la cadena de ands
                            if primeros[cont][1][cnt].type!="nonterm":
                                pre= "if " if cnt==0 else " and "
                                andstr= andstr + pre + " lexx.lookahead(" + t + ")[" + cnt + "].type==\"" + primeros[cont][1][cnt].value + "\" "
                            cnt+=1
                        #print("andstr: " + andstr)
                        code=code + andstr + ": \n"
                    else:
                        code =  code + "if lexx.lookahead("
                        #Asegurarse de que t vale al menos 1!!
                        if t==0:
                            t=1
                        code= code + str(t)  + ")[" + str(t-1) + "].type==\"" + primeros[cont][0] + "\"" + andstr + ": \n"
                        code= code + margin + elem()
                        code= code + "else:\n"
                        ends= ends + "\n"
                else:  
                    #empty_code= "if lexx.lookahead(0).type!=\"EOF\":\n" + margin + elem() + "else\n"
                    #ends= ends + "\nend\n"
                    empty_code=margin + elem()
            cont+=1
        code =  code + last_code
        if empty_code!="":
            code=code + empty_code
        #code = code + "raise \"Error parsing options: No viable alternative for discriminate this options\""
        code=code+ends#FALTA UN END???????*/
    #Algunos no terminales: generar cadena de try-catch e if-else para backtrack
    elif num_nonterms > 1:
        #crear entrada en memos para la regla
        memos.append("\"" + cur_rule + "\":{}")
        code = code + "\nright=0\ntemp=lexx.getIndex()\n"
        cont=1
        try_str = try_str + "if _alreadyParsed(memos[\"" + cur_rule + "\"],temp)==None:\n"
        #Recuperar input tras el ultimo try
        #ifs_str = ifs_str + "lexx.setIndex(_stack.pop())\n"
        ifs_str = ""
        while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type=="pipe":
            lexx.nextToken("pipe")
            elem_code=elem()
            #print("======================elem_code==========")
            #print(elem_code)
            #print(re.sub("[a-zA-Z0-9_]+\s*::","",elem_code))
            #print("=========================================")
            try_str =  try_str + "try:\n"
            try_str =  try_str + "_stack.push(lexx.getIndex())\n"
            #try_str= try_str + margin + elem_code
            try_str= try_str + margin + re.sub("[a-zA-Z0-9_]+\s*::","",elem_code)
            try_str =  try_str + "right=" + cont + "\n"
            try_str= try_str + "except:\n"
            try_str =  try_str + "lexx.setIndex(_stack.pop())\n"
            try_ends= try_ends + "\n"

            ifs_str =  ifs_str + "if right==" + cont + ":\n"
            ifs_str= ifs_str + margin + elem_code
            ifs_str= ifs_str + "else:\n"
            ifs_ends= ifs_ends + "\n"
            cont+=1
        try_str = try_str + margin + "raise \"Error: Sin alternativa viable tras backtrack para las opciones\""
        finally_str= finally_str + "\nfinally:\n"
        finally_str =  finally_str + "_memoize(memos[\"" + cur_rule + "\"],temp,right)\n"
        ifs_str = ifs_str + margin + "raise Exception(\"Error: Sin alternativa viable tras backtrack para las opciones\")"
        #Colocar la cadena con el finally antes del ultimo end de la cadena de try_ends
        #print("VALOR DE TRY_ENDS: " + try_ends)
        t= try_ends.split("")
        t.insert(1,finally_str)
        t= filter(lambda x: x.strip()!="",t)
        #print("NUEVO VALOR DE T: " + _tostring(t))
        try_ends= "".join(t) + "\n"
        #print("NUEVO VALOR DE TRY_ENDS: " + try_ends)
        #print("&&&&&&&&&&&&&&")
        code= code + try_str + try_ends
        code= code + "lexx.setIndex(_stack.pop())\n"
        #Cerrar el if-else
        code = code + "else:\nright=memos[\"" + cur_rule + "\"][temp]\n"
        code= code + ifs_str + ifs_ends
        #print("Code en options: " + code)
    else:
        raise "Opcion no implementada todavia"
    if options_code!="":
        code=code + options_code
    print("===>codigo al salir de options: \n" + code)
    #raise "PARADA TEMPORAL :)"
    return code     

# group : LPAREN elem+ RPAREN closure
def groupet():
    global lexx,groupet_first,groupet_last,rule_items,margin
    code=""
    #print("Entrando a groupet")
    lexx.nextToken("lparen")
    #Coger el valor del primer token si es no terminal
    #que servira para poder procesar el groupet sin que llegue al final de manera incorrecta**/
    if lexx.lookahead(1)[0].type=="terminal":
        groupet_first=lexx.lookahead(1)[0].value
        groupet_last=""
        #print("GROUPET FIRST: " + groupet_first)
    else: #Especulativo: buscar un terminal y usarlo???
        #print("Buscando Groupet_last...")
        cont=2
        while lexx.lookahead(cont)!=[]:
            #print(_tostring(lexx.lookahead(cont)))
            if lexx.lookahead(cont)[cont-1].type=="terminal":
                groupet_last=lexx.lookahead(cont)[cont-1].value
                #print("Encontrado GROUPET_LAST!!:" + groupet_last)
                #groupet_first=""
                break
            cont+=1
    while lexx.lookahead(1)!=[] and lexx.lookahead(1)[0].type!="rparen":
        #Cambio para procesar posibles codes y trees que se puedan colar en un groupet
        #(como p. ej. un optional dentro de un groupet)*/
        if lexx.lookahead(1)[0].type=="tree": 
            lexx.nextToken("tree")
        else:
            if lexx.lookahead(1)[0].type=="code": 
                code=code + lexx.nextToken("code").value.strip("{{").strip("}}")
            else:
                code= code + elem()
    lexx.nextToken("rparen")
    seen=[]
    if lexx.lookahead(1)!=[]: seen= lexx.lookahead(1)
    if seen!=[]: 
        if seen[0].type=="plus":
            code= code + lexx.nextToken("plus").value#Consumirlo
        else:
            if seen[0].type=="mult":
                code= code + lexx.nextToken("mult").value
    #print(f"CODE al salir de groupet():\n{code}")
    return code

def empty():
    return "__dummy_value_for_empty_option__=0\n"

