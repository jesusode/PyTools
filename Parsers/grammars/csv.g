/* Gramatica para archivos CSV */
grammar csv

callbacks

/* tokens */
tokens 
    NL -> <re>\\r?\\n</re>
    COMMA -> <re>,</re>
    QUOTE -> <re>\\"</re>
    SCHAR -> <re>[^\\",\\r\\n]+</re>
    WS -> <re>( |\t)+</re>
end

csv : header (record)+;
header : record;
record : fields NL;
fields : field (COMMA fields)*;
field : (WS)? rawfield (WS)?;
rawfield : |(QUOTE SCHAR QUOTE)|(SCHAR);

{{
import pprint
if __name__ == '__main__':
    input = '''campo1,campo2,campo3,campo4
uno,"dos","tres",cuatro y cinco
v1,v2,v3,v4
'''
    lexx.setInput(input)
    tagListToString(csv())
}}




end