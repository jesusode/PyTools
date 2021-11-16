
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


#Codigo de callbacks

def on_Enter_sentence(sentence_values):
    #Put your code here
    print("Entering sentence with %s" % sentence_values)
    return sentence_values


def on_Exit_sentence(sentence_values):
    #Put your code here
    print("Exiting sentence with %s" % sentence_values)
    return sentence_values


def on_Enter_boolexp(boolexp_values):
    #Put your code here
    print("Entering boolexp with %s" % boolexp_values)
    return boolexp_values


def on_Exit_boolexp(boolexp_values):
    #Put your code here
    print("Exiting boolexp with %s" % boolexp_values)
    return boolexp_values


def on_Enter_orexp(orexp_values):
    #Put your code here
    print("Entering orexp with %s" % orexp_values)
    return orexp_values


def on_Exit_orexp(orexp_values):
    #Put your code here
    print("Exiting orexp with %s" % orexp_values)
    return orexp_values


def on_Enter_notexp(notexp_values):
    #Put your code here
    print("Entering notexp with %s" % notexp_values)
    return notexp_values


def on_Exit_notexp(notexp_values):
    #Put your code here
    print("Exiting notexp with %s" % notexp_values)
    return notexp_values


def on_Enter_cmpexp(cmpexp_values):
    #Put your code here
    print("Entering cmpexp with %s" % cmpexp_values)
    return cmpexp_values


def on_Exit_cmpexp(cmpexp_values):
    #Put your code here
    print("Exiting cmpexp with %s" % cmpexp_values)
    return cmpexp_values


def on_Enter_expr(expr_values):
    #Put your code here
    print("Entering expr with %s" % expr_values)
    return expr_values


def on_Exit_expr(expr_values):
    #Put your code here
    print("Exiting expr with %s" % expr_values)
    return expr_values


def on_Enter_term(term_values):
    #Put your code here
    print("Entering term with %s" % term_values)
    return term_values


def on_Exit_term(term_values):
    #Put your code here
    print("Exiting term with %s" % term_values)
    return term_values


def on_Enter_exp(exp_values):
    #Put your code here
    print("Entering exp with %s" % exp_values)
    return exp_values


def on_Exit_exp(exp_values):
    #Put your code here
    print("Exiting exp with %s" % exp_values)
    return exp_values


def on_Enter_factor(factor_values):
    #Put your code here
    print("Entering factor with %s" % factor_values)
    return factor_values


def on_Exit_factor(factor_values):
    #Put your code here
    print("Exiting factor with %s" % factor_values)
    return factor_values


def on_Enter_arglist(arglist_values):
    #Put your code here
    print("Entering arglist with %s" % arglist_values)
    return arglist_values


def on_Exit_arglist(arglist_values):
    #Put your code here
    print("Exiting arglist with %s" % arglist_values)
    return arglist_values


def on_Enter_pair(pair_values):
    #Put your code here
    print("Entering pair with %s" % pair_values)
    return pair_values


def on_Exit_pair(pair_values):
    #Put your code here
    print("Exiting pair with %s" % pair_values)
    return pair_values



#Codigo del parser
def sentence():

    '''
    sentence : ( boolexp SEMI ) +
    '''
    sentence_values = TagList('sentence')
    on_Enter_sentence(sentence_values)
    sentence_values.append(boolexp())
    sentence_values.append(lexx.nextToken('SEMI'))
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF':
        sentence_values.append(boolexp())
        sentence_values.append(lexx.nextToken('SEMI'))
    on_Exit_sentence(sentence_values)

    return sentence_values

def boolexp():

    '''
    boolexp : orexp ( AND orexp ) *
    '''
    boolexp_values = TagList('boolexp')
    on_Enter_boolexp(boolexp_values)
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
    on_Enter_orexp(orexp_values)
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
    on_Enter_notexp(notexp_values)
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
    on_Enter_cmpexp(cmpexp_values)
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
    on_Enter_expr(expr_values)
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
    on_Enter_term(term_values)
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
    on_Enter_exp(exp_values)
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
    on_Enter_factor(factor_values)
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
    on_Enter_arglist(arglist_values)
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
    on_Enter_pair(pair_values)
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
    input = "2 + 3 *6 + fn(89,a,b*56);25+l;vv(89,5,f*56);"
    lexx.setInput(input)
    #pprint.pprint(boolexp())
    tagListToString(sentence())


