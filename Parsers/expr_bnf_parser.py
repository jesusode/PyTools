
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


__toks_to_ignore = ['WHITESPACES']
lexx.setIgnore(__toks_to_ignore)


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


def on_Enter_sentence_group2(sentence_group2_values):
    #Put your code here
    print("Entering sentence_group2 with %s" % sentence_group2_values)
    return sentence_group2_values


def on_Exit_sentence_group2(sentence_group2_values):
    #Put your code here
    print("Exiting sentence_group2 with %s" % sentence_group2_values)
    return sentence_group2_values


def on_Enter_boolexp(boolexp_values):
    #Put your code here
    print("Entering boolexp with %s" % boolexp_values)
    return boolexp_values


def on_Exit_boolexp(boolexp_values):
    #Put your code here
    print("Exiting boolexp with %s" % boolexp_values)
    return boolexp_values


def on_Enter_boolexp_group5(boolexp_group5_values):
    #Put your code here
    print("Entering boolexp_group5 with %s" % boolexp_group5_values)
    return boolexp_group5_values


def on_Exit_boolexp_group5(boolexp_group5_values):
    #Put your code here
    print("Exiting boolexp_group5 with %s" % boolexp_group5_values)
    return boolexp_group5_values


def on_Enter_orexp(orexp_values):
    #Put your code here
    print("Entering orexp with %s" % orexp_values)
    return orexp_values


def on_Exit_orexp(orexp_values):
    #Put your code here
    print("Exiting orexp with %s" % orexp_values)
    return orexp_values


def on_Enter_orexp_group8(orexp_group8_values):
    #Put your code here
    print("Entering orexp_group8 with %s" % orexp_group8_values)
    return orexp_group8_values


def on_Exit_orexp_group8(orexp_group8_values):
    #Put your code here
    print("Exiting orexp_group8 with %s" % orexp_group8_values)
    return orexp_group8_values


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


def on_Enter_cmpexp_group13(cmpexp_group13_values):
    #Put your code here
    print("Entering cmpexp_group13 with %s" % cmpexp_group13_values)
    return cmpexp_group13_values


def on_Exit_cmpexp_group13(cmpexp_group13_values):
    #Put your code here
    print("Exiting cmpexp_group13 with %s" % cmpexp_group13_values)
    return cmpexp_group13_values


def on_Enter_expr(expr_values):
    #Put your code here
    print("Entering expr with %s" % expr_values)
    return expr_values


def on_Exit_expr(expr_values):
    #Put your code here
    print("Exiting expr with %s" % expr_values)
    return expr_values


def on_Enter_expr_group16(expr_group16_values):
    #Put your code here
    print("Entering expr_group16 with %s" % expr_group16_values)
    return expr_group16_values


def on_Exit_expr_group16(expr_group16_values):
    #Put your code here
    print("Exiting expr_group16 with %s" % expr_group16_values)
    return expr_group16_values


def on_Enter_term(term_values):
    #Put your code here
    print("Entering term with %s" % term_values)
    return term_values


def on_Exit_term(term_values):
    #Put your code here
    print("Exiting term with %s" % term_values)
    return term_values


def on_Enter_term_group19(term_group19_values):
    #Put your code here
    print("Entering term_group19 with %s" % term_group19_values)
    return term_group19_values


def on_Exit_term_group19(term_group19_values):
    #Put your code here
    print("Exiting term_group19 with %s" % term_group19_values)
    return term_group19_values


def on_Enter_exp(exp_values):
    #Put your code here
    print("Entering exp with %s" % exp_values)
    return exp_values


def on_Exit_exp(exp_values):
    #Put your code here
    print("Exiting exp with %s" % exp_values)
    return exp_values


def on_Enter_exp_group22(exp_group22_values):
    #Put your code here
    print("Entering exp_group22 with %s" % exp_group22_values)
    return exp_group22_values


def on_Exit_exp_group22(exp_group22_values):
    #Put your code here
    print("Exiting exp_group22 with %s" % exp_group22_values)
    return exp_group22_values


def on_Enter_factor(factor_values):
    #Put your code here
    print("Entering factor with %s" % factor_values)
    return factor_values


def on_Exit_factor(factor_values):
    #Put your code here
    print("Exiting factor with %s" % factor_values)
    return factor_values


def on_Enter_factor_group25(factor_group25_values):
    #Put your code here
    print("Entering factor_group25 with %s" % factor_group25_values)
    return factor_group25_values


def on_Exit_factor_group25(factor_group25_values):
    #Put your code here
    print("Exiting factor_group25 with %s" % factor_group25_values)
    return factor_group25_values


def on_Enter_factor_group27(factor_group27_values):
    #Put your code here
    print("Entering factor_group27 with %s" % factor_group27_values)
    return factor_group27_values


def on_Exit_factor_group27(factor_group27_values):
    #Put your code here
    print("Exiting factor_group27 with %s" % factor_group27_values)
    return factor_group27_values


def on_Enter_arglist(arglist_values):
    #Put your code here
    print("Entering arglist with %s" % arglist_values)
    return arglist_values


def on_Exit_arglist(arglist_values):
    #Put your code here
    print("Exiting arglist with %s" % arglist_values)
    return arglist_values


def on_Enter_arglist_group31(arglist_group31_values):
    #Put your code here
    print("Entering arglist_group31 with %s" % arglist_group31_values)
    return arglist_group31_values


def on_Exit_arglist_group31(arglist_group31_values):
    #Put your code here
    print("Exiting arglist_group31 with %s" % arglist_group31_values)
    return arglist_group31_values


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
    sentence : sentence_group2
    '''
    sentence_values = TagList('sentence')
    on_Enter_sentence(sentence_values)
    sentence_values.append(sentence_group2())
    on_Exit_sentence(sentence_values)

    return sentence_values

def sentence_group2():

    '''
    sentence_group2 : ( boolexp SEMI ) +
    '''
    sentence_group2_values = TagList('sentence_group2')
    on_Enter_sentence_group2(sentence_group2_values)
    sentence_group2_values.append(boolexp())
    lexx.nextToken('SEMI')
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF':
        sentence_group2_values.append(boolexp())
        lexx.nextToken('SEMI')
    on_Exit_sentence_group2(sentence_group2_values)

    return sentence_group2_values

def boolexp():

    '''
    boolexp : orexp boolexp_group5
    '''
    boolexp_values = TagList('boolexp')
    on_Enter_boolexp(boolexp_values)
    boolexp_values.append(orexp())
    boolexp_values.append(boolexp_group5())
    on_Exit_boolexp(boolexp_values)

    return boolexp_values

def boolexp_group5():

    '''
    boolexp_group5 : ( AND orexp ) *
    '''
    boolexp_group5_values = TagList('boolexp_group5')
    on_Enter_boolexp_group5(boolexp_group5_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'AND':
        boolexp_group5_values.append(lexx.nextToken('AND'))
        boolexp_group5_values.append(orexp())
    on_Exit_boolexp_group5(boolexp_group5_values)

    return boolexp_group5_values

def orexp():

    '''
    orexp : notexp orexp_group8
    '''
    orexp_values = TagList('orexp')
    on_Enter_orexp(orexp_values)
    orexp_values.append(notexp())
    orexp_values.append(orexp_group8())
    on_Exit_orexp(orexp_values)

    return orexp_values

def orexp_group8():

    '''
    orexp_group8 : ( OR notexp ) *
    '''
    orexp_group8_values = TagList('orexp_group8')
    on_Enter_orexp_group8(orexp_group8_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'OR':
        orexp_group8_values.append(lexx.nextToken('OR'))
        orexp_group8_values.append(notexp())
    on_Exit_orexp_group8(orexp_group8_values)

    return orexp_group8_values

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
    cmpexp : expr cmpexp_group13
    '''
    cmpexp_values = TagList('cmpexp')
    on_Enter_cmpexp(cmpexp_values)
    cmpexp_values.append(expr())
    cmpexp_values.append(cmpexp_group13())
    on_Exit_cmpexp(cmpexp_values)

    return cmpexp_values

def cmpexp_group13():

    '''
    cmpexp_group13 : ( BOOLOP expr ) *
    '''
    cmpexp_group13_values = TagList('cmpexp_group13')
    on_Enter_cmpexp_group13(cmpexp_group13_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'BOOLOP':
        cmpexp_group13_values.append(lexx.nextToken('BOOLOP'))
        cmpexp_group13_values.append(expr())
    on_Exit_cmpexp_group13(cmpexp_group13_values)

    return cmpexp_group13_values

def expr():

    '''
    expr : term expr_group16
    '''
    expr_values = TagList('expr')
    on_Enter_expr(expr_values)
    expr_values.append(term())
    expr_values.append(expr_group16())
    on_Exit_expr(expr_values)

    return expr_values

def expr_group16():

    '''
    expr_group16 : ( PLUSMIN term ) *
    '''
    expr_group16_values = TagList('expr_group16')
    on_Enter_expr_group16(expr_group16_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'PLUSMIN':
        expr_group16_values.append(lexx.nextToken('PLUSMIN'))
        expr_group16_values.append(term())
    on_Exit_expr_group16(expr_group16_values)

    return expr_group16_values

def term():

    '''
    term : exp term_group19
    '''
    term_values = TagList('term')
    on_Enter_term(term_values)
    term_values.append(exp())
    term_values.append(term_group19())
    on_Exit_term(term_values)

    return term_values

def term_group19():

    '''
    term_group19 : ( TIMESDIV exp ) *
    '''
    term_group19_values = TagList('term_group19')
    on_Enter_term_group19(term_group19_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'TIMESDIV':
        term_group19_values.append(lexx.nextToken('TIMESDIV'))
        term_group19_values.append(exp())
    on_Exit_term_group19(term_group19_values)

    return term_group19_values

def exp():

    '''
    exp : factor exp_group22
    '''
    exp_values = TagList('exp')
    on_Enter_exp(exp_values)
    exp_values.append(factor())
    exp_values.append(exp_group22())
    on_Exit_exp(exp_values)

    return exp_values

def exp_group22():

    '''
    exp_group22 : ( EXP factor ) *
    '''
    exp_group22_values = TagList('exp_group22')
    on_Enter_exp_group22(exp_group22_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'EXP':
        exp_group22_values.append(lexx.nextToken('EXP'))
        exp_group22_values.append(factor())
    on_Exit_exp_group22(exp_group22_values)

    return exp_group22_values

def factor():

    '''
    factor : | ( PLUSMIN expr ) | ( NUMBER ) | ( ID LPAREN arglist RPAREN ) | ( ID LPAREN RPAREN ) | ( ID LBRACK expr RBRACK ) | ( ID ) | ( STRING ) | ( LPAREN expr RPAREN ) | ( LBRACK expr factor_group25 RBRACK ) | ( LBRACK RBRACK ) | ( LCURLY pair factor_group27 RCURLY ) | ( LCURLY RCURLY )
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
        factor_values.append(factor_group25())
        factor_values.append(lexx.nextToken('RBRACK'))
    elif lexx.lookahead(1)[0].type == 'LCURLY':
        factor_values.append(lexx.nextToken('LCURLY'))
        factor_values.append(pair())
        factor_values.append(factor_group27())
        factor_values.append(lexx.nextToken('RCURLY'))
    on_Exit_factor(factor_values)

    return factor_values

def factor_group25():

    '''
    factor_group25 : ( COMMA expr ) *
    '''
    factor_group25_values = TagList('factor_group25')
    on_Enter_factor_group25(factor_group25_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'COMMA':
        factor_group25_values.append(lexx.nextToken('COMMA'))
        factor_group25_values.append(expr())
    on_Exit_factor_group25(factor_group25_values)

    return factor_group25_values

def factor_group27():

    '''
    factor_group27 : ( COMMA pair ) *
    '''
    factor_group27_values = TagList('factor_group27')
    on_Enter_factor_group27(factor_group27_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'COMMA':
        factor_group27_values.append(lexx.nextToken('COMMA'))
        factor_group27_values.append(pair())
    on_Exit_factor_group27(factor_group27_values)

    return factor_group27_values

def arglist():

    '''
    arglist : expr arglist_group31
    '''
    arglist_values = TagList('arglist')
    on_Enter_arglist(arglist_values)
    arglist_values.append(expr())
    arglist_values.append(arglist_group31())
    on_Exit_arglist(arglist_values)

    return arglist_values

def arglist_group31():

    '''
    arglist_group31 : ( COMMA expr ) *
    '''
    arglist_group31_values = TagList('arglist_group31')
    on_Enter_arglist_group31(arglist_group31_values)
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'COMMA':
        arglist_group31_values.append(lexx.nextToken('COMMA'))
        arglist_group31_values.append(expr())
    on_Exit_arglist_group31(arglist_group31_values)

    return arglist_group31_values

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


