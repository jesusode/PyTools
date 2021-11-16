#Pruebas de gramaticas con lark

from lark import Lark,Tree,Token


def run_instruction(t):
    global prog_str,instr_sep,indent_str
    #print("running_instruction: %s" % t.data)

    if t.data == 'instructions':
        for child in t.children:
            if child.data == 'instruction':
                #Aplicar el indent actual
                prog_str += indent_str
                run_instruction(child)
                prog_str += instr_sep + "\n"
            elif child.data == 'comment':
                prog_str += '#' + child.children[0].strip('\n')[2:] + '\n'
    
    elif t.data == 'instruction': #boolexpr|statement
        run_instruction(t.children[0])

    elif t.data == 'statement':
        run_instruction(t.children[0])
    
    elif t.data == 'block2_st': #"{" instructions "}"
        #print(t)
        prog_str += t.children[0] + '\n'
        #Ajuste de indent
        indent_str += "  "
        run_instruction(t.children[1])
        #recuperar indent
        indent_str = indent_str[:-2]
        prog_str += t.children[2]

    elif t.data == 'break_cont_st': #break_cont_st : ("break"|"continue")
        prog_str += t.children[0] #+ '\n'
    
    elif t.data in ['assert_st','raise_st']: #"assert" boolexpr,"raise" expr
        prog_str += t.children[0] + ' '
        run_instruction(t.children[1])

    elif t.data == 'while_st': #while_st : "while"  boolexpr "do" instructions "end" 
        prog_str += t.children[0] + ' '
        run_instruction(t.children[1])
        prog_str += ' :\n'#Para Python,cambiar para resto
        #Ajuste de indent
        indent_str += "  "
        run_instruction(t.children[3])
        #recuperar indent
        indent_str = indent_str[:-2]

    elif t.data == 'dowhile_st': # "do" instructions "until" boolexpr "end"
        prog_str += t.children[0] + ' \n'
        #Ajuste de indent
        indent_str += "  "
        #print(t.children[1])
        run_instruction(t.children[1])
        prog_str += t.children[2] + ' '#
        #recuperar indent
        indent_str = indent_str[:-2]
        run_instruction(t.children[3])

    elif t.data == 'type_ext': #type_ext : "as" generic
        prog_str += t.children[0] + ' '
        run_instruction(t.children[1])

    elif t.data == 'generic': #generic : assignable  ("where" boolexpr)?
        run_instruction(t.children[0])
        rest = t.children[1:]
        if rest!=[]:
            prog_str += rest[0]
            run_instruction(rest[1])

    elif t.data == 'boolexpr_list': #boolexpr (COMMA boolexpr)*
        #procesar primera instruccion
        run_instruction(t.children[0])
        rest = t.children[1:]
        if rest != []:
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                prog_str += pair[0] + ' '
                run_instruction(pair[1]) 

    elif t.data == 'foreach_st': #"foreach" ("const")? ID type_ext? (COMMA ("const")? ID type_ext?)* "in" boolexpr_list "do" instructions "end"
        prog_str += t.children[0] + ' '
        #Coger la parte fija:"in" boolexpr_list "do" instructions "end"
        fixed = t.children[-5:]
        #Parte variable: 1 hasta -5
        if prog_str[-1] != ' ': prog_str += ' '
        variable = t.children[1:-5]
        for item in  variable:
            if type(item) == Token:
                prog_str += item + ' '
            else:
                run_instruction(item)
        #Recorrer parte variable
        #Meter parte fija
        prog_str += ' ' + fixed[0] + ' ' #in
        run_instruction(fixed[1]) #boolexpr_list
        prog_str += ' ' +  fixed[2] + ' \n' #do
        #Ajuste de indent
        indent_str += "  "
        run_instruction(fixed[3])#instructions, ignoramos end
        #recuperar indent
        indent_str = indent_str[:-2]
    #El for deberia aceptar en la primera opcion i as generic
    elif t.data == 'for_st': #for_st: "for" (boolexpr | ":" | block2_st) ";" (boolexpr | ":" | block2_st) ";" (boolexpr | ":" | block2_st) "do" instructions "end"
        prog_str += t.children[0] + ' '
        #Hay que tomar 3 veces las opciones
        cont = 1
        for i in range(3):
            #print(t.children[cont])
            if type(t.children[cont]) == Token:
                prog_str += t.children[cont] + ' '
            else:
                run_instruction(t.children[cont])
            if i<2:
                prog_str += '; '
                cont += 1
            cont += 1
        #Poner el do y procesar instrucciones
        prog_str += ' do\n'
        #Ajuste de indent
        indent_str += "  "
        run_instruction(t.children[-2])#instructions, ignoramos end
        #recuperar indent
        indent_str = indent_str[:-2]

    elif t.data == 'boolexpr': #orexp ( ("and"|"&&"|"&") orexp)*))
        #Seguir con la primera instruccion que siempre existe
        run_instruction(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                prog_str += ' ' + pair[0] + ' '
                run_instruction(pair[1]) 
    
    elif t.data == 'orexp': #notexp ( ("or"|"||"|"|") notexp)*
        #Seguir con la primera instruccion que siempre existe
        run_instruction(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                prog_str += ' ' + pair[0] + ' '
                run_instruction(pair[1]) 
    
    elif t.data == 'notexp': #("not"|"!") cmpexp | cmpexp
        #Seguir con la primera instruccion que siempre existe
        if len(t.children) == 1:
            run_instruction(t.children[0])
        else: #Hay mas: op instr
            prog_str += ' ' + t.children[0] + ' '
            run_instruction(t.children[1])
    
    elif t.data == 'cmpexp': #expr (BOOLOP expr)*
        #Seguir con la primera instruccion que siempre existe
        run_instruction(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                prog_str += ' ' + pair[0] + ' '
                run_instruction(pair[1]) 
    
    elif t.data == 'expr': #term (PLUSMIN term)*
        #Seguir con la primera instruccion que siempre existe
        run_instruction(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                prog_str += ' ' + pair[0] + ' '
                run_instruction(pair[1]) 
    
    elif t.data == 'term': #exp (TIMESDIV exp)*
        #Seguir con la primera instruccion que siempre existe
        run_instruction(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                prog_str += ' ' + pair[0] + ' '
                run_instruction(pair[1])  
    
    elif t.data == 'exp': #factor (EXP factor)*
        #Seguir con la primera instruccion que siempre existe
        run_instruction(t.children[0])
        if len(t.children) > 1: #Hay mas: op instr
            cont=1
            while cont < len(t.children[1:]):
                pair = [t.children[cont],t.children[cont+1]]
                cont+=2
                prog_str += ' ' + pair[0] + ' '
                run_instruction(pair[1]) 
    
    elif t.data in ['_string','number','null',
                    'true_false','this',
                    'empty_list','empty_tuple']:
        if t.data == '_string':
            prog_str += t.children[0].children[0]
        else:
            prog_str += t.children[0]

    elif t.data=='string':
        prog_str += t.children[0]

    elif t.data == 'plusmin': #PLUSMIN expr 
        prog_str += t.children[0]
        run_instruction(t.children[1])

    elif t.data == 'assignation': #assignable ("+="|"-="|"*="|"/="|"|="|"&="|"=") boolexpr
        #Seguir con la primera instruccion que siempre existe
        #print("En assignation: %s" % t)
        run_instruction(t.children[0])
        prog_str += ' ' + t.children[1] + ' '
        run_instruction(t.children[2])

    elif t.data == '_assignable':
        run_instruction(t.children[0])

    elif t.data == 'assignable': #ID ("[" boolexpr (":" boolexpr)* "]")* ("++"|"--")*
        #print("En assignable")
        #print(t)
        #print(len(t.children))
        prog_str += t.children[0]
        #Coger el final si lo hay
        #print(t.children[-1])
        sufix = t.children[-1] if t.children[-1] in ['++','--'] else ''
        #
        if len(t.children[1:]) > 1: #Hay mas:
            #Si termina en sufix, coger hasta ahi
            parts = []
            if sufix == '':
                parts = t.children[1:]
            else:
                parts = t.children[1:-1]
            #print("parts: %s" % parts)
            cont=0
            while cont < len(parts):
                #print("len-cont: %s" %(len(parts)-cont))
                #Si solo queda uno, es el ] final
                if len(parts) - cont == 1 :
                    prog_str += parts[cont]
                    break
                pair = [parts[cont],parts[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                prog_str += pair[0] + ' '
                run_instruction(pair[1]) 
        prog_str += sufix
    elif t.data in ['list','array','dict']: # "[" boolexpr ("," boolexpr)* "]"   
        #print(t.children) 
        prog_str += t.children[0]
        #procesar primera instruccion
        run_instruction(t.children[1]) #]|}
        sufix = t.children[-1]
        rest = t.children[2:-1]
        if rest != []:
            #print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                prog_str += pair[0] + ' '
                run_instruction(pair[1]) 
        prog_str += sufix

    elif t.data == 'pair_number':#NUMBER ":" boolexpr
        prog_str += t.children[0] + t.children[1]
        run_instruction(t.children[2])

    elif t.data == 'pair_string':#string ":" boolexpr
        run_instruction(t.children[0])
        prog_str += t.children[1]
        run_instruction(t.children[2])
    
    elif t.data == 'pair_id':#ID ":" boolexpr
        prog_str += t.children[0] + t.children[1]
        run_instruction(t.children[2])

    elif t.data == 'pre_incr': #("++"|"--") expr 
        prog_str += t.children[0]
        run_instruction(t.children[1])

    elif t.data == 'funcall': #assignable "(" arglist ")" 
        run_instruction(t.children[0])
        prog_str += t.children[1]
        run_instruction(t.children[2])
        prog_str += t.children[3]

    elif t.data == 'funcall_empty': #assignable "()" 
        run_instruction(t.children[0])
        prog_str += t.children[1]

    elif t.data == 'expr_funcall': # "(" boolexpr ")" "(" arglist ")" 
        prog_str += t.children[0]
        run_instruction(t.children[1])
        prog_str += t.children[2] + t.children[3]
        run_instruction(t.children[4])
        prog_str += t.children[5]

    elif t.data == 'expr_funcall_empty': #"(" boolexpr ")" "()" 
        prog_str += t.children[0]
        run_instruction(t.children[1])
        prog_str += t.children[2] + t.children[3]

    elif t.data == 'arglist': #argitem (COMMA argitem)*
        run_instruction(t.children[0])
        rest = t.children[1:]
        if rest != []:
            print("rest: %s" % rest)
            cont=0
            while cont < len(rest):
                pair = [rest[cont],rest[cont+1]]
                #print('Procesando pair: %s' % pair)
                cont+=2
                prog_str += pair[0] + ' '
                run_instruction(pair[1])

    elif t.data == 'argitem': #argitem: boolexpr type_ext? ("=" boolexpr)? | "..." | ".."
        if type(t.children[0] ) == Token : #"..."|".."
            prog_str += t.children[0]
        else:
            run_instruction(t.children[0])
            rest = t.children[1:]
            if rest != []:
                if len(rest) == 1: #type_ext?
                    prog_str += ' '
                    run_instruction(rest[0])
                    prog_str += ' '
                elif len(rest) == 2:
                    prog_str += rest[0]
                    run_instruction(rest[1])
                else: #todo
                    prog_str += ' '
                    run_instruction(rest[0])
                    prog_str += ' '
                    prog_str += rest[1]
                    run_instruction(rest[2])

    elif t.data == 'simple_conditional': #"?" boolexpr "->" boolexpr  
        prog_str += t.children[0]
        run_instruction(t.children[1])
        prog_str += t.children[2]
        run_instruction(t.children[3])

    elif t.data == 'double_conditional': # "?" boolexpr "->" boolexpr ":" boolexpr
        prog_str += t.children[0]
        run_instruction(t.children[1])
        prog_str += t.children[2]
        run_instruction(t.children[3])
        prog_str += t.children[4]
        run_instruction(t.children[5])



    #else:
    #    raise SyntaxError('Unknown instruction: %s' % t.data)


# Scannerless Earley is the default
#parser = Lark(exprs_grammar,debug=True,parser='lalr') 

prog = open("tests/test3.txt","r",encoding="utf-8").read()

parser = Lark.open("new_bridge2.lark",debug =True,parser = 'lalr')

print(parser.parse(prog).pretty())

prog_str = ""
instr_sep = ';' #'\n' #';'
indent_str = ""
def run_program(program):
    global prog_str
    parse_tree = parser.parse(program)
    for inst in parse_tree.children:
        run_instruction(inst)
    print("code_str: %s" % prog_str)

#Send in the clowns!!
#run_program(prog)
