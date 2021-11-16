/* Gramatica para expresiones
    de grado de complicacion media */
grammar expr_bnf
ignore WHITESPACES end
discard SEMI end
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


sentence: sentence_group2;
sentence_group2: | ( boolexp SEMI ) | ( sentence_group2 );
boolexp: orexp boolexp_group5;
boolexp_group5: | ( empty ) | ( AND orexp boolexp_group5 );
orexp: notexp orexp_group8;
orexp_group8: | ( empty ) | ( OR notexp orexp_group8 );
notexp: | ( NOT cmpexp ) | ( LPAREN boolexp RPAREN ) | ( cmpexp );
cmpexp: expr cmpexp_group13;
cmpexp_group13: | ( empty ) | ( BOOLOP expr cmpexp_group13 );
expr: term expr_group16;
expr_group16: | ( empty ) | ( PLUSMIN term expr_group16 );
term: exp term_group19;
term_group19: | ( empty ) | ( TIMESDIV exp term_group19 );
exp: factor exp_group22;
exp_group22: | ( empty ) | ( EXP factor exp_group22 );
factor: | ( PLUSMIN expr ) | ( NUMBER ) | ( ID LPAREN arglist RPAREN ) | ( ID LPAREN RPAREN ) | ( ID LBRACK expr RBRACK ) | ( ID ) | ( STRING ) | ( LPAREN expr RPAREN ) | ( LBRACK expr factor_group25 RBRACK ) | ( LBRACK RBRACK ) | ( LCURLY pair factor_group27 RCURLY ) | ( LCURLY RCURLY );
factor_group25: | ( empty ) | ( COMMA expr factor_group25 );
factor_group27: | ( empty ) | ( COMMA pair factor_group27 );
arglist: expr arglist_group31;
arglist_group31: | ( empty ) | ( COMMA expr arglist_group31 );
pair: | ( NUMBER COLON expr ) | ( STRING COLON expr ) | ( ID COLON expr );


{{
import pprint
if __name__ == '__main__':
    input = "2 + 3 *6 + fn(89,a,b*56);25+l;vv(89,5,f*56);"
    lexx.setInput(input)
    #pprint.pprint(boolexp())
    tagListToString(sentence())
}}

end
