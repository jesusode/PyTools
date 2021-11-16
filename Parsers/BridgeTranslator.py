from lark import Lark,Tree,Token
import Config


def translateToBridge(t):
    if t.data == 'instructions':
        for child in t.children:
            if child.data == 'instruction':
                #Aplicar el indent actual
                Config.prog_str += Config.indent_str
                translateToBridge(child)
                Config.prog_str += Config.instr_sep + "\n"
            elif child.data == 'comment':
                Config.prog_str += child.children[0] + '\n'
    
    elif t.data == 'instruction': #boolexpr|statement
        translateToBridge(t.children[0])

    elif t.data == 'statement':
        translateToBridge(t.children[0])

    elif t.data == 'import_1': #"(import"|"package" ID ("as" ID)? (COMMA ID ("as" ID)?)* 
        cont = 0
        while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
            translateToBridge(t.children[cont])
            cont += 1
        Config.prog_str += t.children[cont] + ' ' + t.children[cont+1] + ' '
        cont += 2
        if cont < len(t.children) and t.children[cont] == "as":
            Config.prog_str += t.children[cont] + ' ' + t.children[cont+1]
            cont += 2
        #Coger resto si lo hay
        while cont < len(t.children):
            Config.prog_str += t.children[cont] + ' '+ t.children[cont+1]
            cont += 2
            if cont < len(t.children) and t.children[cont] == "as":
                Config.prog_str += t.children[cont] + ' ' + t.children[cont+1]
                cont += 2

    elif t.data == 'import_2': #"from" ID "import" (ID|"*") ("as" ID)? 
        cont = 0
        while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
            translateToBridge(t.children[cont])
            cont += 1
        Config.prog_str += t.children[cont] + ' ' + t.children[cont+1] + ' ' + t.children[cont+2] + ' ' + t.children[cont+3] + ' '
        cont += 4
        if cont < len(t.children):# as ID
            Config.prog_str += t.children[cont] + ' ' + t.children[cont+1]

    elif t.data == 'line_generic': # "." (boolexpr|ID2|LISP_ID|annot)+
        if hasattr(t.children[0],"data"):
            t = t.children[0]
        Config.prog_str += t.children[0] + ' '
        for item in t.children[1:]:
            if hasattr(item,"data"):
                translateToBridge(item)
                Config.prog_str += ' '
            else:
                Config.prog_str += item + ' '
    
    elif t.data == 'block_st': #("block"|"namespace"|"module") generic? ("for" generic)? ":" instructions "end"
        #print(t)
        Config.prog_str += t.children[0] + ' '
        if t.children[1] == ':':
            Config.prog_str += t.children[1] + '\n'
        elif t.children[1] == 'for':
            Config.prog_str += ' ' + t.children[1] + ' '
            translateToBridge(t.children[2])
            Config.prog_str += t.children[3] + '\n'
        else: #todo
            translateToBridge(t.children[1])
            if t.children[2] == 'for':
                Config.prog_str += ' ' +  t.children[2] + ' '
                translateToBridge(t.children[3])
                Config.prog_str += t.children[4] + '\n'
            else:
                Config.prog_str += t.children[2] + '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[-2])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[-1]

    elif t.data == 'block2_st': #ID2? "{" instructions "}"
        cont = 0
        while type(t.children[cont]) == Token:
            Config.prog_str += t.children[cont]
            cont += 1
        Config.prog_str += '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[cont])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[-1]

    elif t.data == 'with_st': #"with" boolexpr type_ext? "do" instructions "end"
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        if hasattr(t.children[2],"data"):
            translateToBridge(t.children[2])
            Config.prog_str += ' ' + t.children[3] + ' \n'
        else:
            Config.prog_str += ' ' +  t.children[2] + ' \n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[-2])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += t.children[-1]

    elif t.data == 'linq_st': #"from" ID "in" expr ("where" boolexpr)? ("order" "by" boolexpr)? ("select"|"groupby") boolexpr
        #print(t)
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' ' + t.children[2] + ' '
        translateToBridge(t.children[3])
        if t.children[4] == 'where':
            Config.prog_str += ' ' + t.children[4] + ' '
            translateToBridge(t.children[5])
            if t.children[6] == "order":
               Config.prog_str += ' ' + t.children[6] + ' ' + t.children[7] + ' ' 
               translateToBridge(t.children[8])
        elif t.children[4] == 'order':
            Config.prog_str += ' ' + t.children[4] + ' ' + t.children[5] + ' '
            translateToBridge(t.children[6])
        Config.prog_str += ' ' +  t.children[-2] + ' '
        translateToBridge(t.children[-1])

    elif t.data == 'try_st': # "try" ":" instructions ("catch" (ID type_ext?|"...") ":" instructions)+ ("finally" ":" instructions)? "end"
        #print(t)
        Config.prog_str += t.children[0] + ' ' + t.children[1] + '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[2])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        cont=3
        while t.children[cont] == "catch":
            Config.prog_str += t.children[cont]
            cont += 1
            if t.children[cont] == "...":
                Config.prog_str += ' ' + t.children[cont]
                cont +=1
            else:
                Config.prog_str += ' ' + t.children[cont]
                cont += 1
                if t.children[cont] != ":":
                    Config.prog_str += ' '
                    translateToBridge(t.children[cont])
                    cont += 1
            Config.prog_str += t.children[cont] + '\n' #:
            #Ajuste de indent
            Config.indent_str += "  "
            translateToBridge(t.children[cont+1])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            cont += 2
        if t.children[cont] != "end":#Hay finally
            Config.prog_str += t.children[cont] + t.children[cont+1] + '\n'
            #Ajuste de indent
            Config.indent_str += "  "
            translateToBridge(t.children[cont+2])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]          
        Config.prog_str += Config.indent_str + t.children[-1]

    elif t.data == 'match_st': #"match" boolexpr "with" ("|" boolexpr ("when" boolexpr)? "then" instructions)+ "end"
        t= t.children[0]
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2] + '\n'
        cont = 3
        while t.children[cont] == "|":
            Config.prog_str += ' ' + t.children[cont] + ' '
            translateToBridge(t.children[cont+1])
            cont += 2
            if t.children[cont] == "when":
                Config.prog_str += ' ' +  t.children[cont] + ' '
                translateToBridge(t.children[cont+1])
                cont += 2
            Config.prog_str += ' ' + t.children[cont] + ' '
            #Ajuste de indent
            Config.indent_str += "  "
            translateToBridge(t.children[cont+1])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            cont += 2
        Config.prog_str += Config.indent_str + t.children[-1]

    elif t.data == 'break_cont_st': #break_cont_st : ("break"|"continue")
        Config.prog_str += t.children[0]

    elif t.data in ["goto_st","label_st"]: #"goto"|"label" ID
        Config.prog_str += t.children[0] + ' ' +  t.children[1]

    elif t.data == 'pass_st': #pass_st : "pass"
        Config.prog_str += t.children[0] 

    elif t.data in ['assert_st','raise_st']: #"assert" boolexpr,"raise" expr
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])

    elif t.data == 'while_st': #while_st : "while"  boolexpr "do" instructions "end" 
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += ' :\n'#Para Python,cambiar para resto
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[3])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[-1]

    elif t.data == 'dowhile_st': # "do" instructions "until" boolexpr "end"
        Config.prog_str += t.children[0] + ' \n'
        #Ajuste de indent
        Config.indent_str += "  "
        #print(t.children[1])
        translateToBridge(t.children[1])
        Config.prog_str += t.children[2] + ' '#
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        translateToBridge(t.children[3])
        Config.prog_str += ' ' +  Config.indent_str + t.children[-1]

    elif t.data == 'if_st': #"if" boolexpr "then" instructions "end"
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2] + '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[3])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[4]

    elif t.data == 'ifelif_else_st': #"if" boolexpr "then" instructions  ("elif" boolexpr "then" instructions)* "else" instructions "end"
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2] + '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[3])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        cont = 4
        while t.children[cont] == "elif":
            Config.prog_str += Config.indent_str + t.children[cont] + ' '
            translateToBridge(t.children[cont+1])
            Config.prog_str += ' ' +  t.children[cont+2] + '\n'
            #Ajuste de indent
            Config.indent_str += "  "
            translateToBridge(t.children[cont+3])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            cont += 4
        Config.prog_str += Config.indent_str + t.children[cont] + '\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[cont+1])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[cont+2]
        
    elif t.data == 'switch_st': #("switch"|"cond") boolexpr "case" boolexpr "do" instructions ("case" boolexpr "do" instructions)* ("else" instructions)? "end"
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += '\n  ' + Config.indent_str +  t.children[2] + ' '
        translateToBridge(t.children[3])
        Config.prog_str += ' ' + Config.indent_str +  t.children[4] + '\n'
        #Ajuste de indent
        Config.indent_str += "    "
        translateToBridge(t.children[5])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-4]
        cont = 6
        while t.children[cont] not in ["else","end"]:
            Config.prog_str += '\n  ' + Config.indent_str + t.children[cont] + ' '
            translateToBridge(t.children[cont+1])
            Config.prog_str += ' ' + Config.indent_str +  t.children[cont+2] + '\n'
            #Ajuste de indent
            Config.indent_str += "    "
            translateToBridge(t.children[cont+3])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-4]
            cont += 4
        #Coger la parte del else si hay
        if t.children[cont] == "else":
            Config.prog_str += Config.indent_str + '  ' +  t.children[cont] + '\n'
            #Ajuste de indent
            Config.indent_str += "    "
            translateToBridge(t.children[cont+1])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-4]
        Config.prog_str += '  ' + Config.indent_str + t.children[-1]
        
    elif t.data == 'type_ext': #ambit* "as" (generic|string) ("as" (generic|string))* ("?"|"!")?
        cont = 0
        while t.children[cont] != "as":
            translateToBridge(t.children[cont])
            Config.prog_str += ' '
            cont += 1
        Config.prog_str += t.children[cont] + ' '
        cont += 1
        translateToBridge(t.children[cont])
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
                translateToBridge(pair[1]) 
                Config.prog_str += ' '
        if t.children[-1] in ["?","!"]:
            Config.prog_str += t.children[-1]

    elif t.data == 'generic': #generic : assignable
        translateToBridge(t.children[0])
        rest = t.children[1:]
        if rest!=[]:
            Config.prog_str += rest[0]
            translateToBridge(rest[1])

    # "generic" "[" boolexpr (("where"|"extends"|"from"|"requires") boolexpr)? (COMMA boolexpr (("where"|"extends"|"from"|"requires") boolexpr)?)* "]"
    elif t.data == 'generic2': 
        cont = 0
        Config.prog_str += ' ' + t.children[0] + t.children[1] #generic [
        translateToBridge(t.children[2]) #boolexpr
        cont +=3
        while cont < len(t.children):
            if t.children[cont] == ']':
                Config.prog_str += t.children[cont]
                break
            #elif t.children[cont] in ["where","extends","from","requires"]:
            else:
                Config.prog_str += ' ' + t.children[cont] + ' '
                translateToBridge(t.children[cont+1])
                cont+=2

    elif t.data == "return_st": #!return_st : ("return"|"yield"|"await") "from"? boolexpr
        Config.prog_str += t.children[0] + ' '
        if t.children[1] == "from":
            Config.prog_str += t.children[1] + ' '
            translateToBridge(t.children[2])
        else:
            translateToBridge(t.children[1])

    elif t.data == "fname": #ID | ("++"|"--"|PLUSMIN|TIMESDIV|"()"|"[]"|BOOLOP)
        Config.prog_str += t.children[0] + ' '

    elif t.data == "ambit": #ID2
        Config.prog_str += t.children[0] + ' '

    elif t.data == "annot": #"[" "^" boolexpr_list "]"
        Config.prog_str += t.children[0] + t.children[1]
        translateToBridge(t.children[2])
        Config.prog_str += t.children[3]

    elif t.data == "fun_header": #annot* ambit* generic2? "async"? ("fun"|"oper"|"proc")
        cont = 0
        if t.children[0] in ["fun","oper","proc"]:
            Config.prog_str += t.children[0] + ' '
        else:
            if t.children[0] == "async":
                Config.prog_str += t.children[0] + ' ' + t.children[1] + ' '
            elif t.children[0].data == "generic2":
                translateToBridge(t.children[0])
                if t.children[1] == "async":
                    Config.prog_str += ' ' + t.children[1] + ' ' + t.children[2]
                else:
                    Config.prog_str += ' ' + t.children[1]
            elif t.children[0].data == "ambit" :
                while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":
                    translateToBridge(t.children[cont])
                    cont += 1
                if t.children[cont] in ["fun","oper"]:
                    Config.prog_str += ' ' + t.children[cont] + ' '
                elif t.children[cont] == "async":
                    Config.prog_str += ' ' + t.children[cont] + ' ' + t.children[cont+1]
                else:
                    translateToBridge(t.children[cont])
                    if t.children[cont+1] in ["fun","oper"]:
                        Config.prog_str += ' ' + t.children[cont+1] + ' '
                    else:
                        Config.prog_str += ' ' + t.children[cont+1] + ' ' +  t.children[cont+2]
            else: #annot*
                while hasattr(t.children[cont],"data") and t.children[cont].data == "annot":
                    translateToBridge(t.children[cont])
                    Config.prog_str += '\n'
                    cont += 1
                if t.children[cont] in ["fun","oper"]:
                    Config.prog_str += ' ' + t.children[cont] + ' '
                elif t.children[cont] == "async":
                    Config.prog_str += ' ' + t.children[cont] + ' ' + t.children[cont+1]
                elif hasattr(t.children[cont],"data") and t.children[cont].data == "generic2":
                    translateToBridge(t.children[cont])
                    if t.children[cont+1] in ["fun","oper"]:
                        Config.prog_str += ' ' + t.children[cont+1] + ' '
                    else:
                        Config.prog_str += ' ' + t.children[cont+1] + ' ' +  t.children[cont+2]
                else:
                    while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":
                        translateToBridge(t.children[cont])
                        cont += 1
                    if hasattr(t.children[cont],"data") and t.children[cont].data == "generic2":
                        translateToBridge(t.children[cont])
                        cont += 1
                    if t.children[cont] in ["fun","oper"]:
                        Config.prog_str += ' ' + t.children[cont] + ' '
                    else:
                        Config.prog_str += ' ' + t.children[cont] + ' ' +  t.children[cont+1]

    elif t.data == "fundef": ##fun_header fname ("(" arglist ")" |"()") type_ext? ("throws" ID(COMMA ID)*)? ":" init? instructions? "end"
        translateToBridge(t.children[0]) #fun_header
        Config.prog_str += ' '
        translateToBridge(t.children[1]) #fname
        cont = 2
        if t.children[2] == "()": #()
            Config.prog_str += t.children[2]
            cont +=1
        else:#(arglist)
            Config.prog_str += t.children[2]
            translateToBridge(t.children[3])
            Config.prog_str += t.children[4]
            cont+=3
        if t.children[cont] == ":": #:
            Config.prog_str += t.children[cont] + "\n"
            cont +=1
        else: #type_ext? ("throws" ID(COMMA ID)*)?
            if hasattr(t.children[cont],"data") and t.children[cont].data == "type_ext":
                Config.prog_str += ' '
                translateToBridge(t.children[cont])
                cont += 1
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
            Config.prog_str += "\n" + t.children[cont] + '\n'
        else:
            #mirar si hay init
            if hasattr(t.children[cont],"data") and t.children[cont].data == "init":
                translateToBridge(t.children[cont])
                cont += 1
            #Ajustar indent
            Config.indent_str += "  "
            translateToBridge(t.children[cont])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            Config.prog_str += "\n" + Config.indent_str + t.children[cont+1] + '\n'

    elif t.data == "init": #"init" block2_st
        Config.prog_str += Config.indent_str + ' ' + t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += "\n" + Config.indent_str

    elif t.data == "ambit": #ID2
        Config.prog_str += t.children[0] + ' '

    elif t.data == "object_header": # annot* ambit* generic2? ("class" |"interface" | "trait" | "enum"|"struct")
        if t.children[0] in ["class","interface","trait","enum","struct","union"]:
            Config.prog_str += t.children[0] + ' '
        elif t.children[0].data == "generic2":
            translateToBridge(t.children[0])
            Config.prog_str += ' ' + t.children[1] + ' '
        else: #El paquete completo
            for item in t.children[:-1]:
                translateToBridge(item)
            Config.prog_str += t.children[-1] + ' '

    elif t.data == "inherit": #(("extends"|"implements") ID)+
        Config.prog_str += ' '
        for item in t.children:
            Config.prog_str += item + ' '

    elif t.data == "fld_list": #((ambit* ID type_ext? ("=" boolexpr)?) | comment | get_set | (line_generic ";") )+
        cont = 0
        while cont < len(t.children):
            if hasattr(t.children[cont],"data") and t.children[cont].data in ["comment","get_set"]:
                Config.indent_str += "    "
                translateToBridge(t.children[cont])
                cont += 1
                Config.prog_str += "\n"
                Config.indent_str = Config.indent_str[:-4]
                continue
            if hasattr(t.children[cont],"data") and t.children[cont].data == "line_generic":
                Config.indent_str += "    "
                translateToBridge(t.children[cont])
                Config.prog_str += t.children[cont+1]
                cont += 2
                Config.prog_str += "\n"
                Config.indent_str = Config.indent_str[:-4]
                continue
            Config.prog_str += "  "
            while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
                translateToBridge(t.children[cont])
                cont += 1
            Config.prog_str += t.children[cont]#ID
            cont += 1
            #mirar si hay type_ext
            if cont < len(t.children) and hasattr(t.children[cont],"data") and t.children[cont].data =="type_ext":
                Config.prog_str += ' '
                translateToBridge(t.children[cont])
                cont += 1
            if cont < len(t.children) and t.children[cont] == "=": #= boolexpr
                Config.prog_str += ' ' + t.children[cont] + ' '
                translateToBridge(t.children[cont+1])
                cont += 2
            Config.prog_str += "\n"

    elif t.data == "get_set": #ambit* "get" block2_st? (ambit* "set" (("(" ID ")")? block2_st)?)?
        cont = 0
        while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit":#ambit*
            translateToBridge(t.children[cont])
            cont += 1
        Config.prog_str += Config.indent_str + t.children[cont] + ' ' #get
        cont += 1
        if hasattr(t.children[cont],"data"): #block_st
            translateToBridge(t.children[cont])
            cont += 1
        if cont < len(t.children):
            while hasattr(t.children[cont],"data") and t.children[cont].data == "ambit": #ambit*
                translateToBridge(t.children[cont])
                cont += 1
            Config.prog_str += '\n' + Config.indent_str + t.children[cont] #set
            cont += 1
        if cont < len(t.children):
            if hasattr(t.children[cont],"data") and t.children[cont].data == "block2_st": #("(" ID ")")?
                translateToBridge(t.children[cont])
            else: #(("(" ID ")")? block2_st)?
                Config.prog_str+= t.children[cont] + t.children[cont+1] + t.children[cont+2]
                Config.prog_str += '\n' + Config.indent_str
                translateToBridge(t.children[cont+3])

    elif t.data == "object_st": #object_header ID? inherit? ":" block2_st? fld_list? fundef_st* "end"
        cont = 0
        translateToBridge(t.children[0])
        if t.children[1] == ":":
            Config.prog_str += t.children[1] + '\n'
            cont = 2
        elif hasattr(t.children[1],"data") and t.children[1].data == "inherit":
            translateToBridge(t.children[1])
            Config.prog_str += ' ' +  t.children[2] + '\n'
            cont = 3
        else:
            Config.prog_str += t.children[1] + ' '
            if t.children[2] == ":":
                Config.prog_str += t.children[2] + "\n"
                cont = 3
            else:
                translateToBridge(t.children[2])
                Config.prog_str += t.children[3] + "\n"
                cont = 4
        if hasattr(t.children[cont],"data") and t.children[cont].data == "block2_st":
            Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToBridge(t.children[cont])
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            Config.prog_str +=  "\n" 
            cont += 1

        if hasattr(t.children[cont],"data") and t.children[cont].data == "fld_list":
            translateToBridge(t.children[cont])
            Config.prog_str += "\n"
            cont += 1
     
        for item in t.children[cont : -1]: #fundef*
            Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToBridge(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += "\n" + Config.indent_str + t.children[-1]

    elif t.data == "type_tuple": #"type" ID "is" generic ("," generic)* type_ext? fundef_st* "end" 
        cont = 0
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' ' + t.children[2] + '\n  '
        translateToBridge(t.children[3])
        cont = 4
        while t.children[cont] == ",":
            Config.prog_str += t.children[cont]
            translateToBridge(t.children[cont+1])
            cont += 2

        if hasattr(t.children[cont],"data") and t.children[cont].data == "type_ext":
            translateToBridge(t.children[cont])
            cont += 1

        for item in t.children[cont : -1]:
            #Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToBridge(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            #Config.prog_str = Config.prog_str[:-3] + "  " + Config.prog_str[-3:] + " " 
        Config.prog_str += "\n" + Config.indent_str + t.children[-1]

    elif t.data == "type_union": #"type" ID "is" (ID "of" generic)+ fundef_st* "end" 
        cont = 0
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' ' + t.children[2] + '\n  '
        cont = 3
        while t.children[cont] != "end":
            if hasattr(t.children[cont],"data"): break
            #Es un ID of generic
            Config.prog_str += t.children[cont] + ' ' + t.children[cont+1] + ' '
            translateToBridge(t.children[cont+2])
            Config.prog_str += '\n  '
            cont += 3
        for item in t.children[cont : -1]:
            #Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToBridge(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            #Config.prog_str = Config.prog_str[:-3] + "  " + Config.prog_str[-3:] + "\n" 
        Config.prog_str += "\n" + Config.indent_str + t.children[-1]

    elif t.data == "type_record": #"type" ID "is" "{" pair (COMMA pair)* fundef_st* "}" "end" 
        cont = 0
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' ' + t.children[2] + ' ' + t.children[3] + "\n  "
        translateToBridge(t.children[4])
        cont = 5
        while t.children[cont] == ",":
            Config.prog_str += t.children[cont] + ' '
            translateToBridge(t.children[cont+1])
            cont += 2
        for item in t.children[cont : -2]:
            #Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToBridge(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            #Config.prog_str = Config.prog_str[:-3] + "  " + Config.prog_str[-3:] + "\n" 
        Config.prog_str += t.children[-2] +  "\n" + Config.indent_str + t.children[-1]

    elif t.data == "type_variant_record": #"type" ID "is" "record" ((ID ":" generic)|switch_st)+ fundef_st*  "end" 
        cont = 0
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' ' + t.children[2] + ' ' + t.children[3] + "\n  "
        cont = 4

        while t.children[cont] != "end" or (hasattr(t.children[cont],"data") and  t.children[cont].data != "fundef_st"):
            if type(t.children[cont]) == Token:
                Config.prog_str += t.children[cont] + t.children[cont+1]
                translateToBridge(t.children[cont+2])
                Config.prog_str += "\n" + Config.indent_str
                cont += 3
            else:
                translateToBridge(t.children[cont])
                cont += 1

        for item in t.children[cont : -1]:
            #Config.prog_str += "  "
            #Ajustar indent
            Config.indent_str += "  "  
            translateToBridge(item)
            #recuperar indent
            Config.indent_str = Config.indent_str[:-2]
            #Config.prog_str = Config.prog_str[:-3] + "  " + Config.prog_str[-3:] + "\n" 
        Config.prog_str += "\n" + Config.indent_str + t.children[-1]

    elif t.data == "lisp_st": #"$" "(" (boolexpr | LISP_ID | lisp_st | comment)+ ")"
        Config.prog_str += t.children[0] + t.children[1]
        for item in t.children[2:-1]:
            if hasattr(item,"data"):
                translateToBridge(item)
                Config.prog_str += ' '
            else:
                Config.prog_str += item + ' '
        Config.prog_str += t.children[-1] #+ "\n"

    elif t.data == "comment": # COMMENT | COMMENT3 | PASS
        Config.prog_str += t.children[0]

    elif t.data == 'typedef_st': #("typedef"|"using") boolexpr ("as" boolexpr)?     
        Config.prog_str += t.children[0] + " "
        translateToBridge(t.children[1])
        if len(t.children) > 2:
            Config.prog_str += ' ' + t.children[2] + ' '
            translateToBridge(t.children[3])
        
    elif t.data == 'boolexpr_list': #boolexpr (COMMA boolexpr)*
        #procesar primera instruccion
        translateToBridge(t.children[0])
        rest = t.children[1:]
        if rest != []:
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToBridge(pair[1]) 

    elif t.data == 'foreach_st': #"foreach" ("const")? ID type_ext? (COMMA ("const")? ID type_ext?)* "in" boolexpr_list "do" instructions "end"
        Config.prog_str += t.children[0] + ' '
        #Coger la parte fija:"in" boolexpr_list "do" instructions "end"
        fixed = t.children[-5:]
        #Parte variable: 1 hasta -5
        if Config.prog_str[-1] != ' ': Config.prog_str += ' '
        variable = t.children[1:-5]
        for item in  variable:
            if type(item) == Token:
                Config.prog_str += item + ' '
            else:
                translateToBridge(item)
        #Recorrer parte variable
        #Meter parte fija
        Config.prog_str += ' ' + fixed[0] + ' ' #in
        translateToBridge(fixed[1]) #boolexpr_list
        Config.prog_str += ' ' +  fixed[2] + ' \n' #do
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(fixed[3])#instructions, ignoramos end
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[-1]
    #El for deberia aceptar en la primera opcion i as generic
    elif t.data == 'for_st': #for_st: "for" (boolexpr type_ext? | ":" | block2_st) ";" (boolexpr | ":" | block2_st) ";" (boolexpr | ":" | block2_st) "do" instructions "end"
        Config.prog_str += t.children[0] + ' '
        #Hay que tomar 3 veces las opciones
        cont = 1
        if type(t.children[cont]) == Token:
            Config.prog_str += t.children[cont] + ' '
        else:
            translateToBridge(t.children[cont])
            cont += 1
            if hasattr(t.children[cont],"data") and t.children[cont].data == "type_ext":
                Config.prog_str += ' '
                translateToBridge(t.children[cont])
                cont +=1
        Config.prog_str += '; '
        cont += 1
        #print("xx:",t.children[cont])
        for i in range(2):
            if type(t.children[cont]) == Token:
                Config.prog_str += t.children[cont] + ' '
            else:
                translateToBridge(t.children[cont])
            if i<2:
                Config.prog_str += '; '
                cont += 1
            cont += 1
        #Poner el do y procesar instrucciones
        Config.prog_str += ' do\n'
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[-2])#instructions, ignoramos end
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += Config.indent_str + t.children[-1]

    elif t.data == "let_st": #("let"|"const"|"ref"|"var") ID ("," ID)* type_ext? ("=" boolexpr)*
        cont = 0
        Config.prog_str += t.children[0] + ' ' + t.children[1]
        cont+=2
        while cont < len(t.children) and t.children[cont] == ",":
            Config.prog_str += t.children[cont] + t.children[cont+1]
            cont+=2
        #type_ext?
        if cont < len(t.children) and hasattr(t.children[cont],"data") and t.children[cont].data == "type_ext":
            Config.prog_str += ' '
            translateToBridge(t.children[cont])
            cont+=1
        if cont < len(t.children):
            while cont < len(t.children):
                Config.prog_str += ' ' + t.children[cont] + ' '
                translateToBridge(t.children[cont+1])
                cont += 2

    elif t.data == "let_in_st": #"let" "in" boolexpr_list ":" instructions "end"
        Config.prog_str += t.children[0] + ' ' + t.children[1] + ' '
        translateToBridge(t.children[2])
        Config.prog_str += t.children[3] + "\n"
        #Ajuste de indent
        Config.indent_str += "  "
        translateToBridge(t.children[4])
        #recuperar indent
        Config.indent_str = Config.indent_str[:-2]
        Config.prog_str += t.children[5]
        
    elif t.data in ['assert','raise']: #assert_st : "assert"/"raise" boolexpr
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])

    elif t.data == 'boolexpr': #orexp ( ("and"|"&&"|"&") orexp)*))
        #Seguir con la primera instruccion que siempre existe
        translateToBridge(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToBridge(pair[1]) 
    
    elif t.data == 'orexp': #notexp ( ("or"|"||"|"|") notexp)*
        #Seguir con la primera instruccion que siempre existe
        translateToBridge(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToBridge(pair[1]) 
    
    elif t.data == 'notexp': #("not"|"!") cmpexp | cmpexp
        #Seguir con la primera instruccion que siempre existe
        if len(t.children) == 1:
            translateToBridge(t.children[0])
        else: #Hay mas: op instr
            Config.prog_str += ' ' + t.children[0] + ' '
            translateToBridge(t.children[1])
    
    elif t.data == 'cmpexp': #expr (BOOLOP expr)*
        #Seguir con la primera instruccion que siempre existe
        translateToBridge(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToBridge(pair[1]) 
    
    elif t.data == 'expr': #term (PLUSMIN term)*
        #Seguir con la primera instruccion que siempre existe
        translateToBridge(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToBridge(pair[1]) 
    
    elif t.data == 'term': #exp (TIMESDIV exp)*
        #Seguir con la primera instruccion que siempre existe
        translateToBridge(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                Config.prog_str += ' ' + pair[0] + ' '
                translateToBridge(pair[1])  
    
    elif t.data == 'exp': #factor (("**"|"."|"member"|"is") factor)*
        #Seguir con la primera instruccion que siempre existe
        translateToBridge(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                sep = ' ' if pair[0] in ["**","member","is"] else ''
                Config.prog_str += sep + pair[0] + sep
                translateToBridge(pair[1]) 
    
    elif t.data in ['_string','number','null',
                    'nil','None',
                    'true_false','this','self',
                    'empty_list','empty_tuple']:
        if t.data == '_string':
            Config.prog_str += t.children[0].children[0]
        else:
            Config.prog_str += t.children[0]

    elif t.data=='string':
        Config.prog_str += t.children[0]

    elif t.data=='_regex':
        Config.prog_str += t.children[0].children[0]

    elif t.data == 'plusmin': #(PLUSMIN|"sizeof"|"typeof") expr 
        Config.prog_str += t.children[0]
        if t.children[0] in ["sizeof","typeof"]:
            Config.prog_str += ' '
        translateToBridge(t.children[1])

    elif t.data == 'assignation': #assignable ("+="|"-="|"*="|"/="|"|="|"&="|"=") boolexpr
        #Seguir con la primera instruccion que siempre existe
        #print("En assignation: %s" % t)
        translateToBridge(t.children[0])
        Config.prog_str += ' ' + t.children[1] + ' '
        translateToBridge(t.children[2])

    elif t.data == '_assignable':
        translateToBridge(t.children[0])

    # ("&"|"$")* ID (("[" boolexpr? (":" boolexpr?)* "]") |"[]")* ("::" ID)* ("++"|"--"|"...")*
    elif t.data == 'assignable': 
        cont = 0
        if t.children[0] in ["&","$"]:
            Config.prog_str+=t.children[0] + t.children[1]
            cont+=2
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
                    translateToBridge(t.children[cont])
                    cont+=1
                if t.children[cont] =="]" and cont == len(t.children):
                    Config.prog_str += t.children[cont]
                    break
                #coger resto si hay
                while t.children[cont] == ":": 
                    Config.prog_str += t.children[cont] #:
                    cont += 1
                    if t.children[cont] not in ["]",":"]: #hay boolexpr
                        translateToBridge(t.children[cont])
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
                translateToBridge(t.children[cont])
            else:
                Config.prog_str+= t.children[cont]
            cont += 1
        
    elif t.data in ['list','dict']: # "[" boolexpr ("," boolexpr)* "]"   
        #print(t.children) 
        Config.prog_str += t.children[0]
        #procesar primera instruccion
        translateToBridge(t.children[1]) #]|}
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
                translateToBridge(pair[1]) 
        Config.prog_str += sufix

    elif t.data == 'list_comprehension': #"[" boolexpr "for" ID(COMMA ID)* "in" boolexpr "]" 
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2] + ' ' + t.children[3]
        cont = 4
        while t.children[cont] != "in":
            Config.prog_str += t.children[cont] + t.children[cont+1]
            cont += 2
        Config.prog_str += ' ' + t.children[cont] + ' '
        translateToBridge(t.children[cont+1])
        Config.prog_str += t.children[-1]

    elif t.data == 'tuple': # "(" boolexpr COMMA boolexpr (COMMA boolexpr)* ")" 
        Config.prog_str += t.children[0]
        #procesar primera instruccion
        translateToBridge(t.children[1]) #]|}
        Config.prog_str += t.children[2]
        translateToBridge(t.children[3])
        rest = t.children[4:-1]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToBridge(pair[1]) 
        Config.prog_str += t.children[-1]

    elif t.data == 'array': #ID? "{" boolexpr (COMMA boolexpr)* "}"    
        cont = 0
        if t.children[0] == "{":
            Config.prog_str += t.children[0] + ' '
            cont = 1
        else:
            Config.prog_str += t.children[0] + t.children[1] + ' '
            cont = 2 
        translateToBridge(t.children[cont])
        cont += 1
        while cont < len(t.children)-1:
            Config.prog_str += t.children[cont]
            translateToBridge(t.children[cont+1])
            cont += 2
        Config.prog_str += t.children[-1]

    elif t.data == 'empty_dict': #ID? "{}"     
        if t.children[0] == "{}":
            Config.prog_str += t.children[0] + " "
        else:
            Config.prog_str += t.children[0] + t.children[1] + " "

    elif t.data == 'pair_number':#NUMBER ":" boolexpr
        Config.prog_str += t.children[0] + t.children[1]
        translateToBridge(t.children[2])

    elif t.data == 'pair_string':#string ":" boolexpr
        translateToBridge(t.children[0])
        Config.prog_str += t.children[1]
        translateToBridge(t.children[2])
    
    elif t.data == 'pair_id':#ID ":" boolexpr
        Config.prog_str += t.children[0] + t.children[1]
        translateToBridge(t.children[2])

    elif t.data == 'pre_incr': #("++"|"--") expr 
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])

    elif t.data == 'funcall': #assignable "(" arglist ")" 
        translateToBridge(t.children[0])
        Config.prog_str += t.children[1]
        translateToBridge(t.children[2])
        Config.prog_str += t.children[3]

    elif t.data == 'funcall_empty': #assignable "()" 
        translateToBridge(t.children[0])
        Config.prog_str += t.children[1]

    elif t.data == 'expr_funcall': # "(" boolexpr ")" "(" arglist ")" 
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += t.children[2] + t.children[3]
        translateToBridge(t.children[4])
        Config.prog_str += t.children[5]

    elif t.data == 'expr_funcall_empty': #"(" boolexpr ")" "()" 
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += t.children[2] + t.children[3]

    elif t.data == 'arglist': #argitem (COMMA argitem)*
        translateToBridge(t.children[0])
        rest = t.children[1:]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                Config.prog_str += pair[0] + ' '
                translateToBridge(pair[1])

    elif t.data == 'argitem': #ambit* boolexpr type_ext? (("="|":=") boolexpr)? | "..." | ".."
        if type(t.children[0] ) == Token : #"..."|".."
            Config.prog_str += t.children[0]
        else:
            cont = 0
            while t.children[cont].data =="ambit":
                translateToBridge(t.children[cont])
                Config.prog_str += ' '
                cont += 1
            translateToBridge(t.children[cont])
            cont += 1
            rest = t.children[cont:]
            if rest != []:
                if len(rest) == 1: #type_ext?
                    Config.prog_str += ' '
                    translateToBridge(rest[0])
                    Config.prog_str += ' '
                elif len(rest) == 2:
                    Config.prog_str += rest[0]
                    translateToBridge(rest[1])
                else: #todo
                    Config.prog_str += ' '
                    translateToBridge(rest[0])
                    Config.prog_str += ' '
                    Config.prog_str += rest[1]
                    translateToBridge(rest[2])

    elif t.data == 'simple_conditional': #"?" boolexpr "->" boolexpr  
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += t.children[2]
        translateToBridge(t.children[3])

    elif t.data == 'double_conditional': # "?" boolexpr "->" boolexpr ":" boolexpr
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += t.children[2]
        translateToBridge(t.children[3])
        Config.prog_str += t.children[4]
        translateToBridge(t.children[5])

    elif t.data == 'range': # "from" expr "to" expr ("in" expr)?
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2] + ' '
        translateToBridge(t.children[3])
        if len(t.children) >4 : 
            Config.prog_str += ' ' + t.children[4] + ' '
            translateToBridge(t.children[5])

    elif t.data == 'cast': # "(" type_ext ")" expr 
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2]
        translateToBridge(t.children[3])

    elif t.data == 'functional': # ("map"|"filter"|"reduce"|"group") expr "in" expr ("from" expr)?
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        Config.prog_str += ' ' + t.children[2] + ' '
        translateToBridge(t.children[3])
        if len(t.children) >4 : 
            Config.prog_str += ' ' + t.children[4] + ' '
            translateToBridge(t.children[5])

    elif t.data == 'fundef_anonym': #"@"( "()" | "(" arglist ")") type_ext? block2_st
        Config.prog_str += t.children[0]
        cont = 1
        if t.children[1] == "()":
            Config.prog_str += t.children[1]
            cont += 1
        else:
            Config.prog_str += t.children[1]
            translateToBridge(t.children[2])
            Config.prog_str += t.children[3]
            cont += 3
        if t.children[cont].data == "type_ext":
            Config.prog_str += ' '
            translateToBridge(t.children[cont])
            Config.prog_str += ' '
            cont += 1
        translateToBridge(t.children[cont])
        
    elif t.data == 'new': #"new" generic ("()" | "(" arglist? ")")?  
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])
        if t.children[2] == "()":
            Config.prog_str += t.children[2]
        else:
            Config.prog_str += t.children[2]
            translateToBridge(t.children[3])
            Config.prog_str += t.children[4]

    elif t.data == 'new_class': #"new" object_st 
        Config.prog_str += t.children[0] + ' '
        translateToBridge(t.children[1])

    elif t.data == "new_record": # "new" "{" pair (COMMA pair)* "}" 
        #print(t.children) 
        Config.prog_str += t.children[0] + ' ' + t.children[1]
        #procesar primera instruccion
        translateToBridge(t.children[2])
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
                translateToBridge(pair[1]) 
        Config.prog_str += sufix

    elif t.data == 'paren_boolexp': #"(" boolexpr ")"      
        Config.prog_str += t.children[0]
        translateToBridge(t.children[1])
        Config.prog_str += t.children[2]

    elif t.data == 'fact_arroba': #"@" ID2+ boolexpr     
        Config.prog_str += t.children[0] + ' '
        for item in t.children[1:-1]:
            Config.prog_str += item + ' '
        translateToBridge(t.children[-1])

    elif t.data == 'block3': #"[" ID2* "]" "{" instructions "}"  
        t = t.children[0]
        cont = 0 
        Config.prog_str += t.children[cont]
        cont += 1
        while t.children[cont] != "]":
            Config.prog_str += t.children[cont] + ' '
            cont += 1
        Config.prog_str += t.children[cont] + t.children[cont+1]
        cont += 2
        translateToBridge(t.children[cont])
        Config.prog_str += t.children[-1]

    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


