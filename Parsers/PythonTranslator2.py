from enum import Enum
from lark import Lark,Tree,Token
import Config
import bridge_parser

#Gestionar que puede ser un pass!
def translateCommentToPy(com):
    #Si es un pass-endpass, devolverlo sin tocar
    if com.strip().strip('\n')[0:5] == "#pass":
        return com.strip().strip('\n')[5:-8]
    if com.strip()[0:2] == "//": 
        return com.replace("//","#")
    else:
        com = com[3:-3]
        return "\n".join(["#" + x  for x in com.split("\n")])

#Para poder cambiar como se interpreta type_ext segun el contexto---------------------------
class InterpretType(Enum):
    asIs = "as"
    asColon = ":"
    asArrow = "->"

interpret_type= InterpretType.asIs
#-------------------------------------------------------------------------------------------

#Devuelve una tupla con la diferencia
#entre dos cadenas que se supone que
#son la ampliacion una de otra (al final)
#y la original sin la ampliacion
def getDifference(appended,total):
    return (total[0:len(appended)],total[len(appended):])

def translateToPython(t):
    global interpret_type
    print(type(t))
    print(t)
    if isinstance(t,bridge_parser.Token):
        print("ES UN TOKEN!!!!!")
        print(t.value)
    if hasattr(t,"data") and t.data   == 'instructions':
        for child in t.children:
            if hasattr(child,"data") and child.data   == 'instruction':
                #Aplicar el indent actual
                Config.prog_str += Config.indent_str
                translateToPython(child)
                Config.prog_str += Config.instr_sep + "\n"
            elif hasattr(child,"data") and child.data   == 'comment':
                Config.prog_str += translateCommentToPy(child.children[0]) + "\n"
    
    elif hasattr(t,"data") and t.data   == 'instruction': #boolexpr|statement
        translateToPython(t.children[0])

    elif hasattr(t,"data") and t.data   == 'statement':
        translateToPython(t.children[0])

    elif hasattr(t,"data") and t.data   == 'import_1': #"ambit* (import|package)" ID ("as" ID)? (COMMA ID ("as" ID)?)* 
        cont = 0
        while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
            translateToPython(t.children[cont])
            cont += 1
        Config.prog_str += t.children[cont] + ' ' + t.children[cont+1].replace("::",".") + ' '
        cont += 2
        if cont < len(t.children) and t.children[cont] == "as":
            Config.prog_str += t.children[cont] + ' ' + t.children[cont+1].replace("::",".")
            cont += 2
        #Coger resto si lo hay
        while cont < len(t.children):
            Config.prog_str += t.children[cont] + ' ' + t.children[cont+1].replace("::",".")
            cont += 2
            if cont < len(t.children) and t.children[cont] == "as":
                Config.prog_str += t.children[cont] + ' ' + t.children[cont+1].replace("::",".")
                cont += 2

    elif hasattr(t,"data") and t.data   == 'import_2': #ambit* "from" ID "import" (ID|"*") ("as" ID)? 
        cont = 0
        while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
            translateToPython(t.children[cont])
            cont += 1
        Config.prog_str += t.children[cont] + ' ' + t.children[cont+1].replace("::",".") + ' ' + t.children[cont+2] + ' ' + t.children[cont+3].replace("::",".") + ' '
        cont += 4
        if cont < len(t.children):# as ID
            Config.prog_str += t.children[cont] + ' ' + t.children[cont+1].replace("::",".")

    elif hasattr(t,"data") and t.data   == 'line_generic': # "." (boolexpr|ID2|LISP_ID|annot)+
        Config.prog_str += "#Python no acepta line_generic\n"
        
    elif hasattr(t,"data") and t.data   == 'block_st': #("block"|"namespace"|"module") generic? ("for" generic)? ":" instructions "end"
        #print(t)
        Config.prog_str += "#La traduccion a Python no admite block_st por ahora\n"

    elif hasattr(t,"data") and t.data   == 'block2_st': #ID2? "{" instructions "}"
        cont = 0
        while type(t.children[cont]) == Token:
            #Config.prog_str += t.children[cont]
            cont += 1
        translateToPython(t.children[cont])

    elif hasattr(t,"data") and t.data   == 'with_st': #"with" boolexpr type_ext? "do" instructions "end"
        Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])
        if hasattr(t.children[2],"data"):
            translateToPython(t.children[2])
            Config.prog_str += ':\n'
        else:
            Config.prog_str += ':\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(t.children[-2])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]

    elif hasattr(t,"data") and t.data   == 'linq_st': #"from" ID "in" expr ("where" boolexpr)? ("order" "by" boolexpr)? ("select"|"groupby") boolexpr
        Config.prog_str += '['
        translateToPython(t.children[-1])
        Config.prog_str += ' for ' + t.children[1] + ' in '
        translateToPython(t.children[3]) 
        if t.children[4] == 'where':
            Config.prog_str += ' if '
            translateToPython(t.children[5])
            if t.children[6] == "order":
                print("Bridge warning: When translating to Python, order part in linq_st is ignored by now.")
        elif t.children[4] == 'order':
            print("Bridge warning: When translating to Python, order part in linq_st is ignored by now.")
        elif t.children[-2] == 'group':
            print("Bridge warning: When translating to Python, only select is allowed. Group is ignored by now.")
        Config.prog_str += ']'

    elif hasattr(t,"data") and t.data   == 'try_st': # "try" ":" instructions ("catch" (ID type_ext?|"...") ":" instructions)+ ("finally" ":" instructions)? "end"
        #print(t)
        Config.prog_str += t.children[0] + ' ' + t.children[1] + '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(t.children[2])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        cont=3
        while t.children[cont] == "catch":
            Config.prog_str += t.children[cont]
            cont += 1
            if t.children[cont] == "...":
                Config.prog_str += ' '
                cont +=1
            else:
                Config.prog_str += ' ' + t.children[cont]
                cont += 1
                if t.children[cont] != ":":
                    Config.prog_str += ' '
                    translateToPython(t.children[cont])
                    cont += 1
            Config.prog_str += t.children[cont] + '\n' #:
            #Ajuste de indent
            Config.indent_str += "  "
            translateToPython(t.children[cont+1])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            cont += 2
        if t.children[cont] != "end":#Hay finally
            Config.prog_str += t.children[cont] + t.children[cont+1] + '\n'
            #Ajuste de indent
            Config.indent_str += "  "
            translateToPython(t.children[cont+2])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]          

    elif hasattr(t,"data") and t.data   == 'match_st': #"match" boolexpr "with" ("|" boolexpr ("when" boolexpr)? "then" instructions)+ "end"
        temp = Config.prog_str
        childs = t.children[0]
        translateToPython(childs.children[1])
        last,new = getDifference(temp,Config.prog_str)
        Config.prog_str = last
        new = new.strip()
        cont = 3
        while childs.children[cont] == "|":
            Config.prog_str += 'if ' if cont == 3 else 'elif '
            Config.prog_str += new + ' == '
            translateToPython(childs.children[cont+1])
            cont += 2
            if childs.children[cont] == "when":
                Config.prog_str += ' and '
                translateToPython(childs.children[cont+1])
                cont += 2
            Config.prog_str += ':\n'
            #Ajuste de indent
            Config.indent_str += "  "
            translateToPython(childs.children[cont+1])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            cont += 2


    elif hasattr(t,"data") and t.data   == 'break_cont_st': #break_cont_st : ("break"|"continue")
        Config.prog_str += t.children[0]

    elif hasattr(t,"data") and t.data   in ["goto_st","label_st"]: #"goto"|"label" ID
        Config.prog_str += "#Python no admite label ni goto.\n"

    elif hasattr(t,"data") and t.data   == 'pass_st': #pass_st : "pass"
        Config.prog_str += t.children[0] 

    elif hasattr(t,"data") and t.data   in ['assert_st','raise_st']: #"assert" boolexpr,"raise" expr
        Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])

    elif hasattr(t,"data") and t.data   == 'while_st': #while_st : "while"  boolexpr "do" instructions "end" 
        Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])
        Config.prog_str += ' :\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(t.children[3])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]

    elif hasattr(t,"data") and t.data   == 'dowhile_st': # "do" instructions "until" boolexpr "end"
        Config.prog_str += '#Python no tiene el bucle do-while \n'

    elif hasattr(t,"data") and t.data   == 'if_st': #"if" boolexpr "then" instructions "end"
        Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])
        Config.prog_str +=  ':\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(t.children[3])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]

    elif hasattr(t,"data") and t.data   == 'ifelif_else_st': #"if" boolexpr "then" instructions  ("elif" boolexpr "then" instructions)* "else" instructions "end"
        Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])
        Config.prog_str += ':\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(t.children[3])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        cont = 4
        while t.children[cont] == "elif":
            Config.prog_str += Config.indent_str + t.children[cont] + ' '
            translateToPython(t.children[cont+1])
            Config.prog_str += ':\n'
            #Ajuste de indent
            Config.indent_str += "  "
            translateToPython(t.children[cont+3])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            cont += 4
        Config.prog_str += Config.indent_str + 'else:\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(t.children[cont+1])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
     
    elif hasattr(t,"data") and t.data   == 'switch_st': #("switch"|"cond") boolexpr "case" boolexpr "do" instructions ("case" boolexpr "do" instructions)* ("else" instructions)? "end"
        Config.prog_str += Config.indent_str + 'if '
        translateToPython(t.children[3])
        Config.prog_str += ':\n'
        #Ajuste de indent
        Config.indent_str += "    "
        translateToPython(t.children[5])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-4]
        cont = 6
        while t.children[cont] not in ["else","end"]:
            Config.prog_str += Config.indent_str + 'elif '
            translateToPython(t.children[cont+1])
            Config.prog_str += ':\n'
            #Ajuste de indent
            Config.indent_str += "    "
            translateToPython(t.children[cont+3])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-4]
            cont += 4
        #Coger la parte del else si hay
        if t.children[cont] == "else":
            Config.prog_str += Config.indent_str +t.children[cont] + ':\n'
            #Ajuste de indent
            Config.indent_str += "    "
            translateToPython(t.children[cont+1])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-4]
        
    elif hasattr(t,"data") and t.data   == 'type_ext': #ambit* "as" (generic|string) ("as" (generic|string))* ("?"|"!")?
        cont = 0
        while t.children[cont] != "as":
            translateToPython(t.children[cont])
            Config.prog_str += ' '
            cont += 1
        #Config.prog_str += t.children[cont] + ' '
        Config.prog_str += interpret_type.value + ' '
        cont += 1
        translateToPython(t.children[cont])
        cont += 1
        Config.prog_str += ' '
        rest = t.children[cont:]
        if rest != []:
            cont = 0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToPython(pair[1]) 
                Config.prog_str += ' '
        if t.children[-1] in ["?","!"]:
            Config.prog_str += t.children[-1]

    elif hasattr(t,"data") and t.data   == 'generic': #generic : assignable
        translateToPython(t.children[0])
        rest = t.children[1:]
        if rest!=[]:
            Config.prog_str += rest[0]
            translateToPython(rest[1])

    # "generic" "[" boolexpr (("where"|"extends"|"from"|"requires") boolexpr)? (COMMA boolexpr (("where"|"extends"|"from"|"requires") boolexpr)?)* "]"
    elif hasattr(t,"data") and t.data   == 'generic2': 
        cont = 0
        Config.prog_str += ' ' + t.children[0] + t.children[1] #generic [
        translateToPython(t.children[2]) #boolexpr
        cont +=3
        while cont < len(t.children):
            if t.children[cont] == ']':
                Config.prog_str += t.children[cont]
                break
            #elif t.children[cont] in ["where","extends","from","requires"]:
            else:
                Config.prog_str += ' ' + t.children[cont] + ' '
                translateToPython(t.children[cont+1])
                cont+=2

    elif hasattr(t,"data") and t.data   == "return_st": #!return_st : ("return"|"yield"|"await") "from"? boolexpr
        Config.prog_str += t.children[0] + ' '
        if t.children[1] == "from":
            Config.prog_str += t.children[1] + ' '
            translateToPython(t.children[2])
        else:
            translateToPython(t.children[1])

    elif hasattr(t,"data") and t.data   == "fname": #ID | ("++"|"--"|PLUSMIN|TIMESDIV|"()"|"[]"|BOOLOP)
        Config.prog_str += t.children[0] + ' '

    elif hasattr(t,"data") and t.data   == "ambit": #ID2
        Config.prog_str += t.children[0] + ' '

    elif hasattr(t,"data") and t.data   == "annot": #"[" "^" boolexpr_list "]"
        Config.prog_str += "@"
        translateToPython(t.children[2])
        Config.prog_str += "\n"

    elif hasattr(t,"data") and t.data   == "fun_header": #annot* ambit* generic2? "async"? ("fun"|"oper"|"proc")
        cont = 0
        if t.children[0] in ["fun","oper","proc"]:
            Config.prog_str += 'def '
        else:
            if t.children[0] == "async":
                Config.prog_str += t.children[0] + ' ' + t.children[1] + ' '
            elif t.children[0].data == "generic2":
                translateToPython(t.children[0])
                if t.children[1] == "async":
                    Config.prog_str += ' ' + t.children[1] + 'def '
                else:
                    Config.prog_str += 'def  '
            elif t.children[0].data == "ambit" :
                while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":
                    translateToPython(t.children[cont])
                    cont += 1
                if t.children[cont] in ["fun","oper"]:
                    Config.prog_str += 'def '
                elif t.children[cont] == "async":
                    Config.prog_str += ' ' + t.children[cont] + 'def '
                else:
                    translateToPython(t.children[cont])
                    if t.children[cont+1] in ["fun","oper"]:
                        Config.prog_str += 'def '
                    else:
                        Config.prog_str += ' ' + t.children[cont+1] + 'def '
            else: #annot*
                while hasattr(t.children[cont],"data") and t.children[cont].data == "annot":
                    translateToPython(t.children[cont])
                    Config.prog_str += '\n'
                    cont += 1
                if t.children[cont] in ["fun","oper"]:
                    Config.prog_str += 'def '
                elif t.children[cont] == "async":
                    Config.prog_str += ' ' + t.children[cont] + 'def '
                elif hasattr(t.children[cont],"data") and t.children[cont].data == "generic2":
                    translateToPython(t.children[cont])
                    if t.children[cont+1] in ["fun","oper"]:
                        Config.prog_str += 'def '
                    else:
                        Config.prog_str += ' ' + t.children[cont+1] + 'def '
                else:
                    while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":
                        translateToPython(t.children[cont])
                        cont += 1
                    if hasattr(t.children[cont],"data") and t.children[cont].data == "generic2":
                        translateToPython(t.children[cont])
                        cont += 1
                    if t.children[cont] in ["fun","oper"]:
                        Config.prog_str += 'def '
                    else:
                        Config.prog_str += ' ' + t.children[cont] + 'def '

    elif hasattr(t,"data") and t.data   == "fundef": ##fun_header fname ("(" arglist ")" |"()") type_ext? ("throws" ID(COMMA ID)*)? ":" init? instructions? "end"
        temp = Config.prog_str
        translateToPython(t.children[0]) #fun_header
        #Cambio para soporte cython: si hay @cdef o @cpdef, usarlos
        last,new = getDifference(temp,Config.prog_str)
        cython_fun = False
        cy_type=""
        if "@cdef" in new:
            cython_fun = True
            Config.prog_str = last
            if new[-5:] ==" def ":
                new = new[:-5]
            new = new.replace("@cdef","").replace("@","")
            cy_type += new
            Config.prog_str += "cdef##cy_type## "
        elif "@cpdef" in new:
            cython_fun = True
            Config.prog_str = last
            if new[-5:] ==" def ":
                new = new[:-5]
            new = new.replace("@cpdef","").replace("@","")
            cy_type += new
            Config.prog_str += "cpdef##cy_type## "
        elif "@cython" in new:
            cython_fun = True
            Config.prog_str = last + 'def '
            #new = new.replace("@cython","")
        else:
            Config.prog_str += ' '
        translateToPython(t.children[1]) #fname
        cont = 2
        if t.children[2] == "()": #()
            Config.prog_str += t.children[2]
            cont +=1
        else:#(arglist)
            #cambiar interpret_type
            interpret_type = InterpretType.asColon
            Config.prog_str += t.children[2]
            #Si cython_fun es True, interpretar los tipos para ella
            if cython_fun == True:
                temp = Config.prog_str
            translateToPython(t.children[3])
            if cython_fun == True:
                last,new = getDifference(temp,Config.prog_str)
                #Reinterpretar los tipos de los argumentos
                args_new = []
                args = new.split(",")
                for item in args:
                    name,tip = item.split(":")
                    args_new.append(tip + name)
                Config.prog_str = temp + ','.join(args_new) 
            Config.prog_str += t.children[4]
            cont+=3
            #recuperar interpret_type
            interpret_type = InterpretType.asIs
        if t.children[cont] == ":": #:
            Config.prog_str += t.children[cont] + "\n"
            cont +=1
        else: #type_ext? ("throws" ID(COMMA ID)*)?
            if hasattr(t.children[cont],"data") and t.children[cont].data == "type_ext":
                temp = Config.prog_str
                #cambiar interpret_type
                interpret_type = InterpretType.asArrow
                Config.prog_str += ' '
                translateToPython(t.children[cont])
                cont += 1
                #recuperar interpret_type
                interpret_type = InterpretType.asIs
                #print("cy_type: %s"%cy_type)
                if cython_fun == True:
                   last,new = getDifference(temp,Config.prog_str)
                   Config.prog_str = last
                   cy_type += new.strip().replace("->","").replace(" as "," ")
                #Poner el valor de cy_type si lo hay
                if "##cy_type##" in Config.prog_str:
                    Config.prog_str = Config.prog_str.replace("##cy_type##",cy_type)
                else:
                    if cython_fun == True:
                        Config.prog_str += new.replace(" as "," ")
            if t.children[cont] == ":":
                Config.prog_str += t.children[cont] + "\n"
                cont += 1
            else: #throws
                Config.prog_str += t.children[cont] + ' ' + t.children[cont+1]
                cont += 2
                while t.children[cont] == ",":
                    Config.prog_str += t.children[cont] + t.children[cont+1]
                    cont += 2
                Config.prog_str += t.children[cont] + "\n"
                cont += 1
        if t.children[cont] == "end":#Funcion vacia
            Config.prog_str += "\n"
        else:
            #mirar si hay init
            if hasattr(t.children[cont],"data") and t.children[cont].data == "init":
                translateToPython(t.children[cont])
                cont += 1
            #Ajustar indent
            Config.indent_str += "  "
            translateToPython(t.children[cont])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]

    elif hasattr(t,"data") and t.data   == "init": #"init" block2_st
        #Config.prog_str += Config.indent_str + ' ' + t.children[0]
        translateToPython(t.children[1])
        Config.prog_str += "\n" + Config.indent_str

    elif hasattr(t,"data") and t.data   == "object_header": # annot* ambit* generic2? ("class" |"interface" | "trait" | "enum"|"struct")
        if t.children[0] in ["class","interface","trait","enum","struct","union"]:
            Config.prog_str += 'class '
        elif t.children[0].data == "generic2":
            translateToPython(t.children[0])
            Config.prog_str += 'class '
        else: #El paquete completo
            for item in t.children[:-1]:
                translateToPython(item)
            Config.prog_str += 'class '

    elif hasattr(t,"data") and t.data   == "inherit": #(("extends"|"implements") ID)+
        items = [x for x in t.children[1:] if x!="extends"and x!="implements"]
        aux = ""
        for item in items:
            aux += item + ','
        if aux != "":
            Config.prog_str += "(" + aux[:-1] + ")"

    elif hasattr(t,"data") and t.data   == "fld_list": #((ambit* ID type_ext? ("=" boolexpr)?) | comment | get_set | (line_generic ";") )+
        cont = 0
        while cont < len(t.children):
            if hasattr(t.children[cont],"data") and t.children[cont].data in ["comment","get_set"]:
                Config.indent_str += "    "
                translateToPython(t.children[cont])
                cont += 1
                Config.prog_str += "\n"
                Config.indent_str = Config.indent_str[:-4]
                continue
            if hasattr(t.children[cont],"data") and t.children[cont].data == "line_generic":
                Config.indent_str += "    "
                translateToPython(t.children[cont])
                Config.prog_str += t.children[cont+1]
                cont += 2
                Config.prog_str += "\n"
                Config.indent_str = Config.indent_str[:-4]
                continue
            Config.prog_str += "  "
            while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
                translateToPython(t.children[cont])
                cont += 1
            Config.prog_str += t.children[cont]#ID
            cont += 1
            #mirar si hay type_ext
            if cont < len(t.children) and hasattr(t.children[cont],"data") and t.children[cont].data =="type_ext":
                Config.prog_str += ' '
                translateToPython(t.children[cont])
                cont += 1
            if cont < len(t.children) and t.children[cont] == "=": #= boolexpr
                Config.prog_str += ' ' + t.children[cont] + ' '
                translateToPython(t.children[cont+1])
                cont += 2
            Config.prog_str += "\n"

    elif hasattr(t,"data") and t.data   == "get_set": #ambit* "get" block2_st? (ambit* "set" (("(" ID ")")? block2_st)?)?
        Config.prog_str += "#Python no admite la seccion get/set\n"

    elif hasattr(t,"data") and t.data   == "object_st": #object_header ID? inherit? ":" block2_st? fld_list? fundef_st* "end"
        cont = 0
        translateToPython(t.children[0])
        if t.children[1] == ":":
            Config.prog_str += t.children[1] + '\n'
            cont = 2
        elif hasattr(t.children[1],"data") and t.children[1].data == "inherit":
            #Config.prog_str += "("
            translateToPython(t.children[1])
            Config.prog_str += t.children[2] + '\n'
            cont = 3
        else:
            Config.prog_str += t.children[1] + ' '
            if t.children[2] == ":":
                Config.prog_str += t.children[2] + "\n"
                cont = 3
            else:
                translateToPython(t.children[2])
                Config.prog_str += t.children[3] + "\n"
                cont = 4
        if hasattr(t.children[cont],"data") and t.children[cont].data == "block2_st":
            Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToPython(t.children[cont])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            Config.prog_str +=  "\n" 
            cont += 1

        if hasattr(t.children[cont],"data") and t.children[cont].data == "fld_list":
            translateToPython(t.children[cont])
            Config.prog_str += "\n"
            cont += 1
     
        for item in t.children[cont : -1]: #fundef*
            Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToPython(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
        #Config.prog_str += "\n" + Config.indent_str + t.children[-1]

    elif hasattr(t,"data") and t.data   == "type_tuple": #"type" ID "is" generic ("," generic)* type_ext? fundef_st* "end" 
        Config.prog_str += '#La traduccion a Python no soporta type_tuple por ahora\n'

    elif hasattr(t,"data") and t.data   == "type_union": #"type" ID "is" (ID "of" generic)+ fundef_st* "end" 
        Config.prog_str += '#La traduccion a Python no soporta type_union por ahora\n'

    elif hasattr(t,"data") and t.data   == "type_record": #"type" ID "is" "{" pair (COMMA pair)* fundef_st* "}" "end" 
        Config.prog_str += '#La traduccion a Python no soporta type_record por ahora\n'

    elif hasattr(t,"data") and t.data   == "type_variant_record": #"type" ID "is" "record" ((ID ":" generic)|switch_st)+ fundef_st*  "end" 
        cont = 0
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' ' + t.children[2] + ' ' + t.children[3] + "\n  "
        cont = 4

        while t.children[cont] != "end" or (hasattr(t.children[cont],"data") and  t.children[cont].data != "fundef_st"):
            if type(t.children[cont]) == Token:
                Config.prog_str += t.children[cont] + t.children[cont+1]
                translateToPython(t.children[cont+2])
                Config.prog_str += "\n" + Config.indent_str
                cont += 3
            else:
                translateToPython(t.children[cont])
                cont += 1

        for item in t.children[cont : -1]:
            #Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToPython(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            #Config.prog_str = Config.prog_str[:-3] + "  " + Config.prog_str[-3:] + "\n" 
        Config.prog_str += "\n" + Config.indent_str + t.children[-1]

    elif hasattr(t,"data") and t.data   == "lisp_st": #"$" "(" (boolexpr | LISP_ID | lisp_st | comment)+ ")"
        Config.prog_str += "#Python no admite lisp_st\n"

    elif hasattr(t,"data") and t.data   == "comment": # COMMENT | COMMENT3 | PASS
        Config.prog_str += translateCommentToPy(t.children[0]) + "\n"

    elif hasattr(t,"data") and t.data   == 'typedef_st': #("typedef"|"using") boolexpr ("as" boolexpr)?     
        Config.prog_str += "ctypedef "
        temp = Config.prog_str
        translateToPython(t.children[1])
        if Config.prog_str[-1] == "^":
            Config.prog_str = Config.prog_str[:-1] + "*"
        if len(t.children) > 2:
            Config.prog_str += ' '
            translateToPython(t.children[3])
        
    elif hasattr(t,"data") and t.data   == 'boolexpr_list': #boolexpr (COMMA boolexpr)*
        #procesar primera instruccion
        translateToPython(t.children[0])
        rest = t.children[1:]
        if rest != []:
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToPython(pair[1]) 

    elif hasattr(t,"data") and t.data   == 'foreach_st': #"foreach" ("const")? ID type_ext? (COMMA ("const")? ID type_ext?)* "in" boolexpr_list "do" instructions "end"
        Config.prog_str += 'for '
        #Coger la parte fija:"in" boolexpr_list "do" instructions "end"
        fixed = t.children[-5:]
        #Parte variable: 1 hasta -5
        if Config.prog_str[-1] != ' ': Config.prog_str += ' '
        variable = t.children[1:-5]
        for item in  variable:
            if type(item) == Token:
                Config.prog_str += item + ' '
            else:
                translateToPython(item)
        #Recorrer parte variable
        #Meter parte fija
        Config.prog_str += ' ' + fixed[0] + ' ' #in
        translateToPython(fixed[1]) #boolexpr_list
        Config.prog_str += ':\n' #do
        #Ajuste de indent
        Config.indent_str += "  "
        translateToPython(fixed[3])#instructions, ignoramos end
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]

    #El for deberia aceptar en la primera opcion i as generic
    elif hasattr(t,"data") and t.data   == 'for_st': #for_st: "for" (boolexpr type_ext? | ":" | block2_st) ";" (boolexpr | ":" | block2_st) ";" (boolexpr | ":" | block2_st) "do" instructions "end"
        Config.prog_str += "#Python no posee el bucle for de C/C++/Java\n"

    elif hasattr(t,"data") and t.data   == "let_st": #("let"|"const"|"ref"|"var") ID ("," ID)* type_ext? ("=" boolexpr)*
        temp = Config.prog_str 
        cont = 0
        varname = t.children[1]
        #Cambiar el ^ final si lo hay por *
        varname = varname.replace("^","*")
        #print("varname: " + varname)
        morevars = ""
        Config.prog_str += varname
        cont+=2
        while cont < len(t.children) and t.children[cont] == ",":
            Config.prog_str += t.children[cont] + t.children[cont+1]
            morevars += t.children[cont] + t.children[cont+1]
            morevars =  morevars.replace("^","*")
            cont+=2
        #type_ext?
        if cont < len(t.children) and hasattr(t.children[cont],"data") and t.children[cont].data == "type_ext":
            Config.prog_str = temp
            Config.prog_str += ' '
            translateToPython(t.children[cont])
            cont+=1
            #Si hay cdef, recomponer la cadena
            #Cogemos todo lo de ambit que 
            #no sea marcador
            # y la cadena de as...
            last,new = getDifference(temp,Config.prog_str)
            #print(f"last:{last}")
            #print(f"new:{new}")
            if "@cdef" in new:
                new = new.replace("@cdef","").replace("@","")
                Config.prog_str = last
                typs = new.split(" as ")
                Config.prog_str += 'cdef' + ' '.join(typs[:-1]) + ' ' + typs[-1] + ' ' + varname + (morevars if morevars!="" else "")
            else:
                Config.prog_str = last + varname + " :" +  new.replace("as ","")

        if cont < len(t.children):
            while cont < len(t.children):
                Config.prog_str += ' ' + t.children[cont] + ' '
                translateToPython(t.children[cont+1])
                cont += 2

    elif hasattr(t,"data") and t.data   == "let_in_st": #"let" "in" boolexpr_list ":" instructions "end"
        Config.prog_str += "#Python no soporta let_in_st por ahora\n"
        
    elif hasattr(t,"data") and t.data   in ['assert','raise']: #assert_st : "assert"/"raise" boolexpr
        Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])

    elif hasattr(t,"data") and t.data   == 'boolexpr': #orexp ( ("and"|"&&"|"&") orexp)*))
        #Seguir con la primera instruccion que siempre existe
        translateToPython(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToPython(pair[1]) 
    
    elif hasattr(t,"data") and t.data   == 'orexp': #notexp ( ("or"|"||"|"|") notexp)*
        #Seguir con la primera instruccion que siempre existe
        translateToPython(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToPython(pair[1]) 
    
    elif hasattr(t,"data") and t.data   == 'notexp': #("not"|"!") cmpexp | cmpexp
        #Seguir con la primera instruccion que siempre existe
        if len(t.children) == 1:
            translateToPython(t.children[0])
        else: #Hay mas: op instr
            Config.prog_str += ' ' + t.children[0] + ' '
            translateToPython(t.children[1])
    
    elif hasattr(t,"data") and t.data   == 'cmpexp': #expr (BOOLOP expr)*
        #Seguir con la primera instruccion que siempre existe
        translateToPython(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToPython(pair[1]) 
    
    elif hasattr(t,"data") and t.data   == 'expr': #term (PLUSMIN term)*
        #Seguir con la primera instruccion que siempre existe
        translateToPython(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToPython(pair[1]) 
    
    elif hasattr(t,"data") and t.data   == 'term': #exp (TIMESDIV exp)*
        #Seguir con la primera instruccion que siempre existe
        translateToPython(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToPython(pair[1])  
    
    elif hasattr(t,"data") and t.data   == 'exp': #factor (("**"|"."|"member"|"is") factor)*
        #Seguir con la primera instruccion que siempre existe
        translateToPython(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                sep = ' ' if pair[0] in ["**","member","is"] else ''
                Config.prog_str += sep + (pair[0] if pair[0] in["is","**","."] else "in") + sep
                translateToPython(pair[1]) 
    
    elif hasattr(t,"data") and t.data   in ['_string','number','empty_list','empty_tuple']:
        if hasattr(t,"data") and t.data   == '_string':
            if t.children[0].children[0][0] == "@":
                Config.prog_str += t.children[0].children[0][1:]
            else:
                Config.prog_str += t.children[0].children[0]
        else:
            Config.prog_str += t.children[0]

    elif hasattr(t,"data") and t.data  =='string':
        Config.prog_str += t.children[0]  

    elif hasattr(t,"data") and t.data  =='_regex':
        Config.prog_str += "#La traduccion a Python no soporta _regex por ahora.\n"        

    elif hasattr(t,"data") and t.data   == 'plusmin': #(PLUSMIN|"sizeof"|"typeof") expr 
        Config.prog_str += t.children[0]
        if t.children[0] in ["sizeof","typeof"]:
            Config.prog_str += ' '
        translateToPython(t.children[1])

    elif hasattr(t,"data") and t.data   == 'assignation': #assignable ("+="|"-="|"*="|"/="|"|="|"&="|"=") boolexpr
        #Seguir con la primera instruccion que siempre existe
        #print("En assignation: %s" % t)
        translateToPython(t.children[0])
        Config.prog_str += ' ' + t.children[1] + ' '
        translateToPython(t.children[2])

    elif hasattr(t,"data") and t.data   == '_assignable':
        translateToPython(t.children[0])

    # ("&"|"$")* ID (("[" boolexpr? (":" boolexpr?)* "]") |"[]")* ("::" ID)* ("++"|"--"|"...")*
    elif hasattr(t,"data") and t.data   == 'assignable': 
        cont = 0
        if t.children[0] in ["&","$"]:
            while t.children[cont] in ["&","$"]:
                Config.prog_str+= "*"
                cont+=1
            Config.prog_str += t.children[cont]
            cont+=1
        else:
            Config.prog_str+=t.children[0]
            cont+=1
        #print("len(t),cont,t.children[cont] aqui: %s,%s" % (len(t.children),cont))

        #Ver si hay parte boolexpr
        while cont< len(t.children) and t.children[cont] in ["[","[]"]:
            if t.children[cont] == "[]":
                Config.prog_str += t.children[cont]
                cont+=1
                #Si estamos en el final, nos vamos
                if cont == len(t.children):
                    break
            else:
                Config.prog_str += t.children[cont] #[
                cont+=1
                #Si estamos en el final, nos vamos
                #print("len(t),cont aqui2: %s,%s" % (len(t.children),cont))
                if t.children[cont] =="]" and cont == len(t.children):
                    Config.prog_str += t.children[cont]
                    break
                if t.children[cont]!= ":": #Hay boolexpr (revisar esto)
                    translateToPython(t.children[cont])
                    cont+=1
                if t.children[cont] =="]" and cont == len(t.children):
                    Config.prog_str += t.children[cont]
                    break
                #coger resto si hay
                while t.children[cont] == ":": 
                    Config.prog_str += t.children[cont] #:
                    cont += 1
                    if t.children[cont] not in ["]",":"]: #hay boolexpr
                        translateToPython(t.children[cont])
                        cont += 1
                #Coger ] final???????
                #Config.prog_str += t.children[cont]
                #print("al final del while")
        #Coger ::ID si lo hay
        while cont < len(t.children) and t.children[cont] == "::":
            Config.prog_str += t.children[cont]
            Config.prog_str += t.children[cont+1]
            cont += 2
        #Coger el resto si lo hay
        while cont < len(t.children):
            if hasattr(t.children[cont],"data"):
                translateToPython(t.children[cont])
            else:
                Config.prog_str+= t.children[cont]
            cont += 1
        
    elif hasattr(t,"data") and t.data   in ['list','dict']: # "[" boolexpr ("," boolexpr)* "]"   
        #print(t.children) 
        Config.prog_str += t.children[0]
        #procesar primera instruccion
        translateToPython(t.children[1]) #]|}
        sufix = t.children[-1]
        rest = t.children[2:-1]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToPython(pair[1]) 
        Config.prog_str += sufix

    elif hasattr(t,"data") and t.data   == 'list_comprehension': #"[" boolexpr "for" ID(COMMA ID)* "in" boolexpr ("if" boolexpr)? "]" 
        Config.prog_str += t.children[0]
        translateToPython(t.children[1])
        Config.prog_str += ' ' + t.children[2] + ' ' + t.children[3]
        cont = 4
        while t.children[cont] != "in":
            Config.prog_str += t.children[cont] + t.children[cont+1]
            cont += 2
        Config.prog_str += ' ' + t.children[cont] + ' '
        translateToPython(t.children[cont+1])
        cont+=2
        if t.children[cont]!="]": #hay parte if
            Config.prog_str += ' ' + t.children[cont] + ' '
            translateToPython(t.children[cont+1])
        Config.prog_str += t.children[-1]

    elif hasattr(t,"data") and t.data   == 'tuple': # "(" boolexpr COMMA boolexpr (COMMA boolexpr)* ")" 
        Config.prog_str += t.children[0]
        #procesar primera instruccion
        translateToPython(t.children[1]) #]|}
        Config.prog_str += t.children[2]
        translateToPython(t.children[3])
        rest = t.children[4:-1]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToPython(pair[1]) 
        Config.prog_str += t.children[-1]

    elif hasattr(t,"data") and t.data   == 'array': #ID? "{" boolexpr (COMMA boolexpr)* "}"    
        cont = 0
        if t.children[0] == "{":
            Config.prog_str += t.children[0] + ' '
            cont = 1
        else:
            Config.prog_str += t.children[0] + t.children[1] + ' '
            cont = 2 
        translateToPython(t.children[cont])
        cont += 1
        while cont < len(t.children)-1:
            Config.prog_str += t.children[cont]
            translateToPython(t.children[cont+1])
            cont += 2
        Config.prog_str += t.children[-1]

    elif hasattr(t,"data") and t.data   == 'empty_dict': #ID? "{}"     
        if t.children[0] == "{}":
            Config.prog_str += t.children[0] + " "
        else:
            Config.prog_str += t.children[0] + t.children[1] + " "

    elif hasattr(t,"data") and t.data   == 'pair_number':#NUMBER ":" boolexpr
        Config.prog_str += t.children[0] + t.children[1]
        translateToPython(t.children[2])

    elif hasattr(t,"data") and t.data   == 'pair_string':#string ":" boolexpr
        translateToPython(t.children[0])
        Config.prog_str += t.children[1]
        translateToPython(t.children[2])
    
    elif hasattr(t,"data") and t.data   == 'pair_id':#ID ":" boolexpr
        Config.prog_str += t.children[0] + t.children[1]
        translateToPython(t.children[2])

    elif hasattr(t,"data") and t.data   == 'pre_incr': #("++"|"--") expr 
        Config.prog_str += "#Python no tiene los operadores ++ o --\n"

    elif hasattr(t,"data") and t.data   == 'funcall': #assignable "(" arglist ")" 
        translateToPython(t.children[0])
        Config.prog_str += t.children[1]
        translateToPython(t.children[2])
        Config.prog_str += t.children[3]

    elif hasattr(t,"data") and t.data   == 'funcall_empty': #assignable "()" 
        translateToPython(t.children[0])
        Config.prog_str += t.children[1]

    elif hasattr(t,"data") and t.data   == 'expr_funcall': # "(" boolexpr ")" "(" arglist ")" 
        Config.prog_str += t.children[0]
        translateToPython(t.children[1])
        Config.prog_str += t.children[2] + t.children[3]
        translateToPython(t.children[4])
        Config.prog_str += t.children[5]

    elif hasattr(t,"data") and t.data   == 'expr_funcall_empty': #"(" boolexpr ")" "()" 
        Config.prog_str += t.children[0]
        translateToPython(t.children[1])
        Config.prog_str += t.children[2] + t.children[3]

    elif hasattr(t,"data") and t.data   == 'arglist': #argitem (COMMA argitem)*
        translateToPython(t.children[0])
        rest = t.children[1:]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToPython(pair[1])

    elif hasattr(t,"data") and t.data   == 'argitem': #ambit* boolexpr type_ext? (("="|":=") boolexpr)? | "..." | ".."
        if type(t.children[0] ) == Token : #"..."|".."
            Config.prog_str += t.children[0]
        else:
            cont = 0
            while t.children[cont].data =="ambit":
                translateToPython(t.children[cont])
                Config.prog_str += ' '
                cont += 1
            translateToPython(t.children[cont])
            cont += 1
            rest = t.children[cont:]
            if rest != []:
                if len(rest) == 1: #type_ext?
                    Config.prog_str += ' '
                    translateToPython(rest[0])
                    Config.prog_str += ' '
                elif len(rest) == 2:
                    Config.prog_str += rest[0]
                    translateToPython(rest[1])
                else: #todo
                    Config.prog_str += ' '
                    translateToPython(rest[0])
                    Config.prog_str += ' '
                    Config.prog_str += rest[1]
                    translateToPython(rest[2])

    elif hasattr(t,"data") and t.data   == 'simple_conditional': #"?" boolexpr "->" boolexpr  
        Config.prog_str += "#Python no admite simple_conditional"

    elif hasattr(t,"data") and t.data   == 'double_conditional': # "?" boolexpr "->" boolexpr ":" boolexpr
        translateToPython(t.children[3])
        Config.prog_str += " if " 
        translateToPython(t.children[1])
        Config.prog_str += " else "
        translateToPython(t.children[5])

    elif hasattr(t,"data") and t.data   == 'range': # "from" expr "to" expr ("in" expr)?
        Config.prog_str += 'range('
        translateToPython(t.children[1])
        Config.prog_str += ','
        translateToPython(t.children[3])
        if len(t.children) >4 : 
            Config.prog_str += ','
            translateToPython(t.children[5])
        Config.prog_str += ')'

    elif hasattr(t,"data") and t.data   == 'cast': # "(" type_ext ")" expr 
        Config.prog_str += t.children[0]
        translateToPython(t.children[1])
        Config.prog_str += ' ' + t.children[2]
        translateToPython(t.children[3])

    elif hasattr(t,"data") and t.data   == 'functional': # ("map"|"filter"|"reduce"|"group") expr "in" expr ("from" expr)?
        Config.prog_str += t.children[0] + '('
        translateToPython(t.children[1])
        Config.prog_str += ','
        translateToPython(t.children[3])
        if len(t.children) >4 : 
            Config.prog_str += ', initializer='
            translateToPython(t.children[5])
        Config.prog_str += ')'

    elif hasattr(t,"data") and t.data   == 'fundef_anonym': #"@"( "()" | "(" arglist ")") type_ext? block2_st
        Config.prog_str += "lambda "
        cont = 1
        if t.children[1] == "()":
            Config.prog_str += " : "
            cont += 1
        else:
            #Config.prog_str += t.children[1]
            translateToPython(t.children[2])
            Config.prog_str += " : "
            cont += 3
        if t.children[cont].data == "type_ext":
            Config.prog_str += ' '
            translateToPython(t.children[cont])
            Config.prog_str += ' '
            cont += 1
        translateToPython(t.children[cont])
        if Config.prog_str[-1] =='\n': Config.prog_str = Config.prog_str[:-1]
        
    elif hasattr(t,"data") and t.data   == 'new': #"new" generic ("()" | "(" arglist? ")")?  
        #Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])
        if t.children[2] == "()":
            Config.prog_str += t.children[2]
        else:
            Config.prog_str += t.children[2]
            translateToPython(t.children[3])
            Config.prog_str += t.children[4]

    elif hasattr(t,"data") and t.data   == 'new_class': #"new" object_st 
        #Config.prog_str += t.children[0] + ' '
        translateToPython(t.children[1])

    elif hasattr(t,"data") and t.data   == "new_record": # "new" "{" pair (COMMA pair)* "}" 
        #print(t.children) 
        Config.prog_str += t.children[1]
        #procesar primera instruccion
        translateToPython(t.children[2])
        sufix = t.children[-1]
        rest = t.children[3:-1]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToPython(pair[1]) 
        Config.prog_str += sufix

    elif hasattr(t,"data") and t.data   == 'paren_boolexp': #"(" boolexpr ")"      
        Config.prog_str += t.children[0]
        translateToPython(t.children[1])
        Config.prog_str += t.children[2]

    elif hasattr(t,"data") and t.data   == 'fact_arroba': #"@" ID2+ boolexpr     
        for item in t.children[1:-1]:
            Config.prog_str += item[1:] + ' '
        translateToPython(t.children[-1])

    elif hasattr(t,"data") and t.data   == 'block3': #"[" ID2* "]" "{" instructions "}"  
        Config.prog_str += "#La traduccion a a Python no permite block3\n"

    else:
        raise SyntaxError('Unknown instruction: %s' % hasattr(t,"data") and t.data  )