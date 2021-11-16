/* Gramatica para expresiones
    de grado de complicacion media */
grammar expr_bnf
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


sentence: sentence_group2;
sentence_group2: | ( boolexp SEMI ) | ( sentence_group2 );
boolexp: orexp boolexp_group5;
boolexp_group5: | ( empty ) | ( AND orexp boolexp_group5 );
orexp: notexp orexp_group8;
orexp_group8: | ( empty ) | ( OR notexp orexp_group8 {{print("Code repetitivo")}});
notexp: | ( NOT cmpexp ) | ( LPAREN boolexp RPAREN ) | ( cmpexp );


end
