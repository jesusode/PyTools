/* Gramatica para archivos CSV */
grammar ini

callbacks

/* tokens */
tokens 
    NL -> <re>\\r?\\n</re>
    LBRACK -> <re>\\[</re>
    RBRACK -> <re>\\]</re>
    EQUAL -> <re>=</re>
    TEXT -> <re>[^\\r\\n\[\]=]+</re>
    WS -> <re>( |\t)+</re>
end

ini : (section)+;
section : LBRACK TEXT RBRACK NL (pair [LBRACK])+;
/* Esta gramatica no funciona como esta
busca pair indefinidamente. Necesita un terminador
y los ini no lo tienen */
pair : TEXT EQUAL TEXT (NL)+;

{{
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
}}


end