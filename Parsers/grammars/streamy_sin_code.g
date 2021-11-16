    /* Gramatica para expresiones
    de grado de complicacion media */
    grammar streamy
    ignore WHITESPACES end
    discard WHITESPACES WITH IS SET end
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
            PIPE -> <re>\|></re>
            AND -> <re>\\band\\b</re>
            OR -> <re>\\bor\\b</re>
            NOT -> <re>\\bnot\\b</re>
            STREAM -> <re>\\bstream\\b</re>
            QUERY -> <re>\\bquery\\b</re>
            ENCODING -> <re>\\bencoding\\b</re>
            IMPORT -> <re>\\bimport\\b</re>
            SEPARATOR -> <re>\\bseparator\\b</re>
            OBSERVERS -> <re>\\bobservers\\b</re>
            SHOW -> <re>\\bshow\\b</re>
            HEADERS -> <re>\\bheaders\\b</re>
            RANDOM -> <re>\\brandom\\b</re>
            SET -> <re>\\bset\\b</re>
            IS -> <re>\\bis\\b</re>
            AS -> <re>\\bas\\b</re>
            DB -> <re>\\bdb\\b</re>
            WITH -> <re>with</re>
            BOOLOP -> <re><=|>=|>|<|==|!=<|></re>
            STREAMOP -> <re>@[a-z]+</re>
            ID -> <re>[a-zA-Z_][a-zA-Z_0-9]*(\\.[a-zA-Z0-9_]+)*</re>
            STRING -> <re>\\"[^\\"]+\\"</re>
            SEMI -> <re>;</re>
            EQUAL -> <re>=</re>
        end
        script : (sent SEMI)+;
        sent : | (STREAM streamdef) 
               | (QUERY dbquery) 
               | (ENCODING expr)
               | (IMPORT expr)
               | (SEPARATOR expr)
               | (SHOW expr)
               | (SET ID EQUAL ID) 
               | (SET ID COLON EQUAL ID streampipe) 
               | (ID streampipe) 
               | (boolexp);
        streamdef : ID IS source (WITH HEADERS (ID)+)? (WITH OBSERVERS (ID)+)?;
        source : |(FILE expr) | (DB dbquery) | (RANDOM expr) | (expr);
        dbquery : QUERY ID WITH expr (AS expr)?;
        streampipe : (PIPE (STREAMOP)+ boolexp)+;
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
    input = """
    encoding "latin-1";
    separator ",";
    stream hemos is "hemos20.csv" with headers nombre nhc organismo with observers urines totals;
    hemos |> @select [x[2],x[4]] |> @filter x[4] == "Pseudomonas"
          |> @save "Pseudomonas20.csv" |> @export "Pseudomonas20.pdf";
    set hemos2 = hemos;
    stream cosita is 
            db query antibiogramas with "select * from atbs" as mysql 
            with headers uno dos tres 
            with observers o1 o2 o45;
    stream randoms is random ["normal",50,10,5000] 
           with headers gg hh jj with observers totals;
    show randoms;
    set result := randoms |> @flat @filter x < 200;
    """
    lexx.setInput(input)
    tagListToString(script())
}}
    end