

from grammar_utils import *
from ebnf_parser import *


py_packrat_template='''
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
__MEMOS_TABLE : Dict[str,Dict[int,Tuple[bool,int,int]]] = {}

def addToMemos(rule_name):
    'Mete una regla en memos'
    global __MEMOS_TABLE
    if not rule_name in __MEMOS_TABLE:
        __MEMOS_TABLE[rule_name] = {}

def getMemos():
    'Devuelve __MEMOS_TABLE'
    return __MEMOS_TABLE

def memoize(rule_name : str, pos:int, success : bool,offset: int=-1,opt=-1) -> None:
    'Guarda la posicion en la que se invoco la regla la ultima vez y si se consiguió ejecutarla.'
    global __MEMOS_TABLE
    if rule_name in __MEMOS_TABLE:
        __MEMOS_TABLE[rule_name][pos] = (success,offset,opt)

def alreadyParsed(rule_name: str,pos:int,as_tuple=False) -> Union[Tuple,None]:
    'Doc'
    global __MEMOS_TABLE
    if pos in __MEMOS_TABLE[rule_name]:
        if as_tuple == False:
            return __MEMOS_TABLE[rule_name][pos][0]
        else:
            return __MEMOS_TABLE[rule_name][pos]
    else:
        return None



'''

packrat_rule_template='''


def {0}():
    #Obtener el indice de la entrada para backtrack
    _index = lexx.getIndex()
    _success = alreadyParsed('{0}',_index)
    #Si no estamos probando y success es True, ejecutarla
    if _success == True:
        if not isTrying():
            _resul = _{0}()
            return _resul
        else:
            print("Using cache for rule {0} true")
            return            
    elif _success == False:
        #Si ya se ha visto,
        print("Using cache for rule {0} false")
        #return
        raise Exception("Yet parsed rule {0} at index %s without success" % _index)
    else:
        try:
            print("Trying rule {0}")
            _{0}()
            _success = True
        except:
            #Rewind
            print("Failed parsing of rule {0}: Backtrack")
            _success = False
        finally:
            print("Memoizing rule {0} with success: " + str(_success))
            memoize('{0}',_index,_success)
            print(getMemos())
            return

'''

packrat_starter_template='''

def startPackrat():
    'Inicia la cadena de try'
    setTrying(True)
    {0}()
    print("-----Try completado----------")
    if alreadyParsed("{0}",0) in [None,False]:
        raise Exception("Error: el parser no puede reconocer la entrada!!")
    else:
        setTrying(False)
        lexx.setIndex(0)
        return {0}()


'''

def buildPackratParser(rule_list : list, callbacks : bool,toks_to_discard :  List[str]) -> str:
    '''
    Construye un parser descendente recursivo en Python
    con backtracking y cache
    a partir de una lista de GrammarRules.
    '''
    global callbacks_template,callbacks_code,packrat_rule_template
    buffer = io.StringIO()
    for rule in rule_list:
        #print("RULE:")
        #pprint.pprint(rule)
        #print("====")
        rule_values = rule[0].value + "_values"

        #------------------------------------------------------------------------------------
        #Cambios para permitir params y return: si los tiene hay un
        #token con ese tipo y otro con code: buscar primero params y luego returns
        rule_rhs = rule[1:]
        rule_args = ""
        rule_returns = ""
        if type(rule_rhs[0]) == lexer.Token and rule_rhs[0].type == "params": 
            rule_args = rule_rhs[1].value[2:-2]
            print(f">>>>RULE_ARGS: {rule_args}")
            rule_rhs=rule_rhs[2:]
        if type(rule_rhs[0]) == lexer.Token and rule_rhs[0].type == "returns": 
            rule_returns = rule_rhs[1].value[2:-2]
            rule_rhs=rule_rhs[2:]
        #------------------------------------------------------------------------------------

        buffer.write("addToMemos('" + rule[0].value + "')\n")
        buffer.write(packrat_rule_template.format(rule[0].value))
        buffer.write("def _" + rule[0].value + "(" + rule_args + "):\n")
        #Regla como docstring
        docstr = "\n    '''\n" + "    " +  rule[0].value + " : " + " ".join([x.value for x in flat(rule[1:])])    + "\n    '''\n"
        buffer.write(docstr)
        #Meter lista para recoger tokens parseados
        #buffer.write("    " + rule_values + " = []\n")
        buffer.write("    " + rule_values + " = TagList('" + rule[0].value + "')\n")
        #Callback de entrada si se ha definido
        if callbacks == True:
            buffer.write("    on_Enter_" + rule[0].value + "(" + rule_values + ")\n")
            callbacks_code.write(callbacks_template.format("Enter",rule[0].value,rule_values))
        ruleToPackratParser(rule_rhs,buffer,rule_values = rule_values,toks_to_discard=toks_to_discard,rule_name = rule[0].value)
        #Callback de salida si se ha definido
        if callbacks == True:
            buffer.write("    on_Exit_" + rule[0].value + "(" + rule_values + ")\n")
            callbacks_code.write(callbacks_template.format("Exit",rule[0].value,rule_values))
        if rule_returns != "":
            #buffer.write("\n    return " + rule_values + "\n\n")
        #else:
            buffer.write("\n    return " + rule_returns + "\n\n")
  
    return buffer.getvalue()


def ruleToPackratParser2(rule_rhs : list, parser_buff : io.StringIO, margin : str = "    ",rule_values = "",toks_to_discard = [],rule_name="",is_group = False,while_str = "") -> str:
    '''
    Convierte una regla en un parser descendente
    de LA variable. distingue cuatro tipos de
    variaciones: Terminal, No terminal, Closure y 
    Options. 
    '''
    #print(f"TOKS_TO_DISCARD AQUI:{toks_to_discard}")
    #print("ENTERING ruleToPackratParser()")
    #Plantilla para los and de LA > 1
    #and_template = " and lexx.lookahead({0})[{1}].type == '{2}'"
    packrat_buff = io.StringIO()
    rule_buff = io.StringIO()
    #options_buff = io.StringIO()
    for item in rule_rhs:
        #print("ITEM:\n")
        pprint.pprint(item)
        if type(item) != list:
            if item.type == "nonterm":
                print("Procesando un no terminal")
                packrat_buff.write(margin*2 +  item.value + "()\n")                
                rule_buff.write(margin*2 + rule_values + ".append(" +  item.value + "())\n")
            elif item.type == 'terminal':
                print(f"procesando un terminal: {item.value}")
                #Cambio para solo avanzar token en packrat
                #MEJOR SEPARAR ESTO EN DOS STRINGS: SOLO UNA VEZ isTrying!!!!!!!
                packrat_buff.write(margin*2 + "lexx.nextToken('" + item.value + "')\n") 
                if item.value not in toks_to_discard:
                    rule_buff.write(margin*2  + rule_values +  ".append(lexx.nextToken('" + item.value + "'))\n")
                else:
                    rule_buff.write(margin*2 + "lexx.nextToken('" + item.value + "')\n")                    
            elif item.type == "code":
                print("Procesando code")
                rule_buff.write(indent(item.value[2:-2],margin*2))
            else: #empty
                print("Procesando empty!")
                #no hacemos nada??
        else: 
            #Procedemos segun elemento
            if item[0].type == "lparen":
                print("procesando un group o un closure")
                cls = item[-1].value if item[-1].type!="code" else item[-2].value
                #to_process = item[1:-1] if item[-1].type!="code" else item[1:-2]
                has_code_last = item[-1].type =="code" #REORGANIZAR ESTO!!!!!!!
                #print(f"====VALOR DE CLS: {cls}, has_code_last: {has_code_last}")
                #---------------------------------------------------------------------------------------
                #Cambio para permitir que el primer elemento de un group sea un no terminal (instr SEMI)*
                always_check = "lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF'"
                #Cambios para extra_checks-------------------------------------------------------------
                check_if_terminal = " and lexx.lookahead(1)[0].type == '" + item[1].value + "'"
                extra_checks = ""
                #print(f"\nITEM DE GROUP: {item}\n")
                #Separar item en xtras y no xtras
                xtras = []
                rest = []
                for el in item: 
                    if type(el) == list and type(el[0])== lexer.Token and el[0].type=="lbrack":
                        xtras.append(el)
                    else:
                        rest.append(el)
                if len(xtras) > 0:
                    xtras=xtras[0][1:-1]
                    for xtra in xtras:
                        extra_checks += " and lexx.lookahead(1)[0].type != '" + xtra.value + "'"
                #print(f"xtras: {xtras}")
                #print(f"rest: {rest}")
                to_process = rest[1:-1] if rest[-1].type!="code" else rest[1:-2]
                #fin cambios para extra_checks----------------------------------------------------------

                check_string = always_check + extra_checks
                if item[1].type == "terminal":
                    check_string += check_if_terminal 
                #---------------------------------------------------------------------------------------
                if cls == '?':
                    print("Es un optional")
                    parser_buff.write(margin + "if " + check_string + ":\n")
                    ruleToPackratParser(to_process,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = "")
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = "")
                elif cls == '*':
                    #Ignorar parentesis de apertura de grupo, de cierre y */+/?
                    print(f"Es un closure 0 o mas: procesando: {to_process}")
                    #packrat_buff.write(margin + "xwhile " + check_string + ":\n")
                    #parser_buff.write(margin + "while " + check_string + ":\n")
                    while_str = margin + "while " + check_string + ":\n"
                    ruleToPackratParser(to_process,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = while_str)
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = "")
                elif cls == '+':
                    print("Es un uno o mas")
                    ruleToPackratParser(to_process,parser_buff,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = while_str)
                    #parser_buff.write(margin + "while " + check_string + ":\n")
                    while_str = margin + "while " + check_string + ":\n"
                    ruleToPackratParser(to_process,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = while_str)
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = "")
                else:
                    print("Es un group")
                    #Hay que comprobar que tipo de group es y proceder en consecuencia??
                    ruleToPackratParser(to_process,parser_buff,margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=True,while_str = "")
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=False,while_str = "")
            elif item[0].type == 'pipe':
                print("procesando Options")
                #print(f"ITEM AQUI: {item}")
                #opts=[]
                opts = getOptions(item,[])
                print("opts-----------")
                print(opts)
                print("-------------")
                for opt in opts:
                    parser_buff.write(margin + "try:\n")                    
                    ruleToPackratParser(opt,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=is_group,while_str = "")                                       
                    parser_buff.write(margin  + "except:\n        pass\n")
            else: #Cadena de terminales/no terminales
                ruleToPackratParser(item,parser_buff,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_group=is_group,while_str = "")  

    #Ahora meter por separado lo del packrat y lo normal------------------------------
    packrat_str = packrat_buff.getvalue()

    if packrat_str != "":
        print(f"PACKRAT_STR: {packrat_str}")
        print(f"while_str: {while_str}")
        if while_str != "":
            tmp = margin[:-4] + "if isTrying():\n"
            tmp+= margin[:-4] + while_str
            packrat_str = tmp + packrat_str
            packrat_str+="\n" + margin + "return \n"
            packrat_str += margin[:-4] + "else:\n" + margin[:-4] + while_str

        else:
            parser_buff.write(margin + "if isTrying():\n")
        parser_buff.write(packrat_str)
        if is_group != True:
            parser_buff.write(margin*2 + "return\n")
        if while_str == "":
            parser_buff.write(margin + "else:\n")
    parser_buff.write(rule_buff.getvalue())
    if is_group!=True:
        parser_buff.write(margin + "return " +  rule_name +  "_values\n\n\n")
        is_group = False 
    #---------------------------------------------------------------------------------


def ruleToPackratParser(rule_rhs : list, parser_buff : io.StringIO, margin : str = "    ",rule_values = "",toks_to_discard = [],rule_name="",is_trying = False,deep_level = 0) -> str:
    '''
    Convierte una regla en un parser descendente
    de LA variable. distingue cuatro tipos de
    variaciones: Terminal, No terminal, Closure y 
    Options. 
    '''
    for item in rule_rhs:
        #print("ITEM:\n")
        pprint.pprint(item)
        if type(item) != list:
            if item.type == "nonterm":
                print("Procesando un no terminal") 
                if is_trying == False:            
                    parser_buff.write(margin*2 + rule_values + ".append(" +  item.value + "())\n")
                else:            
                    parser_buff.write(margin*2 + item.value + "()\n")
            elif item.type == 'terminal':
                print(f"procesando un terminal: {item.value}")
                #Cambio para solo avanzar token en packrat
                #MEJOR SEPARAR ESTO EN DOS STRINGS: SOLO UNA VEZ isTrying!!!!!!!
                if is_trying == False:
                    if item.value not in toks_to_discard:
                        parser_buff.write(margin*2  + rule_values +  ".append(lexx.nextToken('" + item.value + "'))\n")
                    else:
                        parser_buff.write(margin*2 + "lexx.nextToken('" + item.value + "')\n") 
                else:
                        parser_buff.write(margin*2 + "lexx.nextToken('" + item.value + "')\n")                
            elif item.type == "code" and is_trying ==False:
                print("Procesando code")
                parser_buff.write(indent(item.value[2:-2],margin*2))
            else: #empty
                print("Procesando empty!")
                #no hacemos nada??
        else: 
            #Procedemos segun elemento
            if item[0].type == "lparen":
                print("procesando un group o un closure")
                cls = item[-1].value if item[-1].type!="code" else item[-2].value
                #to_process = item[1:-1] if item[-1].type!="code" else item[1:-2]
                has_code_last = item[-1].type =="code" #REORGANIZAR ESTO!!!!!!!
                #print(f"====VALOR DE CLS: {cls}, has_code_last: {has_code_last}")
                #---------------------------------------------------------------------------------------
                #Cambio para permitir que el primer elemento de un group sea un no terminal (instr SEMI)*
                always_check = "lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF'"
                #Cambios para extra_checks-------------------------------------------------------------
                check_if_terminal = " and lexx.lookahead(1)[0].type == '" + item[1].value + "'"
                extra_checks = ""
                #print(f"\nITEM DE GROUP: {item}\n")
                #Separar item en xtras y no xtras
                xtras = []
                rest = []
                for el in item: 
                    if type(el) == list and type(el[0])== lexer.Token and el[0].type=="lbrack":
                        xtras.append(el)
                    else:
                        rest.append(el)
                if len(xtras) > 0:
                    xtras=xtras[0][1:-1]
                    for xtra in xtras:
                        extra_checks += " and lexx.lookahead(1)[0].type != '" + xtra.value + "'"
                #print(f"xtras: {xtras}")
                #print(f"rest: {rest}")
                to_process = rest[1:-1] if rest[-1].type!="code" else rest[1:-2]
                print("to_process:-----------------")
                print(to_process)
                print("-------------------------------")
                #fin cambios para extra_checks----------------------------------------------------------

                check_string = always_check + extra_checks
                if item[1].type == "terminal":
                    check_string += check_if_terminal 
                #---------------------------------------------------------------------------------------
                if cls == '?':
                    print("Es un optional")
                    #Procesar primera llamada
                    if_str = margin + "if " + check_string + ":\n"
                    temp = io.StringIO()
                    ruleToPackratParser(to_process,temp,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=True,deep_level = deep_level+1)
                    code= temp.getvalue()
                    print("=======")
                    print(f"CODE?: {code}")
                    print("=======")
                    #if deep_level < 2:
                    parser_buff.write(margin + "if isTrying():\n")
                    parser_buff.write(margin + if_str)
                    parser_buff.write(indent(code,margin))
                    parser_buff.write(margin + "    return\n")
                    #Procesar el while
                    temp = io.StringIO()
                    ruleToPackratParser(to_process,temp,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False,deep_level = deep_level+1)
                    code= temp.getvalue()
                    parser_buff.write(margin + "else:\n")
                    parser_buff.write(margin + if_str)
                    parser_buff.write(indent(code,margin))
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False,deep_level = deep_level+1)
                elif cls == '*':
                    #Ignorar parentesis de apertura de grupo, de cierre y */+/?
                    print(f"Es un closure 0 o mas: procesando: {to_process}")
                    while_str = margin + "while " + check_string + ":\n"
                    #Procesar primera llamada
                    temp = io.StringIO()
                    ruleToPackratParser(to_process,temp,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=True,deep_level = deep_level+1)
                    code= temp.getvalue()
                    print("=======")
                    print(f"CODE*: {code}")
                    print("=======")
                    #if deep_level < 2:
                    parser_buff.write(margin + "if isTrying():\n")
                    parser_buff.write(margin + while_str)
                    parser_buff.write(indent(code,margin))
                    if deep_level==0:
                        parser_buff.write(margin + "    return\n")
                    #Procesar el while
                    temp = io.StringIO()
                    ruleToPackratParser(to_process,temp,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False,deep_level = deep_level+1)
                    code= temp.getvalue()
                    parser_buff.write(margin + "else:\n")
                    parser_buff.write(margin + while_str)
                    parser_buff.write(indent(code,margin))
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False,deep_level = deep_level+1)
                elif cls == '+':
                    print("Es un uno o mas")
                    while_str = margin + "while " + check_string + ":\n"
                    #Procesar primera llamada
                    '''
                    temp = io.StringIO()
                    print("Procesando code trying!!------------------------------")
                    ruleToPackratParser(to_process,temp,margin = margin,rule_values=rule_values,
                                        toks_to_discard=toks_to_discard,rule_name=rule_name,
                                        is_trying=True,deep_level = deep_level) #+1)
                    print("Fin trying--------------------------------------------")
                    code_t= temp.getvalue()
                    '''                    
                    temp = io.StringIO()
                    print("Procesando code real----------------------------------")
                    ruleToPackratParser(to_process,temp,margin = margin,rule_values=rule_values,
                                        toks_to_discard=toks_to_discard,rule_name=rule_name,
                                        is_trying=False,deep_level = deep_level+1)
                    code= temp.getvalue()
                    print("Fin code real------------------------------------------")
                    print("=======")
                    print(f"CODE+:\n{code}")
                    print("=======")
                    #if is_trying == True:
                    parser_buff.write("#--------------------------->>" + str(deep_level) + "\n")
                    parser_buff.write(margin + "if isTrying():\n")
                    parser_buff.write(code)
                    parser_buff.write(margin + while_str)
                    parser_buff.write(indent(code,margin))
                    if deep_level==0:
                        parser_buff.write(margin + "    return\n")
                    #Procesar el while
                    #if is_trying == False:
                    parser_buff.write(margin + "else:\n")
                    parser_buff.write(code)
                    parser_buff.write(margin + while_str)
                    parser_buff.write(indent(code,margin))
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False,deep_level = deep_level+1)
                    parser_buff.write("#<<---------------------------" + str(deep_level) + "\n")
                else:
                    print("Es un group")
                    #Hay que comprobar que tipo de group es y proceder en consecuencia??
                    ruleToPackratParser(to_process,parser_buff,margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=True,deep_level = deep_level+1)
                    if has_code_last:
                        ruleToPackratParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False,deep_level = deep_level+1)

            elif item[0].type == 'pipe':
                print("procesando Options")
                #print(f"ITEM AQUI: {item}")
                #opts=[]
                opts = getOptions(item,[])
                print("opts-----------")
                print(opts)
                print("-------------")
                for opt in opts:
                    parser_buff.write(margin + "try:\n")                    
                    ruleToPackratParser(opt,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False)                                       
                    parser_buff.write(margin  + "except:\n        pass\n")
            else: #Cadena de terminales/no terminales
                ruleToPackratParser(item,parser_buff,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard,rule_name=rule_name,is_trying=False)  




def packPackratParser(g_id,main_symbol,toks,parser_code,pre_code,post_code,toks_to_ignore):
    '''
    Construye y empaqueta el parser en un archivo
    '''
    global parser_template
    parser = py_packrat_template
    parser += parser_template.replace("%%tokens%%",toks)
    parser = parser.replace("%%parser_code%%",parser_code)
    if toks_to_ignore != []:
        parser = parser.replace("%%to_ignore%%","__toks_to_ignore = [" + ','.join(toks_to_ignore) + ']\nlexx.setIgnore(__toks_to_ignore)\n')
    else:
        parser = parser.replace("%%to_ignore%%","")

    parser = parser.replace("%%callbacks_code%%",callbacks_code.getvalue())
    if pre_code!="":
        parser = parser.replace("%%user_init_code%%",pre_code.value[2:-2] )
    else:
        parser = parser.replace("%%user_init_code%%","") 

    if post_code!="":    
        parser = parser.replace("%%user_end_code%%",packrat_starter_template.format(main_symbol) + post_code.value[2:-2] )
    else:
        parser = parser.replace("%%user_end_code%%","" )

    with open(g_id + "_packrat_parser.py","w",encoding = "utf-8") as f:
        f.write(parser)


