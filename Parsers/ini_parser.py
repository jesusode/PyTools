
import lexer
from taglist import *

lexx = lexer.Lexer()

_table= [
    ["\\r?\\n","NL",None,False],
    ["\\[","LBRACK",None,False],
    ["\\]","RBRACK",None,False],
    ["=","EQUAL",None,False],
    ["[^\\r\\n\[\]=]+","TEXT",None,False],
    ["( |\t)+","WS",None,False]
]





lexx.setTable(_table)

#Codigo de inicio de usuario


#Codigo de callbacks

def on_Enter_ini(ini_values):
    #Put your code here
    print("Entering ini with %s" % ini_values)
    return ini_values


def on_Exit_ini(ini_values):
    #Put your code here
    print("Exiting ini with %s" % ini_values)
    return ini_values


def on_Enter_section(section_values):
    #Put your code here
    print("Entering section with %s" % section_values)
    return section_values


def on_Exit_section(section_values):
    #Put your code here
    print("Exiting section with %s" % section_values)
    return section_values


def on_Enter_pair(pair_values):
    #Put your code here
    print("Entering pair with %s" % pair_values)
    return pair_values


def on_Exit_pair(pair_values):
    #Put your code here
    print("Exiting pair with %s" % pair_values)
    return pair_values



#Codigo del parser
def ini():

    '''
    ini : ( section ) +
    '''
    ini_values = TagList('ini')
    on_Enter_ini(ini_values)
    ini_values.append(section())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF':
        ini_values.append(section())
    on_Exit_ini(ini_values)

    return ini_values

def section():

    '''
    section : LBRACK TEXT RBRACK NL ( pair [ LBRACK ] ) +
    '''
    section_values = TagList('section')
    on_Enter_section(section_values)
    section_values.append(lexx.nextToken('LBRACK'))
    section_values.append(lexx.nextToken('TEXT'))
    section_values.append(lexx.nextToken('RBRACK'))
    section_values.append(lexx.nextToken('NL'))
    section_values.append(pair())
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type != 'LBRACK':
        section_values.append(pair())
    on_Exit_section(section_values)

    return section_values

def pair():

    '''
    pair : TEXT EQUAL TEXT ( NL ) +
    '''
    pair_values = TagList('pair')
    on_Enter_pair(pair_values)
    pair_values.append(lexx.nextToken('TEXT'))
    pair_values.append(lexx.nextToken('EQUAL'))
    pair_values.append(lexx.nextToken('TEXT'))
    pair_values.append(lexx.nextToken('NL'))
    while lexx.lookahead(1)!= [] and not lexx.lookahead(1)[0].type == 'EOF' and lexx.lookahead(1)[0].type == 'NL':
        pair_values.append(lexx.nextToken('NL'))
    on_Exit_pair(pair_values)

    return pair_values



#Codigo de usuario

import pprint
if __name__ == '__main__':
    input = '''[section 1]
x = 90
y=erte dd ft

[section numero 2]
tralari = tralara
56 = op
[seccion3 y mas]
ff=90

'''
    lexx.setInput(input)
    tagListToString(ini())


