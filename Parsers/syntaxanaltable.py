#TDA de utilidad en estudio de grmaticas y automatas

from typing import *

class SyntaxAnalTable:
    def __init__(self,fnames : List[str],cnames : List[str]):
        #assert _size(fnames)==_size(cnames)
        self.__cnames=cnames
        self.__fnames=fnames
        self.table={}
        self.table[""]=self.__cnames
        for item in self.__fnames:
            self.table[item]=[None]* len(cnames)


    def toString(self):
        return str(self.table)

    def __str__(self):
        return self.toString()


    def lookup(self,fname,cname):
        #return self.table[fname][_index(cname,self.__cnames)]
        return self.table[fname][self.__cnames.index(cname)]


    def entry(self,fname,cname,value):
        self.table[fname][self.__cnames.index(cname)]
