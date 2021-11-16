

from grammar_utils import *
from ebnf_parser import *


def manageBNFRightRec(rule):
    '''
    Convierte una regla BNF recursiva por la
    derecha a un equivalente EBNF.
    Manejamos:

    a : |(empty)|Ba => a : B*
    a : |B|Ba => B+
    '''
    if isRightRecursive(rule):
        group = rule[1][1]
        #print(f"group:{group}")
        if group[1].type == "empty":
            #Correccion para |(empty)|Ba
            #tmp= [tokenFactory("rparen",")"),tokenFactory("mult","*")]
            tmp= [tokenFactory("mult","*")]
            #Eliminar la cabe3za de la regla. Hay que hacerlo asi
            # para no perder los codes si los hay
            tmp2 = [x for x in rule[1][3] if x.value != rule[0].value]  
            rule = [rule[0],(tmp2 + tmp)] 
        else:
            #Correccion para |B|Ba
            rule_end= [tokenFactory("plus","+")] 
            rule = [rule[0],(group + rule_end)]         
        #print(f"rule transformada: {rule}")
    return rule


def buildDescParser(rule_list : list, callbacks : bool,toks_to_discard :  List[str],callbacks_all : bool) -> str:
    '''
    Construye un parser descendente recursivo en Python
    a partir de una lista de GrammarRules.
    '''
    global callbacks_template,callbacks_code
    buffer = io.StringIO()
    for rule in rule_list:
        print("RULE:")
        pprint.pprint(rule)
        print("====")
        #-----------------------------------------------------------
        #Para reglas BNF, corregir las recursivas por la derecha,
        #no traducibles a parser descendente con LA
        rule = manageBNFRightRec(rule)
        #-----------------------------------------------------------
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

        buffer.write("def " + rule[0].value + "(" + rule_args + "):\n")
        #Regla como docstring
        docstr = "\n    '''\n" + "    " +  rule[0].value + " : " + " ".join([x.value for x in flat(rule[1:])])    + "\n    '''\n"
        buffer.write(docstr)
        #Meter lista para recoger tokens parseados
        #buffer.write("    " + rule_values + " = []\n")
        buffer.write("    " + rule_values + " = TagList('" + rule[0].value + "')\n")
        #Callback de entrada si se ha definido
        if callbacks == True:
            if callbacks_all == True:
                buffer.write("    on_Enter_" + rule[0].value + "(" + rule_values + ")\n")
                callbacks_code.write(callbacks_template.format("Enter",rule[0].value,rule_values))
        ruleToDescParser(rule_rhs,buffer,rule_values = rule_values,toks_to_discard=toks_to_discard)
        #Callback de salida si se ha definido
        if callbacks == True:
            buffer.write("    on_Exit_" + rule[0].value + "(" + rule_values + ")\n")
            callbacks_code.write(callbacks_template.format("Exit",rule[0].value,rule_values))
        if rule_returns == "":
            buffer.write("\n    return " + rule_values + "\n\n")
        else:
            buffer.write("\n    return " + rule_returns + "\n\n")
  
    return buffer.getvalue()


def ruleToDescParser(rule_rhs : list, parser_buff : io.StringIO, margin : str = "    ",rule_values = "",toks_to_discard = []) -> str:
    '''
    Convierte una regla en un parser descendente
    de LA variable. distingue cuatro tipos de
    variaciones: Terminal, No terminal, Closure y 
    Options. 
    '''
    print(f"TOKS_TO_DISCARD AQUI:{toks_to_discard}")
    #print("ENTERING ruleToDescParser()")
    #Plantilla para los and de LA > 1
    and_template = " and lexx.lookahead({0})[{1}].type == '{2}'"

    for item in rule_rhs:
        print("ITEM:\n")
        pprint.pprint(item)
        if type(item) != list:
            if item.type == "nonterm":
                print("Procesando un no terminal")
                parser_buff.write(margin + rule_values + ".append(" +  item.value + "())\n")
            elif item.type == 'terminal':
                print(f"procesando un terminal: {item.value}")
                if item.value not in toks_to_discard:
                    parser_buff.write(margin  + rule_values +  ".append(lexx.nextToken('" + item.value + "'))\n")
                else:
                    parser_buff.write(margin + "lexx.nextToken('" + item.value + "')\n")                    
            elif item.type == "code":
                print("Procesando code")
                parser_buff.write(indent(item.value[2:-2],margin))
            else: #empty
                print("Procesando empty!")
                #no hacemos nada??
        else: 
            #Procedemos segun elemento
            if item[0].type == "lparen":
                print("procesando un group o un closure")

                #Nota: Para un parser descendente se necesita que el primer--------------------------------------------
                #token de un group sea un terminal
                #if item[1].type not in ["terminal",""]:
                #    raise Exception("Error: Para un parser descendente se necesita que el primer Token de un grupo sea un termnal")
                #------------------------------------------------------------------------------------------------------
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
                    ruleToDescParser(to_process,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard)
                    if has_code_last:
                        ruleToDescParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard)
                elif cls == '*':
                    #Ignorar parentesis de apertura de grupo, de cierre y */+/?
                    print(f"Es un closure 0 o mas: procesando: {to_process}")
                    parser_buff.write(margin + "while " + check_string + ":\n")
                    ruleToDescParser(to_process,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard)
                    if has_code_last:
                        ruleToDescParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard)
                elif cls == '+':
                    print("Es un uno o mas")
                    ruleToDescParser(to_process,parser_buff,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard)
                    parser_buff.write(margin + "while " + check_string + ":\n")
                    ruleToDescParser(to_process,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard)
                    if has_code_last:
                        ruleToDescParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard)
                else:
                    print("Es un group")
                    #Hay que comprobar que tipo de group es y proceder en consecuencia??
                    ruleToDescParser(to_process,parser_buff,margin,rule_values=rule_values,toks_to_discard=toks_to_discard)
                    if has_code_last:
                        ruleToDescParser([item[-1]],parser_buff,margin = margin ,rule_values=rule_values,toks_to_discard=toks_to_discard)
            elif item[0].type == 'pipe':
                print("procesando Options")
                #print(f"ITEM AQUI: {item}")
                #opts=[]
                opts = getOptions(item,[])
                print("opts-----------")
                print(opts)
                print("-------------")
                #print("########################################################")
                only_one_nonterm,checked_options = checkOptionsForASDR(opts)
                #pprint.pprint(checked_options)
                #print("checkOptionsForASDR devuelve el lookahead que hay que usar para cada opcion")
                #print("hay que cambiar el algoritmo para usarlo")
                #print("#############################################")
                #Montar el if-elif-else
                if only_one_nonterm == False:
                    print("==> WARNING: This rule has more than one nonterminal as first option. Undecidible with Recursive Descendent Parser.")
                check_eof = "if 'EOF' in [x.value for x in lexx.lookahead({0})] : raise Exception('Error: found EOF while parsing rule')\n"
                #Para cada opcion, usar el LA que es el primer valor para montar el if-elif-else
                cont = 0
                header = ""
                parser_buff.write(margin + check_eof.format(max([x[0] for x in checked_options])))
                for op in checked_options:
                    la,opt = op
                    #Mirar si el ultimo elemento es un no terminal y usarlo como else
                    #ESTO DEPENDE DE COMO LO ESCRIBA EL USUARIO: EL PARSER NO LO HACE TODAVIA!!!!
                    put_last_else = False
                    if only_one_nonterm == True and len(opt)==1 and  (opt[-1].type if type(opt[-1]) == lexer.Token else opt[-1][0].type) == "nonterm":
                        #print("====PUESTO PUT_LAST_ELSE A TRUE===")
                        put_last_else = True
                    #if o elif o else segun cont y put_last_else
                    header = "if"
                    if cont > 0:
                        if cont == len(checked_options) - 1 and len(opt)==1 and put_last_else == True:
                            header = "else"
                        else:
                            header = "elif"
                    #print(f"opt:{opt}, len(opt):{len(opt)},only_one_term:{only_one_nonterm}")
                    parser_buff.write(margin + header) # + check_eof.format(la))
                    #Montar cadena de ands y añadirla
                    if put_last_else == False:
                        for i in range(la if put_last_else == False else la[:-1]):
                            cond = and_template.format(la,i,opt[i].value if type(opt[i])==lexer.Token else opt[i][0].value)
                            if i==0:
                                cond = cond[4:]
                            parser_buff.write(cond)
                    #else:
                    #    parser_buff.write("else")
                    #Poner else si es necesario
                    parser_buff.write(":\n")
                    #Y parsear la opcion
                    ruleToDescParser(opt,parser_buff,margin = margin + "    ",rule_values=rule_values,toks_to_discard=toks_to_discard)
                    #incrementar contador
                    cont+=1
                #------------------------------------------------------------------------------
                #Esto requiere que TODOS los primeros de las opciones sean
                #terminales menos el ultimo y que esten ordenados de mayor a menor LA
                #Pte de implementar que el no terminal sea el ultimo.
                #------------------------------------------------------------------------------
            else: #Cadena de terminales/no terminales
                ruleToDescParser(item,parser_buff,margin = margin,rule_values=rule_values,toks_to_discard=toks_to_discard)  


    #return parser_buff.getvalue()

def checkOptionsForASDR(opts):
    '''
    Acepta una lista de opciones y
    comprueba que todos menos una
    empiecen por terminal y que si hay 
    terminales repetidos,cual debe ser el LA
    para cada uno y ademas en que orden
    deben evaluarse.
    '''
    new_options=[]
    #print("############################################################################")
    #print(f"Options: {opts}")
    byFirstTerminal = groupby(lambda x: x.value if type(x)==lexer.Token else x[0].value,opts)
    #pprint.pprint(byFirstTerminal)
    term_conts = {}
    for item in byFirstTerminal:
        #print(f"VIENDO ITEM: {item}")
        opt_size = len(byFirstTerminal[item])
        #Si solo hay una opcion, no hay problema
        if opt_size == 1:
            new_options.append([1,byFirstTerminal[item]])
        else:
            term_conts[item] = {}
            num_conts = 0
            cont = 0
            for el in byFirstTerminal[item]:
                #print(f"    VIENDO EL: {el}")
                #contar no terminales contiguos
                for t in el:
                    if type(t) == lexer.Token and t.type == "terminal":
                        num_conts+=1
                    else:
                        break
                #print(f"    num_conts: {num_conts}")
                #print(f"    cont: {cont}")
                term_conts[item][cont]=num_conts
                num_conts = 0
                cont+=1
        #Meter las opciones con el num de terminales contiguos
        for i in range(len(byFirstTerminal[item])):
            if len(byFirstTerminal[item]) > 1:
                new_options.append([term_conts[item][i],byFirstTerminal[item][i]])
    #pprint.pprint(term_conts)
    #pprint.pprint(sorted(new_options,key = lambda x: x[0],reverse = True))
    #print("############################################################################")
    #1.- Comprobar que todas las opciones menos una son terminales
    all_but_one_terminals = True
    for i in range(len(opts)-1):
        if type(opts[i]) == lexer.Token:
            if opts[i].type != "terminal":
                all_but_one_terminals = False
        else: #list
            if opts[i][0].type != "terminal":
                all_but_one_terminals = False
    return [all_but_one_terminals,sorted(new_options,key = lambda x: x[0],reverse = True)]


def packParser(g_id,toks,parser_code,pre_code,post_code,toks_to_ignore,toks_to_discard):
    '''
    Construye y empaqueta el parser en un archivo
    '''
    global parser_template
    parser = parser_template.replace("%%tokens%%",toks)
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
        parser = parser.replace("%%user_end_code%%",post_code.value[2:-2] )
    else:
        parser = parser.replace("%%user_end_code%%","" )

    with open(g_id + "_parser.py","w",encoding = "utf-8") as f:
        f.write(parser)


