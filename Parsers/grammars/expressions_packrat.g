    /* Gramatica para expresiones
    de grado de complicacion media */
    grammar expr
    discard WHITESPACES end
    callbacks
{{
import re
import sys
import io
}}
        /* aqui van los tokens */
        tokens 
            WHITESPACES -> <re>\\s+</re>
            PLUSMIN -> <re>\\+|\\-</re>
            TIMESDIV -> <re>\\*|/</re>
            EXP -> <re>\\^</re>
            LPAREN -> <re>\(</re>
            RPAREN -> <re>\)</re>
            LBRACK -> <re>\[</re>
            RBRACK -> <re>\]</re>
            LCURLY-> <re>\{</re>
            RCURLY -> <re>\}</re>
            NUMBER -> <re>[0-9]+</re>
            COMMA -> <re>,</re>
            COLON -> <re>:</re>
            DOT -> <re>\\.</re>
            AND -> <re>and</re>
            OR -> <re>or</re>
            NOT -> <re>not</re>
            BOOLOP -> <re><=|>=|>|<|==|!=<|></re>
            ID -> <re>[a-zA-Z_][a-zA-Z_0-9]*(\\.[a-zA-Z0-9_]+)*</re>
            STRING -> <re>\\"[^\\"]+\\"</re>
            SEMI -> <re>;</re>
        end
        /* Solo para ejercicios 
        prog : (sentence (TIMESDIV)+ {{print("Code repetitivo")}})+;*/
        prog : (sentence (TIMESDIV)+ {{print("Code repetitivo")}})+;
        sentence : |(expr SEMI) |(expr DOT);
        expr : NUMBER PLUSMIN NUMBER DOT (TIMESDIV)?;
{{
import pprint
if __name__ == '__main__':
    input = "2+3.4-5.2323+54.69-89."
    lexx.setInput(input)
    #pprint.pprint(boolexp())
    print(startPackrat())
}}
                
    end