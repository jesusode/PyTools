from typing import *
import lexer
from lexer import tokenFactory
from flat import flat
import pprint
import io

#Utilidades para gramaticas-----------------------------------------------------

def flatTokList(lst):
    '''
    Convierte una lista de tokens con posibles sublistas en
    una lista de un solo nivel
    '''
    #print(f"\nLST:{lst}")
    flatted=[]
    for el in lst:
        if type(el)==list or isinstance(el,list):
            for item in flatTokList(el):
                flatted.append(item)
        else:
            flatted.append(el.value)
    return flatted


def findInTokList(lst,tokvalue):
    '''
    Busca un value de un token en una
    lista posiblemente anidada de tokens.
    '''
    for el in lst:
        #print(f"EL:{el}")
        if type(el)==list or isinstance(el,list):
            rval = findInTokList(el,tokvalue)
            if rval is not None:
                return rval
        else:
            if el.value == tokvalue: return el
    return None


def getOptions(lst,options=[]):
    '''
    Busca las options en una lista de listas de Tokens.
    Cada options empieza con un | y va seguida de sus elementos
    en forma de group. El último valor de la option
    es el último elemento de la lista.
    '''
    for i in range(len(lst)):
        #print(f"PROCESANDO: {i}")
        #print("PROCESANDO:")
        #pprint.pprint(lst[i])
        if type(lst[i])!= list and lst[i].type in ["pipe","code"]:
            #Incrementar puntero
            if i < len(lst)-1 : i+=1
            if type(lst[i]) == list:
                options.append(lst[i][1:-1])
            else:
                options.append(lst[i])
        elif type(lst[i]) == list:
                getOptions(lst[i],options)
    #Si el ultimo es un code y el penultimo nonterm, meterlos en una lista
    if len(options) > 1 and type(options[-1])==lexer.Token and type(options[-2])==lexer.Token and options[-1].type=="code" and options[-2].type=="nonterm":
        last_two = [options[-2],options[-1]]
        options = options[:-2]
        options.append(last_two)
    #print(f"OPTIONS en getOptions: {options}")
    return options


def isLeftRecursive(rule : List[Any]): #??
    '''
    True si la cabeza de la regla se repite
    la primera del resto de componentes.
    Recursiva por la izquierda.
    Asume Tokens.
    '''
    #Aplanar rule si es necesario
    rule = flat(rule)
    if rule[0] == rule[1] : 
        return True
    else:
        return False


def isRightRecursive(rule : List[Any]): #??
    '''
    True si la cabeza de la regla es
    igual al ultimo elemento.
    Recursiva por la derecha.
    Asume Tokens.
    '''
    #Aplanar rule si es necesario
    rule = flat(rule)
    if rule[0] in rule[1:]:
        return True
    else:
        return False


def reprRule(lst):
    '''
    Devuelve una representacion de los values de una rule
    '''
    lst = flat(lst)
    return lst[0].value + (" : " if lst[1].value != ":" else "") + " ".join(x.value for x in lst[1:]) + ';'

def reprRules(rules : Any,file : str="") -> str: #REVISARLO!!!!
    '''
    Devuelve la representación como string
    de un conjunto de reglas.
    Si se especifica file, la escribe en el archivo.
    '''
    rule_str = io.StringIO()
    for rule in rules:
        #for item in rule:
        #    rule_str.write(reprRule(item))
            rule_str.write(reprRule(rule))
            rule_str.write("\n")
    transformed = rule_str.getvalue()
    if file != "":
        with open(file,"w") as f:
            f.write(transformed)
            f.close()
    return transformed


def getGroups(lst,groups=[],nocode=False,noextras=False,processed=[]):
    '''
    Busca las options en una lista de listas de Tokens.
    Cada group empieza con un ( y termina con un )
    El fin de un grupo puede ser ?/*/+ o nada.
    '''
    cont=0
    skip_this = False
    #for i in range(len(lst)):
    #print(f"==>Longitud de la lista a procesar: {len(lst)}\n")
    while cont < len(lst):
        #print(f"PROCESANDO con cont: {cont}:")
        #pprint.pprint(lst[cont])
        if type(lst[cont])!= list and lst[cont].type == "lparen": #Esta mal!!! CAMBIAR LA LOGICA!!!
            #print(f"POR GROUP")
            processed.append("group")
            group = []
            #Buscar fin de parentesis o ?/*/+
            for j in range(cont+1,len(lst)):
                #print(f"Mirando subitem: {lst[j]} con j:{j}")
                if type(lst[j]) == lexer.Token:
                    if lst[j].type == "rparen":
                        #print("BREAK!!")
                        break
                    else: #list
                        #print(f"metiendo item en group!: {group}")
                        group.append(lst[j])
                        #print(f"metiendo item en group!: {group}")
                else: #?????
                    #print(f"Procesando GROUP recursivo!i:{cont},j:{j},group:{lst[j]}")
                    k=getGroups(lst[j],group,nocode,noextras,processed)
                    #print(f"Hemos avanzado: {k} items")
                    j+= k
                    #print(f"Group recursivo procesado: group {group},cont:{cont},j:{j}")
                    #print(f"groups aqui: {groups}")

            #Si hay closure, cogerla
            if j+1 < len(lst) and type(lst[j+1])==lexer.Token and lst[j+1].type in ["mult","question","plus"]:
                #print("COGIENDO CLOSURE")
                group.append(lst[j+1])
                skip_this = True
            #print(f"GROUP a meter:{group}")
            groups.append(group)
            cont = j
            #print(f"SKIP_THIS: {skip_this}")
            if skip_this == True:
                skip_this = False
                #print("ME SALTO LA CLOSURE!!")
                cont+=2
                continue
        elif type(lst[cont])== list:
            #print(f"POR LIST")
            getGroups(lst[cont],groups,nocode,noextras,processed)
            
        else:
            #print("IGNORADO")
            processed.append(lst[cont])
        cont+=1
        #print(f"VALOR DE cont aqui: {cont}")
    #print(f"retornando cont:{cont}")
    return cont


def groupToRules(group,name,cont=0,rules=[],closr=None):
    '''
    Convierte un grupo en una serie de reglas.
    Normas: 
    (G)? -> Gs: empty|G
    (G)* -> Gs: empty|GGs
    (G)+ -> Gs: G|GGs
    (G) -> G
    Los grupos pueden estar anidados cualquier
    numero de niveles.
    '''
    #print(f"GROUP:{group}")
    rule = []
    aux = []
    cls=None
    closure=""
    if type(group[-1]) != list:
        closure = group[-1].value if group[-1].value in ["+","*","?"] else ""
    #print(f"closure. {closure}")
    if closure != "":
        #print("Grupo con closure!\n")
        if closure in ["*","?","+"]:
            cls=tokenFactory("nonterm",name + "_group" + str(cont))
            #print(f"Creado group:{cont}")
            rule.append(cls)
            closr=cls
            rule.append(tokenFactory("colon",":"))
            rule.append(tokenFactory("pipe","|"))
            rule.append(tokenFactory("lparen","("))
            if closure != "+":
                #rule.append(tokenFactory("lparen","("))
                rule.append(tokenFactory("empty","empty"))
                rule.append(tokenFactory("rparen",")"))
                rule.append(tokenFactory("pipe","|"))
                rule.append(tokenFactory("lparen","("))
            
    else: #Poner parentesis para los grupos sin closure
        #print("USO EL ELSE!!")
        rule.append(tokenFactory("lparen","("))

    for item in group:
        #print(f"Mirando ITEM: {item} con cont: {cont}\n")
        if type(item) == lexer.Token:
            if item.type not in ["plus","question","mult"]:
                #print(f"Metiendo item normal:{item}\n")
                if closure != "+":
                    rule.append(item)
                else:
                    aux.append(item)

        else:
            cont+=1
            #print(f"Metiendo item recursivo:{item}, cont: {cont}, cls: {cls}\n")
            cont2 = groupToRules(item,name,cont,rules,cls)
            #print(f"valor de cont2: {cont2}")
            if closure != "+":
                rule.append(tokenFactory("nonterm",name + "_group" + str(cont2)))
            else:
                aux.append(tokenFactory("nonterm",name + "_group" + str(cont2)))
                aux.append(tokenFactory("lparen","("))#?????
            cont=cont2+1
            #print(f"cont despues de meter recursivo:{cont}" )
    #print(f"cont despues del for: {cont}")

    if closure == "": #Cerrar grupos sin closure
        rule.append(tokenFactory("rparen",")"))

    elif closure in ["*","+"] and closr!=None:
        #print(f"AUX: {aux}")
        #print(f"CLOSR: {closr}")
        if closure == "*":
            #rule.append(tokenFactory("lparen","("))
            rule.append(closr)
            rule.append(tokenFactory("rpren",")"))
        else:
            #meter aux en rule
            #rule.append(tokenFactory("lparen","("))#????
            rule.extend(aux)
            rule.append(tokenFactory("rparen",")"))
            rule.append(tokenFactory("pipe","|"))
            rule.append(tokenFactory("lparen","("))
            rule.append(closr)
            rule.append(tokenFactory("rpren",")"))
    #cont+=1
    #print(f"\n\nRULE AL FINAL: {rule}\n\n")
    rules.append(rule)
    #print(f"Devolviendo cont: {cont}")
    return cont


def EBNFToBNF(tree):
    '''
    Transforma AST de reglas EBNF en BNF,
    basicamente cambiando los closures
    por nuevas reglas.
    '''
    #pprint.pprint(tree)
    grp_cont = 0
    bnf_rules = []
    for item in tree:
        rules=[]
        tmp=[]
        proc=[]
        grp_cont += getGroups(item,tmp,processed=proc)

        for grp in tmp:
            grp_cont = groupToRules(grp,item[0].value,grp_cont,rules)
        #Intento de reconstruir las reglas transformadas
        buff=[]
        #Nuevo----------------------------------------------------------------------------------------------
        grppos=0
        isPipe = False
        last_pos = 0
        for i in range(len(proc)):
            if i <len(proc):
                if proc[i]!="group":
                    if isinstance(proc[i],lexer.Token) and proc[i].type == "pipe":
                        #Coger la regla que toca
                        isPipe = True
                        while i < len(proc)-1 and proc[i+1] == "group":
                            grppos += 1
                            i += 1
                        #buff.append(rules[grppos])
                        #print(f"Valor de grppos: {grppos}")
                    elif isinstance(proc[i],lexer.Token) and proc[i].type not in  ["pipe","colon"]:
                        if i == 0:                      
                            buff.append([proc[0]])
                            buff[0].append(tokenFactory("colon",":"))
                        else:
                            buff[0].append(proc[i])
                else:
                    #print(f"grppos:{grppos}, last_pos:{last_pos},isPipe:{isPipe}")
                    if last_pos == 0 and grppos == 0 and isPipe == False:
                        buff[0].append(rules[grppos][0])
                        buff.append(rules[grppos])
                    elif isPipe == False:
                        if grppos > last_pos:
                            buff[0].append(tokenFactory("pipe","|"))
                            buff[0].extend(rules[grppos][0])
                            buff.append(rules[grppos])
                    else:
                        if grppos > last_pos:
                            buff[0].append(tokenFactory("pipe","|"))
                            buff[0].extend(rules[grppos-1])
                            buff.extend(rules[last_pos : grppos-1])
                            last_pos = grppos
                        isPipe=False                       
        #---------------------------------------------------------------------------------------------------

        if len(buff)> 0 and type(buff[0]) == lexer.Token:
            buff = [buff]

        #for el in buff:
        #    print(reprRule(el))
        bnf_rules.append(buff)

    return bnf_rules


def rulesToTable(rules : List[Any]) -> Dict[str, List[Any]]:
    '''
    Crea una tabla con las reglas ordenadas por el value del primer
    token.
    '''
    table = {}
    for rule in rules:
        table[rule[0].value] = rule
    return table


def getTerminalsAndNotTerminals(grammar):
    '''
    Devuelve dos sets con los terminales
    y los no terminales de la gramatica
    '''
    terminals= set()
    nonterminals= set()
    flatted = [flat(rule) for rule in grammar]
    for item in flatted:
        for tok in item:
            if tok.type in ["terminal","empty"]:
                terminals.add(tok.value)
            elif tok.type == "nonterm":
                nonterminals.add(tok.value)
    return (terminals,nonterminals)


def isNullable(rule: List[Any],grammar_table: Dict[str,List[Any]],cache = {}) -> bool:
    '''
    True si contiene o produce empty.
    Si no, False.
    Revisar funcionamiento y rendimiento
    '''
    #print("RULE:")
    #pprint.pprint(rule)
    options=getOptions(rule,[])#Ojito: poner [] o coge lo anterior!!!!!!
    #print(f"options: {options}")
    if options == []:
        #Si no tiene opciones y el primer item es terminal: False
        #Si algun item es empty : True
        #print("Sin options")
        for item in flat(rule[1:]):
            #print(f"mirando item: {item}")
            if item.value == rule[0].value : 
                #print("Header->continue")
                continue
            elif item.type == "empty":
                #print("empty->True")
                cache[rule[0].value] = True
                return True
            elif item.type == "terminal":
                #print("Terminal->False")
                return False
            elif item.type == "nonterm":
                #print("nonterm-> Recurse or follow")
                if isNullable(grammar_table[item.value],grammar_table,cache):
                    #cache[item.value] = True
                    return True
                else:
                    #print(f"nonterm {item.value} no anulable: devolvemos False")
                    return False
    else:
        #Si alguna opcion es anulable, es anulable la regla
        #print(f"Comprobando options: {options}")
        for option in options:
            #print(f"mirando option: {option}")
            #Si el primero es un terminal, la opcion NO es anulable
            if option[0].type == "terminal":
                #print("primero de opcion es terminal, opcion no anulable")
                continue
            for item in option:
                #print(f"Mirando item de options:{item}")
                if item.value == rule[0].value:
                    #print("Header opt->continue")
                    continue
                elif item.type == "empty":
                    #print("Empty opt->True")
                    cache[rule[0].value] = True
                    return True
                elif item.type == "nonterm":
                    #print("nonterm opt->recurse or follow")
                    if isNullable(grammar_table[item.value],grammar_table,cache):
                        return True
                    else:
                        #print(f"nonterm {item.value} no anulable: break")
                        break #?????
        #Si no hay ningun item anulable, devolvemos False
        return False


def nullables(grammar: List[Any],grammar_table: Dict[str,List[Any]])-> Dict[str,bool]:
    '''
    Calcula un diccionario con todas las reglas
    anulables de la gramatica.
    '''
    nullables={}
    for rule in grammar:
        isNullable(rule,grammar_table,nullables)
    return nullables


def firsts(grammar):
    '''
    Calcula y devuelve el conjunto de Primeros
    de la gramatica en forma de diccionario.
    '''
    firsts = {}
    #PRIM{empty} = {empty}. Regla 0.
    rules = rulesToTable(grammar)
    nullables_ = nullables(grammar,rules)
    #PRIM{TERM} = {TERM}. Regla 1:
    tms,ntms = getTerminalsAndNotTerminals(grammar)
    for tm in tms:
        firsts[tm] = {tm}
    #print(f"\n-----Calculando firsts para expr-----\n")
    #firsts[tm] = calcFirsts("sentence",rules,nullables_,firsts)
    #print(f"\nFIRSTS: {firsts[tm]}---\n")
    #'''
    for symbol in ntms:
        print(f"\n-----Calculando firsts para {symbol}-----\n")
        firsts[tm] = calcFirsts(symbol,rules,nullables_,firsts)
        print(f"\nFIRSTS: {firsts[tm]}---\n")
    #'''
    return firsts


def calcFirsts(symbol,grammar_table,nullables,cache):
    '''
    Calcula Primeros de un no terminal.
    '''
    #Aplicar cache: si esta calculado, lo devolvemos
    if symbol in cache:
        print("Devolviendo firsts del cache!!!!!")
        return cache[symbol]
    firsts = set()
    rule = grammar_table[symbol]
    #PRIM(no terminal) con produccion s->empty: meter empty.Regla 2
    #if isNullable(rule,grammar_table):
    if symbol in nullables:
        firsts.add("empty")
    options = getOptions(rule,[])
    #print(f"OPTIONS: {options}")
    if options == []: 
        print("Sin opciones")
        #No tiene opciones: X->Y1Y2...Yn...
        #cont=0
        for item in rule[1:]:
            print(f"Mirando item: {item}")
            #Si es recursiva por la derecha, saltarse el recursivo
            if item.value == symbol: continue
            #Si es un terminal, lo metemos y nos vamos
            if item.type == "terminal":
                print("Es un terminal: Lo metemos y salimos")
                firsts.add(item.value)
                cache[symbol] = firsts
                return firsts
            elif item.type == "nonterm":
                #Agregar PRIM(Yn)-{empty} a PRIM(X)
                print("No terminal: Cache o llamada recursiva")
                if not item.value in cache:
                    print(f"Llamada recursiva con {item.value}")
                    primY = calcFirsts(item.value,grammar_table,nullables,cache)
                    for elem in primY:
                        if elem != "empty":
                            firsts.add(elem)
                    #Si empty no esta en PRIM(Yn) parar
                    if not "empty" in primY:
                        cache[symbol] = firsts
                        return firsts
            #cont += 1
    else:
        print("con opciones")
        #Tiene opciones: proceder para cada una de ellas
        for option in options:
            print(f"Mirando opcion:{option}")
            for item in option:
                print(f"Mirando item de opcion: {item}")
                if item.value == symbol : continue
                if item.type == "terminal":
                    print("Es un terminal de opcion: Lo metemos y break")
                    firsts.add(item.value)
                    break
                elif item.type == "nonterm":
                    print("No terminal de opcion: Cache o llamada recursiva")
                    #Agregar PRIM(Yn)-{empty} a PRIM(X)
                    if not item.value in cache:
                        print(f"Llamada recursiva en opcion con {item.value}")
                        primY = calcFirsts(item.value,grammar_table,nullables,cache)
                        for elem in primY:
                            if elem != "empty":
                                firsts.add(elem)
    cache[symbol] = firsts
    return firsts #???


def follows(grammar,firsts):
    '''
    Calcula y devuelve los conjuntos follows para 
    los no terminales de una gramatica.
    Algoritmo:
    1.- Sig(A) = {}
    2.- Si A es el simbolo inicial: Sig(A)=Sig(A) U {$}
    3.- Para cada regla B: aAb -> Sig(A) = Sig(A) U Prim(b)
    4.- Para cada regla B: aA o bien B: aAb con empty en Prim(b)
        -> Sig(A) = Sig(A) U Sig(B)
    5.- Repetir 3 y 4 hasta que no se puedan
        añadir más símbolos a Sig(A) 
    '''
    follows = {}
    #rules = rulesToTable(grammar)
    _,ntms = getTerminalsAndNotTerminals(grammar)
    first_symbol = grammar[0][0].value
    for symbol in ntms:
        print(f"\n-----Calculando follows para {symbol}-----\n")
        follows[symbol] = calcFollows(symbol,grammar,first_symbol,firsts,follows)
        print(f"\nFOLLOWS: {follows[symbol]}---\n")
    return follows


def calcFollows(symbol,grammar,first_symbol,firsts,cache):
    '''
    Calcula el conjunto Sig(symbol)
    '''
    follows = set()
    old = len(follows)
    actual = len(follows)
    if symbol == first_symbol:
        follows.add("$")
    #Buscar todas las reglas que contengan symbol
    for rule in grammar:
        #print(f"Viendo regla {rule}")
        rule = rule[1:]
        if actual > 0 and actual == old:
            break
        #Si hay opciones en la regla hay que considerarlas una a una
        opts = getOptions(rule,[])
        if opts == []:
            elems = [x.value for x in rule]
            print(f"Viendo regla {elems}")
            if symbol  in elems:
                idx = elems.index(symbol)
                #Regla 3: 
                if idx < len(elems) -1:
                    if not "empty" in firsts[elems[idx+1]]:
                        print("Aplicando regla 3: B: aAb -> Sig(A) = Sig(A) U Prim(b)")
                        follows = follows.union(firsts[elems[idx+1]])
                    else: #Regla 4
                        #Redundante: deberia tener cache!!
                        print("Aplicando regla 4: Sig(A) = Sig(A) U Sig(B)")
                        if elems[idx+1] in cache:
                            print("Devolviendo follows desde cache!")
                            follows = follows.union(cache[elems[idx+1]])
                        else:
                            follows = follows.union(calcFollows(elems[idx+1],grammar,first_symbol,firsts,follows))
                print("match symbol")
        else:
            for item in opts:
                elems = [x.value for x in item]
                print(f"Viendo regla {elems}")
                if symbol  in elems:
                    idx = elems.index(symbol)
                    #Regla 3: 
                    if idx < len(elems) -1:
                        if not "empty" in firsts[elems[idx+1]]:
                            print("Aplicando regla 3: B: aAb -> Sig(A) = Sig(A) U Prim(b)")
                            follows = follows.union(firsts[elems[idx+1]])
                        else: #Regla 4
                            #Redundante: deberia tener cache!!
                            print("Aplicando regla 4: Sig(A) = Sig(A) U Sig(B)")
                            if elems[idx+1] in cache:
                                print("Devolviendo follows desde cache!")
                                follows = follows.union(cache[elems[idx+1]])
                            else:
                                follows = follows.union(calcFollows(elems[idx+1],grammar,first_symbol,firsts,follows))
                    print("match symbol in opt")
    return follows






class GrammarRule:
    '''
    Crea una Regla Gramatical a partir de lo que sale
    del ebnf parser.
    '''

    def __init__(self,parsed_rule : List[lexer.Token],priority=0):
        assert type(parsed_rule) == list
        self.lhs= parsed_rule[0]
        self.id= self.lhs.value
        self.rhs= parsed_rule[1:]
        self.flattedtoks = flat(self.rhs)
        self.flatted = [self.id] + [x.value for x in self.flattedtoks]
        self.priority=priority
        self.options=[]
        self.closure = False
        #print(self.flattedtoks)
        self.terminals = {x for x in self.flattedtoks if x.type == 'terminal'}
        self.nonterminals = {x for x in self.flattedtoks if x.type == 'nonterm'}


    def hasEmpty(self):
        return True if findInTokList(self.rhs,'empty') is not None else  False

    def toString(self):
        return "<<GrammarRule. id: {0}\n LHS: {1},\nRHS: {2},\n Priority: {3}>>".format(self.id,self.lhs,self.rhs,self.priority)

    def toText(self):
        return "{0} : {1}\n".format(self.id," ".join(self.flatted[1:]))

