
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
    ["\|>","PIPE",None,False],
    ["\\band\\b","AND",None,False],
    ["\\bor\\b","OR",None,False],
    ["\\bnot\\b","NOT",None,False],
    ["\\bstream\\b","STREAM",None,False],
    ["\\bquery\\b","QUERY",None,False],
    ["\\bencoding\\b","ENCODING",None,False],
    ["\\bimport\\b","IMPORT",None,False],
    ["\\bseparator\\b","SEPARATOR",None,False],
    ["\\bobservers\\b","OBSERVERS",None,False],
    ["\\bshow\\b","SHOW",None,False],
    ["\\bheaders\\b","HEADERS",None,False],
    ["\\brandom\\b","RANDOM",None,False],
    ["\\bset\\b","SET",None,False],
    ["\\bis\\b","IS",None,False],
    ["\\bas\\b","AS",None,False],
    ["\\bdb\\b","DB",None,False],
    ["with","WITH",None,False],
    ["<=|>=|>|<|==|!=<|>","BOOLOP",None,False],
    ["@[a-z]+","STREAMOP",None,False],
    ["[a-zA-Z_][a-zA-Z_0-9]*(\\.[a-zA-Z0-9_]+)*","ID",None,False],
    ['''\\"[^\\"]+\\"''',"STRING",None,False],
    [";","SEMI",None,False],
    ["=","EQUAL",None,False]
]


__toks_to_ignore = ['WHITESPACES']
lexx.setIgnore(__toks_to_ignore)


lexx.setTable(_table)

#Codigo de inicio de usuario


#Codigo de callbacks

def on_Exit_script(script_values):
    #Put your code here
    print("Exiting script with %s" % script_values)
    return script_values


def on_Exit_sent(sent_values):
    #Put your code here
    print("Exiting sent with %s" % sent_values)
    return sent_values


def on_Exit_streamdef(streamdef_values):
    #Put your code here
    print("Exiting streamdef with %s" % streamdef_values)
    return streamdef_values


def on_Exit_source(source_values):
    #Put your code here
    print("Exiting source with %s" % source_values)
    return source_values


def on_Exit_dbquery(dbquery_values):
    #Put your code here
    print("Exiting dbquery with %s" % dbquery_values)
    return dbquery_values


def on_Exit_streampipe(streampipe_values):
    #Put your code here
    print("Exiting streampipe with %s" % streampipe_values)
    return streampipe_values


def on_Exit_boolexp(boolexp_values):
    #Put your code here
    print("Exiting boolexp with %s" % boolexp_values)
    return boolexp_values


def on_Exit_orexp(orexp_values):
    #Put your code here
    print("Exiting orexp with %s" % orexp_values)
    return orexp_values


def on_Exit_notexp(notexp_values):
    #Put your code here
    print("Exiting notexp with %s" % notexp_values)
    return notexp_values


def on_Exit_cmpexp(cmpexp_values):
    #Put your code here
    print("Exiting cmpexp with %s" % cmpexp_values)
    return cmpexp_values


def on_Exit_expr(expr_values):
    #Put your code here
    print("Exiting expr with %s" % expr_values)
    return expr_values


def on_Exit_term(term_values):
    #Put your code here
    print("Exiting term with %s" % term_values)
    return term_values


def on_Exit_exp(exp_values):
    #Put your code here
    print("Exiting exp with %s" % exp_values)
    return exp_values


def on_Exit_factor(factor_values):
    #Put your code here
    print("Exiting factor with %s" % factor_values)
    return factor_values


def on_Exit_arglist(arglist_values):
    #Put your code here
    print("Exiting arglist with %s" % arglist_values)
    return arglist_values


def on_Exit_pair(pair_values):
    #Put your code here
    print("Exiting pair with %s" % pair_values)
    return pair_values



#Codigo del parser
def script():

    '''
    script : ( sent SEMI ) +
    '''
    script_values = TagList('script')
    script_values.append(sent())
    script_values.append(lexx.nextToken('SEMI'))
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF':
        script_values.append(sent())
        script_values.append(lexx.nextToken('SEMI'))
    on_Exit_script(script_values)

    return script_values

def sent():

    '''
    sent : | ( STREAM streamdef ) | ( QUERY dbquery ) | ( ENCODING expr ) | ( IMPORT expr ) | ( SEPARATOR expr ) | ( SHOW expr ) | ( SET ID EQUAL ID ) | ( SET ID COLON EQUAL ID streampipe ) | ( ID streampipe ) | ( boolexp )
    '''
    sent_values = TagList('sent')
    if 'EOF' in [x.value for x in lexx.lookahead(5)] : raise Exception('Error: found EOF while parsing rule')
    if lexx.lookahead(5)[0].type == 'SET' and lexx.lookahead(5)[1].type == 'ID' and lexx.lookahead(5)[2].type == 'COLON' and lexx.lookahead(5)[3].type == 'EQUAL' and lexx.lookahead(5)[4].type == 'ID':
        lexx.nextToken('SET')
        sent_values.append(lexx.nextToken('ID'))
        sent_values.append(lexx.nextToken('COLON'))
        sent_values.append(lexx.nextToken('EQUAL'))
        sent_values.append(lexx.nextToken('ID'))
        sent_values.append(streampipe())
    elif lexx.lookahead(4)[0].type == 'SET' and lexx.lookahead(4)[1].type == 'ID' and lexx.lookahead(4)[2].type == 'EQUAL' and lexx.lookahead(4)[3].type == 'ID':
        lexx.nextToken('SET')
        sent_values.append(lexx.nextToken('ID'))
        sent_values.append(lexx.nextToken('EQUAL'))
        sent_values.append(lexx.nextToken('ID'))
    elif lexx.lookahead(1)[0].type == 'STREAM':
        sent_values.append(lexx.nextToken('STREAM'))
        sent_values.append(streamdef())
    elif lexx.lookahead(1)[0].type == 'QUERY':
        sent_values.append(lexx.nextToken('QUERY'))
        sent_values.append(dbquery())
    elif lexx.lookahead(1)[0].type == 'ENCODING':
        sent_values.append(lexx.nextToken('ENCODING'))
        sent_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'IMPORT':
        sent_values.append(lexx.nextToken('IMPORT'))
        sent_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'SEPARATOR':
        sent_values.append(lexx.nextToken('SEPARATOR'))
        sent_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'SHOW':
        sent_values.append(lexx.nextToken('SHOW'))
        sent_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'ID':
        sent_values.append(lexx.nextToken('ID'))
        sent_values.append(streampipe())
    else:
        sent_values.append(boolexp())
    on_Exit_sent(sent_values)

    return sent_values

def streamdef():

    '''
    streamdef : ID IS source ( WITH HEADERS ( ID ) + ) ? ( WITH OBSERVERS ( ID ) + ) ?
    '''
    streamdef_values = TagList('streamdef')
    streamdef_values.append(lexx.nextToken('ID'))
    lexx.nextToken('IS')
    streamdef_values.append(source())
    if lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'WITH':
        lexx.nextToken('WITH')
        streamdef_values.append(lexx.nextToken('HEADERS'))
        streamdef_values.append(lexx.nextToken('ID'))
        while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'ID':
            streamdef_values.append(lexx.nextToken('ID'))
    if lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'WITH':
        lexx.nextToken('WITH')
        streamdef_values.append(lexx.nextToken('OBSERVERS'))
        streamdef_values.append(lexx.nextToken('ID'))
        while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'ID':
            streamdef_values.append(lexx.nextToken('ID'))
    on_Exit_streamdef(streamdef_values)

    return streamdef_values

def source():

    '''
    source : | ( FILE expr ) | ( DB dbquery ) | ( RANDOM expr ) | ( expr )
    '''
    source_values = TagList('source')
    if 'EOF' in [x.value for x in lexx.lookahead(1)] : raise Exception('Error: found EOF while parsing rule')
    if lexx.lookahead(1)[0].type == 'FILE':
        source_values.append(lexx.nextToken('FILE'))
        source_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'DB':
        source_values.append(lexx.nextToken('DB'))
        source_values.append(dbquery())
    elif lexx.lookahead(1)[0].type == 'RANDOM':
        source_values.append(lexx.nextToken('RANDOM'))
        source_values.append(expr())
    else:
        source_values.append(expr())
    on_Exit_source(source_values)

    return source_values

def dbquery():

    '''
    dbquery : QUERY ID WITH expr ( AS expr ) ?
    '''
    dbquery_values = TagList('dbquery')
    dbquery_values.append(lexx.nextToken('QUERY'))
    dbquery_values.append(lexx.nextToken('ID'))
    lexx.nextToken('WITH')
    dbquery_values.append(expr())
    if lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'AS':
        dbquery_values.append(lexx.nextToken('AS'))
        dbquery_values.append(expr())
    on_Exit_dbquery(dbquery_values)

    return dbquery_values

def streampipe():

    '''
    streampipe : ( PIPE ( STREAMOP ) + boolexp ) +
    '''
    streampipe_values = TagList('streampipe')
    streampipe_values.append(lexx.nextToken('PIPE'))
    streampipe_values.append(lexx.nextToken('STREAMOP'))
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'STREAMOP':
        streampipe_values.append(lexx.nextToken('STREAMOP'))
    streampipe_values.append(boolexp())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'PIPE':
        streampipe_values.append(lexx.nextToken('PIPE'))
        streampipe_values.append(lexx.nextToken('STREAMOP'))
        while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'STREAMOP':
            streampipe_values.append(lexx.nextToken('STREAMOP'))
        streampipe_values.append(boolexp())
    on_Exit_streampipe(streampipe_values)

    return streampipe_values

def boolexp():

    '''
    boolexp : orexp ( AND orexp ) *
    '''
    boolexp_values = TagList('boolexp')
    boolexp_values.append(orexp())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'AND':
        boolexp_values.append(lexx.nextToken('AND'))
        boolexp_values.append(orexp())
    on_Exit_boolexp(boolexp_values)

    return boolexp_values

def orexp():

    '''
    orexp : notexp ( OR notexp ) *
    '''
    orexp_values = TagList('orexp')
    orexp_values.append(notexp())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'OR':
        orexp_values.append(lexx.nextToken('OR'))
        orexp_values.append(notexp())
    on_Exit_orexp(orexp_values)

    return orexp_values

def notexp():

    '''
    notexp : | ( NOT cmpexp ) | ( LPAREN boolexp RPAREN ) | ( cmpexp )
    '''
    notexp_values = TagList('notexp')
    if 'EOF' in [x.value for x in lexx.lookahead(1)] : raise Exception('Error: found EOF while parsing rule')
    if lexx.lookahead(1)[0].type == 'NOT':
        notexp_values.append(lexx.nextToken('NOT'))
        notexp_values.append(cmpexp())
    elif lexx.lookahead(1)[0].type == 'LPAREN':
        notexp_values.append(lexx.nextToken('LPAREN'))
        notexp_values.append(boolexp())
        notexp_values.append(lexx.nextToken('RPAREN'))
    else:
        notexp_values.append(cmpexp())
    on_Exit_notexp(notexp_values)

    return notexp_values

def cmpexp():

    '''
    cmpexp : expr ( BOOLOP expr ) *
    '''
    cmpexp_values = TagList('cmpexp')
    cmpexp_values.append(expr())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'BOOLOP':
        cmpexp_values.append(lexx.nextToken('BOOLOP'))
        cmpexp_values.append(expr())
    on_Exit_cmpexp(cmpexp_values)

    return cmpexp_values

def expr():

    '''
    expr : term ( PLUSMIN term ) *
    '''
    expr_values = TagList('expr')
    expr_values.append(term())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'PLUSMIN':
        expr_values.append(lexx.nextToken('PLUSMIN'))
        expr_values.append(term())
    on_Exit_expr(expr_values)

    return expr_values

def term():

    '''
    term : exp ( TIMESDIV exp ) *
    '''
    term_values = TagList('term')
    term_values.append(exp())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'TIMESDIV':
        term_values.append(lexx.nextToken('TIMESDIV'))
        term_values.append(exp())
    on_Exit_term(term_values)

    return term_values

def exp():

    '''
    exp : factor ( EXP factor ) *
    '''
    exp_values = TagList('exp')
    exp_values.append(factor())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'EXP':
        exp_values.append(lexx.nextToken('EXP'))
        exp_values.append(factor())
    on_Exit_exp(exp_values)

    return exp_values

def factor():

    '''
    factor : | ( PLUSMIN expr ) | ( NUMBER ) | ( ID LPAREN arglist RPAREN ) | ( ID LPAREN RPAREN ) | ( ID LBRACK expr RBRACK ) | ( ID ) | ( STRING ) | ( LPAREN expr RPAREN ) | ( LBRACK expr ( COMMA expr ) * RBRACK ) | ( LBRACK RBRACK ) | ( LCURLY pair ( COMMA pair ) * RCURLY ) | ( LCURLY RCURLY )
    '''
    factor_values = TagList('factor')
    if 'EOF' in [x.value for x in lexx.lookahead(3)] : raise Exception('Error: found EOF while parsing rule')
    if lexx.lookahead(3)[0].type == 'ID' and lexx.lookahead(3)[1].type == 'LPAREN' and lexx.lookahead(3)[2].type == 'RPAREN':
        factor_values.append(lexx.nextToken('ID'))
        factor_values.append(lexx.nextToken('LPAREN'))
        factor_values.append(lexx.nextToken('RPAREN'))
    elif lexx.lookahead(2)[0].type == 'ID' and lexx.lookahead(2)[1].type == 'LPAREN':
        factor_values.append(lexx.nextToken('ID'))
        factor_values.append(lexx.nextToken('LPAREN'))
        factor_values.append(arglist())
        factor_values.append(lexx.nextToken('RPAREN'))
    elif lexx.lookahead(2)[0].type == 'ID' and lexx.lookahead(2)[1].type == 'LBRACK':
        factor_values.append(lexx.nextToken('ID'))
        factor_values.append(lexx.nextToken('LBRACK'))
        factor_values.append(expr())
        factor_values.append(lexx.nextToken('RBRACK'))
    elif lexx.lookahead(2)[0].type == 'LBRACK' and lexx.lookahead(2)[1].type == 'RBRACK':
        factor_values.append(lexx.nextToken('LBRACK'))
        factor_values.append(lexx.nextToken('RBRACK'))
    elif lexx.lookahead(2)[0].type == 'LCURLY' and lexx.lookahead(2)[1].type == 'RCURLY':
        factor_values.append(lexx.nextToken('LCURLY'))
        factor_values.append(lexx.nextToken('RCURLY'))
    elif lexx.lookahead(1)[0].type == 'PLUSMIN':
        factor_values.append(lexx.nextToken('PLUSMIN'))
        factor_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'NUMBER':
        factor_values.append(lexx.nextToken('NUMBER'))
    elif lexx.lookahead(1)[0].type == 'ID':
        factor_values.append(lexx.nextToken('ID'))
    elif lexx.lookahead(1)[0].type == 'STRING':
        factor_values.append(lexx.nextToken('STRING'))
    elif lexx.lookahead(1)[0].type == 'LPAREN':
        factor_values.append(lexx.nextToken('LPAREN'))
        factor_values.append(expr())
        factor_values.append(lexx.nextToken('RPAREN'))
    elif lexx.lookahead(1)[0].type == 'LBRACK':
        factor_values.append(lexx.nextToken('LBRACK'))
        factor_values.append(expr())
        while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'COMMA':
            factor_values.append(lexx.nextToken('COMMA'))
            factor_values.append(expr())
        factor_values.append(lexx.nextToken('RBRACK'))
    elif lexx.lookahead(1)[0].type == 'LCURLY':
        factor_values.append(lexx.nextToken('LCURLY'))
        factor_values.append(pair())
        while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'COMMA':
            factor_values.append(lexx.nextToken('COMMA'))
            factor_values.append(pair())
        factor_values.append(lexx.nextToken('RCURLY'))
    on_Exit_factor(factor_values)

    return factor_values

def arglist():

    '''
    arglist : expr ( COMMA expr ) *
    '''
    arglist_values = TagList('arglist')
    arglist_values.append(expr())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'COMMA':
        arglist_values.append(lexx.nextToken('COMMA'))
        arglist_values.append(expr())
    on_Exit_arglist(arglist_values)

    return arglist_values

def pair():

    '''
    pair : | ( NUMBER COLON expr ) | ( STRING COLON expr ) | ( ID COLON expr )
    '''
    pair_values = TagList('pair')
    if 'EOF' in [x.value for x in lexx.lookahead(1)] : raise Exception('Error: found EOF while parsing rule')
    if lexx.lookahead(1)[0].type == 'NUMBER':
        pair_values.append(lexx.nextToken('NUMBER'))
        pair_values.append(lexx.nextToken('COLON'))
        pair_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'STRING':
        pair_values.append(lexx.nextToken('STRING'))
        pair_values.append(lexx.nextToken('COLON'))
        pair_values.append(expr())
    elif lexx.lookahead(1)[0].type == 'ID':
        pair_values.append(lexx.nextToken('ID'))
        pair_values.append(lexx.nextToken('COLON'))
        pair_values.append(expr())
    on_Exit_pair(pair_values)

    return pair_values



#Codigo de usuario

import pprint
if __name__ == '__main__':
    input = """
    encoding "latin-1";
    separator ",";
    stream hemos is "hemos20.csv" with headers nombre nhc organismo with observers urines totals;
    hemos |> @select [x[2],x[4]] |> @filter x[4] == "Pseudomonas"
          |> @save "Pseudomonas20.csv" |> @export "Pseudomonas20.pdf";
    set hemos2 = hemos;
    stream cosita is 
            db query antibiogramas with "select * from atbs" as mysql 
            with headers uno dos tres 
            with observers o1 o2 o45;
    stream randoms is random ["normal",50,10,5000] 
           with headers gg hh jj with observers totals;
    show randoms;
    set result := randoms |> @flat @filter x < 200;
    """
    lexx.setInput(input)
    tagListToString(script())


