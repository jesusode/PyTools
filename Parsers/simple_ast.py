#AST homogeneo (segun Parr). Necesita definir al menos un parent o None
#Implementar un metodo visit externo o una clase visitor para usarlos
class AST:

    def __init__(self,children=None,annots={},token=None,parent=None,scope=None):
        #En python36, aparentemente, si se pone en el constructor children=[], comparte la instancia de la lista
        #con TODAS las instancias de la clase y  da errores (????). Con children==None y asignando la lista vacia dentro
        #del constructor no ocurre
        self.children=[] if children==None else children
        self.annots=annots
        self.token=token
        self.parent=parent
        self.scope=scope

    def isRoot(self):
        return self.parent==None

    def isLeaf(self):
        return len(self.children)==0

    def getParent(self): #tb getSiblings,getAncestors,getWhere(filter)...
        return self.parent

    def getChildren(self):
        return self.children

    def addChild(self,child): #child as AST
        self.children.append(child)
        #_print("CHILDREN: ")
        #_print(map |(x):x.toString()| in self.children)

    def getNodeType(self):
        return self.token.type if self.token!= None else None

    def isNil(self):
        return self.token==None

    def getScope(self):
        return self.scope

    def toString(self):
        return self.token.toString() if self.token!=None else "nil"

    def toStringTree(self):
        buff=""
        #_print("SIZE CHILDREN: " + len(self.children))
        if self.children==None or len(self.children)==0:
            return self.toString()
        if not self.isNil():
            buff=buff + "("
            buff=buff + self.toString()
            buff= buff + " "

        for child in self.children:
            #_print("SEEING CHILD: " + child.toString())
            buff= buff + " "
            buff= buff + child.toStringTree()
        if not self.isNil():
            buff= buff + ")"
        return buff


def visit(ast,fun):
    assert type(ast)== AST
    fun(ast.token)
    for node in ast.getChildren():
        visit(node,fun)
