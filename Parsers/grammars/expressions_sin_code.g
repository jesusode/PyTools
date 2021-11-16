    /* Gramatica para expresiones
    de grado de complicacion media */
    grammar expr
    discard WHITESPACES end
    callbacks
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
        sentence : (boolexp SEMI)+;
        boolexp :  orexp (AND orexp)*;
        orexp : notexp (OR notexp)*;
        notexp : | (NOT cmpexp) | (LPAREN boolexp RPAREN) |(cmpexp);
        cmpexp : expr (BOOLOP expr)*;
        expr : term (PLUSMIN term)*;
        term : exp (TIMESDIV exp)*;
        exp : factor (EXP factor)*;
        /* Para factor hay que poner primero
        las opciones con mas elementos */
        factor : |(PLUSMIN expr)
                 |(NUMBER)
                 |(ID LPAREN arglist RPAREN)
                 |(ID LPAREN RPAREN)
                 |(ID LBRACK expr RBRACK)
                 |(ID)
                 |(STRING)
                 |(LPAREN expr RPAREN)
                 |(LBRACK expr (COMMA expr)* RBRACK)
                 |(LBRACK RBRACK)
                 |(LCURLY pair (COMMA pair)* RCURLY)
                 |(LCURLY RCURLY);
        arglist : expr (COMMA expr)*; 
        pair : | (NUMBER COLON expr) | (STRING COLON expr) | (ID COLON expr);
{{
import pprint
if __name__ == '__main__':
    input = "2 + 3 *6 + fn(89,a,b*56);25+l;vv(89,5,f*56);"
    lexx.setInput(input)
    #pprint.pprint(boolexp())
    tagListToString(sentence())
}}
    end