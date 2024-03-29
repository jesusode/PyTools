#Pruebas de gramaticas con lark

from lark import Lark
import turtle

turtle_grammar= """
start: instruction+

instruction: MOVEMENT NUMBER -> movement
    | "c" COLOR [COLOR] -> change_color
    | "fill" code_block -> fill
    | "repeat" NUMBER code_block -> repeat

code_block: "{" instruction+ "}"

MOVEMENT: "f"|"b"|"l"|"r"

COLOR: LETTER+
%import common.LETTER
%import common.INT -> NUMBER
%import common.WS
%ignore WS

"""

text = """
c red yellow
fill { repeat 36 {
f200 l170
}}
"""

def run_instruction(t):
    if t.data == 'change_color':
        turtle.color(*t.children) # We just pass the color names as-is
    elif t.data == 'movement':
        name, number = t.children
        {
        'f': turtle.fd,
        'b': turtle.bk,
        'l': turtle.lt,
        'r': turtle.rt,
        }[name](int(number))
    elif t.data == 'repeat':
        count, block = t.children
        for i in range(int(count)):
            run_instruction(block)
    elif t.data == 'fill':
        turtle.begin_fill()
        run_instruction(t.children[0])
        turtle.end_fill()
    elif t.data == 'code_block':
        for cmd in t.children:
            run_instruction(cmd)
    else:
        raise SyntaxError('Unknown instruction: %s' % t.data)


parser = Lark(turtle_grammar,parser='lalr') # Scannerless Earley is the default
#print(parser.parse(text))
#print(parser.parse(text).pretty())

def run_turtle(program):
    parse_tree = parser.parse(program)
    for inst in parse_tree.children:
        run_instruction(inst)

def main():
    while True:
        code = input('> ')
    try:
        run_turtle(code)
    except Exception as e:
        print(e)

run_turtle(text)
input()

