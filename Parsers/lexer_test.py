import lexer
import  pprint

words_counter={}


def wcount(tok):
    global words_counter
    if tok not in words_counter:
        words_counter[tok]=1
    else:
        words_counter[tok]+=1


table=[
    ["\s+","WHITESPACE",None,True],
    ["\.","dot",None,False],
    ["\w+","word",wcount,False],
    [",","comma",None,False],
    ["\\","colon",None,False]
	]

lexx = lexer.Lexer()
lexx.setTable(table)

texto="""En un lugar de La Mancha,
de cuyo nombre no quiero acordarme, no ha mucho
que vivia un hidalgo, de los de lanza en astillero,
adarga antigua y galgo corredor."""

lexx.setInput(texto)
tok = None

#Cuando ya no queda entrada, lexx.nextToken() genera un token de tipo EOF
while True:
    tok=lexx.nextToken()
    print(tok)
    if tok.type=="EOF": break


pprint.pprint(words_counter)

print("Ok")
