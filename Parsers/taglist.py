#Lista que acepta una etiqueta

from typing import *
import lexer

class TagList(list):

    def __init__(self, tag : str, *elems : List[Any]):
        '''
        Clase que representa una lista con una etiqueta.
        Necesaria para ASTs.
        '''
        self.tag = tag
        self._list = list(elems)
        self._iter = iter(self._list)

    def getList(self):
        return self._list

    def append(self,elem):
        self._list.append(elem)

    def __delitem__(self, index):
        del self._list[index]

    def __getitem__(self, index):
        return self._list[index]

    def __iter__(self):
        return self._iter

    def __next__(self):
        return self._iter.__next__()

    def __eq__(self, other):
        '''
        Para operador ==
        '''
        return self.tag == other.tag and self._list == other.getList()

    def __repr__(self):
        '''
        __repr__
        '''
        return f"{type(self).__name__}({self.tag,self._list})"



def tagListToString(tl : TagList, indent : str = ""):
    '''
    Recorre y presenta un TagList
    '''
    if type(tl) == TagList:
        print(indent + tl.tag)
    for item in tl : 
        #print(f"\nTYPE TL: {type(tl)}\n")
        if type(item) == TagList:
            #print("TAGLIST!!")
            tagListToString(item, indent = indent + "    ")
        elif type(item) == list:
            for el in item:
                tagListToString(el, indent=indent + "    ")
        elif type(item) == lexer.Token:
            print(indent + "    " + item.value)
        else: #No deberia ir por aqui a nos ser que las reglas devuelvan algo distinto a TagList
            print(indent + str(tl))



if __name__ == '__main__':
    tagl = TagList("OneList",1,2,3,4,5,6)
    print(tagl)
    print(tagl.tag)
    print(tagl.getList())
    print(tagl[1])
    print(tagl[-1])
    print(tagl[1:3])
    print(tagl[:-1])
    for item in tagl:
        print(item)