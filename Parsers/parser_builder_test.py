from typing import *

from parser_builder import *

#Leer gramatica para la que se quiere el parser
grammar_ = open("expressions_grammar_simple.g","r").read()

#Ponerla como input del lexer
lexx.setInput(grammar_)

#Y que ruede la bola
template = grammar()

print(template)

