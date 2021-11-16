#Pruebas de gramaticas con lark

import sys

from lark import Lark

import Config

from BridgeTranslator import *
from PythonTranslator import *
from GroovyTranslator import *
import preprocessor

from bridge_parser import Lark_StandAlone


#Tabla de lenguajes <-> traductores
TRANSLATION_TABLE = {
    "Bridge" : translateToBridge,
    "Python" : translateToPython,
    "Groovy" : translateToGroovy,
    "Java"   : "translateToJava",
    "C"      : "translateToC",
    "C++"    : "translateToCPP"
}


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
#parser = Lark_StandAlone()
print(parser)
#print(parser.parse(prog).pretty())


language = Config.language
#language = "Bridge"

#Incluir algo de soporte para group!!
#Incluir soporte para traducir a mas de un lenguaje!
def bridge(program,debug = False):
    global TRANSLATION_TABLE,language
    if debug==True:
        print(parser.parse(program).pretty())
    parse_tree = parser.parse(program)
    print(parser.parse(program).pretty())
    translator = TRANSLATION_TABLE[language]

    for inst in parse_tree.children:
        print(type(inst))
        translator(inst)
    #raise Exception("DEBUG STOP!")
    #print("code_str: %s" % Config.prog_str)
    #with open("Simulacion.py","w",encoding="utf-8") as f:
    #    f.write(Config.prog_str)
    return Config.prog_str

def processCommandline(cmdline):
    pass

def main():
    #Send in the clowns!!
    cmdline = sys.argv
    fil = ""
    translated = ""
    output_file = "zzzz_output.bridge"
    exec_code = False
    processCommandline(cmdline)
    #print(cmdline)
    if len(cmdline)==1:
        print("Usage:  lark_bridge file_to_translate [options]")
        print("You must pass a file to translate!")
        sys.exit(1)
    else:
        fil = open(cmdline[1],"r",encoding=Config.encoding).read()

    preprocessed = preprocessor.preprocessor(fil) 
    translated= bridge(preprocessed)#,True)
    print(translated)
    if exec_code:
        exec(translated)
    #f = open(output_file,"w",encoding = Config.encoding)
    #f.write(translated)
    #f.close()


if __name__ == '__main__':
    main()
