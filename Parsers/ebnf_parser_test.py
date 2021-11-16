__version__ = 1.0

import  pprint
from typing import *
from py_desc_parser import *
from py_packrat_parser import *
from grammar_utils import *

if __name__ == '__main__':
    #g = open("grammars/expressions_sin_code.g").read()
    #g = open("grammars/ini.g").read()
    #g = open("grammars/csv.g").read()
    #g = open("grammars/expressions_packrat.g").read()
    g = open("grammars/streamy_sin_code.g").read()
    lexx.setInput(g)
    #pprint.pprint(lexx.tokenize(g))
    #'''
    g_id,toks,tree,pre_code,post_code,toks_to_ignore,toks_to_discard,callbacks,callbacks_all = grammar()

    #pprint.pprint()
    _table=rulesToTable(tree)
    #pprint.pprint(getTerminalsAndNotTerminals(tree))
    #pprint.pprint(tree)
    print(reprRules(tree))
    #pprint.pprint(nullables(tree,_table))
    #print(isNullable(_table["sentence"],_table,{}))

    #_firsts = firsts(tree)
    #pprint.pprint(_firsts)

    #pprint.pprint(follows(tree,_firsts))

    #pprint.pprint(tree)

    #rls = EBNFToBNF(tree)
    #pprint.pprint(rls)
    #print(reprRules(rls)) #,"zzexpressions_bnf.txt"))
    print("---------------------------------------")
    print("Pruebas de generacion de parsers packrat")
    print("---------------------------------------")
    #parser_code = buildPackratParser(tree,False,[])
    #print(parser_code)
    #packPackratParser(g_id,tree[0][0].value,toks,parser_code,pre_code,post_code,toks_to_ignore)
    #print("=============")



    


    '''
    for item in tree:
        #pprint.pprint(item)
        r = GrammarRule(item)
        print("---------------------------------------")
        print(f"Regla: {r.id}")
        pprint.pprint(r.rhs)
        #print(r.toString())
        print(r.toText())
        print(f"Terminals: {r.terminals}")
        print(f"Nonterminals: {r.nonterminals}")
        print(f"\nHasOptions:{r.hasOptions()}")
        print(f"\nHasClosures:{r.hasClosures()}")
        print(f"\nHasEmpty:{r.hasEmpty()}")
        print("---------------------------------------")
        print(f"Options:")
        pprint.pprint(r.getOptions())
        print("------------------------------------")
        print("---------------------------------------")
        print(f"Closures:")
        pprint.pprint(r.getClosures())
        print("------------------------------------")

    print("---------------------------------------")
    print("Pruebas de generacion de parsers")
    print("---------------------------------------")
    pbuff = io.StringIO()
    ruleToDescParser(tree[0][1:],pbuff)
    print(pbuff.getvalue())
    print("=============")
    pbuff2 = io.StringIO()
    ruleToDescParser(tree[1][1:],pbuff2)
    print(pbuff2.getvalue())
    print("=============")
    pbuff3 = io.StringIO()
    ruleToDescParser(tree[2][1:],pbuff3)
    print(pbuff3.getvalue())
    print("========------------==========")
    #print(buildDescParser([tree[0],tree[1],tree[2]]))

    pprint.pprint(tree)
    for item in tree:
        print(reprRule(item))
        #print(f"Rule {item[0].value} : Left recursive: {isLeftRecursive(item)}")
        #print(f"Rule {item[0].value} : Right recursive: {isRightRecursive(item)}")
        print(f"\nGROUPS:")
        pprint.pprint(getGroups(item,[]))
        print("------------------------------------------------------")
  
    
    print(f"\nGROUPS:")
    grps = []
    getGroups(tree[0],grps)
    pprint.pprint(grps)
    print(reprRule(tree[0]))
    print("------------------------------------------------------")
    '''
    '''
    grps = []
    nogrps = []
    getGroups(tree[0],grps,processed=nogrps)
    print(f"grps: {grps}")
    #print(f"processed : {nogrps}")
    print("-------------------------------------")
    rules = []
    for grp in grps:
        rls = []
        groupToRules(grp,"factor",0,rls)
        pprint.pprint(rls)
        for item in rls:
            print(reprRule(item))
    '''
    #print(EBNFToBNF(tree[0]))
    #opts=[]
    #getOptions(tree[0],opts)
    #print("OPTIONS:")
    #pprint.pprint(opts)
    #print(reprRule(tree[0]))

    parser_code = buildDescParser(tree,callbacks,toks_to_discard,callbacks_all)
    #print(parser_code)
    packParser(g_id,toks,parser_code,pre_code,post_code,toks_to_ignore,toks_to_discard)
    #print(tree[0])
    #print(getGroups(tree[0]))


    print("OK")


