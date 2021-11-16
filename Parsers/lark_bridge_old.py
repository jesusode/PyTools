#Pruebas de gramaticas con lark

import sys
import os
import os.path

from lark import Lark,Tree,Token

import Config

from BridgeTranslator import *
from PythonTranslator import *
from GroovyTranslator import *


#Tabla de lenguajes <-> traductores
TRANSLATION_TABLE = {
    "Bridge" : translateToBridge,
    "Python" : translateToPython,
    "Groovy" : translateToGroovy,
    "Java"   : "translateToJava",
    "C"      : "translateToC",
    "C++"    : "translateToCPP"
}

prog = open("tests/test5.txt","r",encoding="utf-8").read()

prog="""
//Hay que separar el . de los numeros o da error!!
1 . to(89);
let http = {
    100 : "CONTINUE",
    200 : "OK",
    400 : "BAD REQUEST"};
assert http[200] == "OK";
http[500] = "INTERNAL SERVER ERROR";
assert http.size() == 4;
let x = from 1 to 10;
let totalClinks = 0;
let partyPeople = 100;
1 . upto(partyPeople) :> [@guestNumber] {
clinksWithGuest = guestNumber-1;
totalClinks += clinksWithGuest;
};
assert totalClinks == (partyPeople*(partyPeople-1))/2;
[1,2,3].each :> [@entry]{println(entry);};
let i = 0;
while i < 10 do
    i++;
end;
assert i == 10;
let clinks = 0;
foreach remainingGuests in from 0 to 9 do
    clinks += remainingGuests;
end;
assert clinks == (10*9)/2;
let list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
foreach j in list do
    assert j == list[j];
end;
list.each() :> [@item] {
    assert item == list[item];
};
/**switch(3) {
    case 1 : assert false; break
    case 3 : assert true; break
    default: assert false
}**/
let b = ./\w+/;
"tres".saltos.de. 5km;
(5)(pa,ti);
"""

#Hay que guardar el parser y recargarlo!!(esto no va???)
#parser = None
#if not os.path.exists("bridge.parser"):
#    print("creating parser")
#    parser = Lark.open("bridge.lark",debug = True,parser = 'lalr')
#    with open("bridge.parser","w") as f:
#        parser.save(f)
#else:
#    print("parser loaded from file")
#    parser = Lark.load("bridge.parser")


# Scannerless Earley is the default
parser = Lark.open("bridge.lark",debug = True,parser = 'lalr')
#print(parser.parse(prog).pretty())


language = Config.language
#language = "Bridge"

#Incluir el preprocesador y algo de soporte para group!!
def bridge(program):
    global TRANSLATION_TABLE,language
    parse_tree = parser.parse(program)
    translator = TRANSLATION_TABLE[language]
    for inst in parse_tree.children:
        translator(inst)
    print("code_str: %s" % Config.prog_str)
    #with open("Simulacion.py","w",encoding="utf-8") as f:
    #    f.write(Config.prog_str)
    input("algo para salir?")


if __name__ == '__main__':
    #Send in the clowns!!
    bridge(prog)


