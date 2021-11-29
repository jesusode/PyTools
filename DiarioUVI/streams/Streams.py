#Stream
from typing import *
import abc
from  streams.IteratorBase import *
from streams.IteratorObserver import *
from streams.ListIterator import *
from streams.dictutils import *
from functools import reduce


class Stream:

    '''
    Stream
    ------

    Clase que implementa un Stream basado en un Iterador.
    Sólo asume que el iterador tiene los dos métodos
    definidos en IteratorBase: next() y hasNext().
    Permite deifinir un gran número de operaciones
    a realizar según se va recorriendo el stream.
    Unas son "lazy" y no obligan a realizar ningún cálculo,
    y otras no lo son y en cuanto se usen obligarán a 
    realizar el Stream.
    '''

    def __init__(self : "Stream" ,iterator=None):
        '''
        Constructor
        -----------

        Sólo requiere un iterador, que puede ser None.
        '''
        self.iterator=iterator
        self._ops_list=[]
        self._ops_funcs=[]
        self.num_takes=0
        self.num_skips=0
        self.num_takewhiles=0
        self.num_skipwhiles=0

    #Funciones lazy. No fuerzan la evaluacion del stream
    #y son encadenables mediante interfaz fluida
    #Hay numeros magicos: corregirlo

    def map(self : "Stream",fun):
        '''
        map
        ---

        Map es una función lazy que no obliga a
        realizar el stream. Aplica una función fun
        a cada elemento del stream.

        Parámetros
        ----------

        fun : Callable([Any],Any) -- Función a aplicar a cada elemento.
        '''
        self._ops_list.append(1)
        self._ops_funcs.append([fun])
        return self

    def flatMap(self : "Stream",fun):
        '''
        flatMap
        ---

        flatMap es una función lazy que no obliga a
        realizar el stream. Reduce las listas que pudiera
        haber y luego aplica la función fun.

        Parámetros
        ----------

        fun : Callable([Any],Any) -- Función a aplicar a cada elemento.
        '''
        self._ops_list.append(5)
        self._ops_funcs.append([fun])
        return self

    def flatFilter(self : "Stream",fun):
        '''
        flatFilter
        ---

        flatFilter es una función lazy que no obliga a
        realizar el stream. Aplica un predicado fun
        a cada elemento del stream y recurivamente a las sublistas
        que hubiera.

        Parámetros
        ----------

        fun : Callable([Any],bool) -- Predicado a aplicar a cada elemento.
        '''        
        self._ops_list.append(16)
        self._ops_funcs.append([fun])
        return self

    def select(self : "Stream",fun):
        '''
        select
        ------

        Select es un alias de map

        Parámetros
        ----------

        fun : Callable([Any],Any) -- Función a aplicar a cada elemento.
        '''        
        return self.map(fun)

    def filter(self : "Stream",pred):
        '''
        filter
        ------

        filter es una función lazy que no obliga a
        realizar el stream. Aplica una predicado pred
        a cada elemento del stream.

        Parámetros
        ----------

        pred : Callable([Any],bool) -- Función a aplicar a cada elemento.
        '''        
        self._ops_list.append(2)
        self._ops_funcs.append([pred])
        return self

    def where(self : "Stream",pred):
        '''
        where
        ---

        Where es un alias de filter

        Parámetros
        ----------

        pred : Callable([Any],bool) -- Función a aplicar a cada elemento.
        '''        
        return self.filter(pred)

    def all(self : "Stream",pred): #Es equivalente de verdad a filter??
        '''
        all
        ---

        All es otro alias de filter

        Parámetros
        ----------

        pred : Callable([Any],bool) -- Función a aplicar a cada elemento.
        '''
        return self.filter(pred)

    def take(self : "Stream",num):
        '''
        take
        ---

        take es una función lazy que no obliga a
        realizar el stream. Coge num elementos
        del stream

        Parámetros
        ----------

        num : int -- Número de elementos a coger.
        '''        
        self._ops_list.append(3)
        self._ops_funcs.append([lambda: num,0])
        return self

    def takeWhile(self : "Stream",pred):
        '''
        takeWhile
        ---------

        takeWhile es una función lazy que no obliga a
        realizar el stream. Coge elementos del stream
        mientras se cumpla pred. En cuanto falle se detiene.

        Parámetros
        ----------

        pred : Callable([Any],bool) -- Función a aplicar a cada elemento.
        '''        
        self._ops_list.append(4)
        self._ops_funcs.append([pred,True])
        return self

    def skip(self : "Stream",num):
        '''
        skip
        ---

        Skip es una función lazy que no obliga a
        realizar el stream. Se salta num elementos del stream.

        Parámetros
        ----------

        num : int -- Número de elementos a saltar.
        '''        
        self._ops_list.append(5)
        self._ops_funcs.append([lambda: num,0])
        return self

    def skipWhile(self : "Stream",pred):
        '''
        skipWhile
        ---

        skipWhile es una función lazy que no obliga a
        realizar el stream. Se salta los elementos del stream
        mientras se cumpla pred. Se detiene cuando falle.

        Parámetros
        ----------

        pred : Callable([Any],bool) -- Predicado a aplicar a cada elemento.
        '''
        self._ops_list.append(6)
        self._ops_funcs.append([pred,True])
        return self

    def foreach(self : "Stream",fun):
        '''
        foreach
        ---

        Foreach es una función lazy que no obliga a
        realizar el stream. Aplica una función fun
        a cada elemento del stream, pero no recoge el valor producido
        si lo hay.

        Parámetros
        ----------

        fun : Callable([Any],Any) -- Función a aplicar a cada elemento.
        '''        
        self._ops_list.append(7)
        self._ops_funcs.append([fun])
        return self

    def zip(self : "Stream",fun,iter):
        self._ops_list.append(8)
        self._ops_funcs.append([fun,iter])
        return self

    def multiZip(self : "Stream",fun,iterlist):
        self._ops_list.append(9)
        self._ops_funcs.append([fun,iterlist])
        return self

    def mix(self : "Stream",fun,iter):
        self._ops_list.append(10)
        self._ops_funcs.append([fun,iter])
        return self

    def multiMix(self : "Stream",fun,iterlist):
        self._ops_list.append(11)
        self._ops_funcs.append([fun,iterlist])
        return self

    def concat(self : "Stream",fun,iterator):
        self._ops_list.append(12)
        self._ops_funcs.append([fun,iterator])
        return self

    def multiConcat(self : "Stream",fun,iterlist):
        self._ops_list.append(13)
        self._ops_funcs.append([fun,iterlist])  
        return self

    def join(self : "Stream",iterator,fun1,fun2,mapfun):
        self._ops_list.append(14)
        self._ops_funcs.append([lambda: 0,[iterator,fun1,fun2,mapfun]])
        return self

    #Fin de funciones lazy
    
    #Funciones que obligan a realizar el stream

    def orderBy(self : "Stream",fun):
        assert self.iterator != None
        return ListIterator(iterable=sorted(self.toList(),key=fun))


    def reverse(self : "Stream"):
        assert self.iterator != None
        return ListIterator(iterable= self.toList()[::-1])


    def distinct(self : "Stream"):
        assert self.iterator != None
        temp=[]
        iter= ListIterator(iterable=self.toList())
        while iter.hasNext():
            t= iter.next()
            if t not in temp:   
                temp.append(t)
        return ListIterator(iterable=temp)


    def intersect(self : "Stream",iter):
        assert self.iterator != None
        innerit=   ListIterator(iterable=self.toList())
        temp=[]
        temp2=[]
        while iter.hasNext() :  
            temp2.append(iter.next())

        while innerit.hasNext() :  
            t= innerit.next()
            if t in temp2 and t not in temp:
                temp.append(t)
        return ListIterator(iterable=temp)


    def union(self : "Stream",iter):
        assert self.iterator != None
        temp=[]
        innerit= ListIterator(iterable=self.toList())
        while innerit.hasNext() :  
            t= innerit.next()
            if t not in temp  :
                temp.append(t)
        while iter.hasNext() :  
            t2= iter.next()
            if t2 not in temp   :
                temp.append(t2)
        return ListIterator(iterable=temp)


    def except_(self : "Stream",iter):
        assert self.iterator != None
        temp=[]
        temp2=[]
        innerit=  ListIterator(iterable=self.toList())
        while iter.hasNext():  
            t2= iter.next()
            if t2 not in temp:
                temp2.append(t2)

        while innerit.hasNext():  
            t= innerit.next()
            if t not in temp2:
                temp.append(t)
        return  ListIterator(iterable=temp)


    def groupJoin(self : "Stream",it,p1,p2,mapf):
        assert self.iterator != None
        joined=[]
        temp=[]
        innerit= ListIterator(iterable=self.toList())
        while innerit.hasNext():
            temp.append(innerit.next())
        grouped=  groupby(temp,p1)
        temp2=[]
        while it.hasNext(): 
            temp2.append(it.next())
        grouped2= groupby(temp2,p2)

        for item in grouped :
            joined.append(mapf(grouped[item],grouped2[item]))

        return  ListIterator(iterable=joined)


    def contains(self : "Stream",elem):
        if elem in self.toList():
            return True
        else:  
            return False


    def count(self : "Stream"):
        return  len(self.toList())


    def groupBy(self : "Stream",fun):
        return groupby(self.toList(),fun)


    def groupMap(self : "Stream",fung,funlist,passList=False):
        temp= groupby(self.toList(),fung)
        for key in temp.keys() :
            for fun in funlist :  
                if passList == False:
                    temp[key]= map(fun,temp[key])
                else:
                    temp[key]= fun(temp[key])              
        return temp


    def multiGroup(self : "Stream",flist):
        return multiGroup(self.toList(),flist)


    def toDictionary(self : "Stream",fun):
        return self.groupBy(fun)


    def toLookup(self : "Stream",keysfun,valuesfun):
        lookup={}
        for item in self.toList():
            if not keysfun(item) in lookup:
                lookup[keysfun(item)]=[valuesfun(item)]
            else:
                lookup[keysfun(item)].append(valuesfun(item))
        return lookup


    def first(self : "Stream"):
        return self.toList()[0]


    def last(self : "Stream"):
        return self.toList()[-1]


    def elementAt(self : "Stream",pos):
        return self.toList()[pos]


    def nth(self : "Stream",pos):
        return self.elementAt(pos)


    def reduce(self : "Stream",fun,init=None):
        if init == None :
            return reduce(fun,self.toList())
        else: 
            return reduce(fun,self.toList(),init)
  

    def aggregate(self : "Stream",fun,init=None):
        return self.reduce(fun,init)


    def partialReduce(self : "Stream",fun,initval):
        t= self.toList()
        temp=[]
        for i in range(len(t)+1):
            temp.append(reduce(fun,t[0:i]))
        return temp


    def partialAggregate(self : "Stream",fun):
        return self.partialReduce(fun)


    def paginate(self : "Stream",pagesize):
        assert pagesize > 0
        t=self.toList()
        temp=[]
        pages= int( len(t)/pagesize)
        cont=0
        while cont + pagesize <  len(t) : 
            temp.append(t[cont : cont+pagesize])
            cont=cont + pagesize

        if cont <  len(t)  :
            temp.append(t[cont : None])
        return temp


    def sum(self : "Stream"):
        return reduce(lambda x,y:x+y ,self.toList())


    def average(self : "Stream"):
        t= self.toList()
        return reduce(lambda x,y: x+y, t)/ len(t)


    def max(self : "Stream"):
        return reduce (lambda x,y: x if x > y else y , self.toList())


    def min(self : "Stream"):
        return reduce(lambda x,y: x if x < y else y,self.toList())


    def any(self : "Stream",pred):
        for item in self.toList() : 
            if pred(item) == True :
                return True
        return False


    def single(self : "Stream",pred):
        Truecont=0
        for item in self.toList() : 
            if pred(item) == True  :
                Truecont+=1
        if Truecont == 0 or Truecont >1  :
            return False
        else:  
            return True


    def sequenceEqual(self : "Stream",seq):
        t=self.toList()
        assert  len(t) ==  len(seq)
        for i in range(len(t)) :
            if t[i] != seq[i] :
                return False
        return True

    def ofType(self : "Stream",typ):
        temp=[]
        for item in self.toList():  
            if type(item) == typ:
                temp.append(item)
        return temp
    
    #Ejecutar todas las funciones lazy con un solo pase al hacer collect
    def collect(self : "Stream"):
        collected=[]
        #Generar siguiente elemento
        elem_counter=0
        skip_counter=0
        take_counter=0
        take_while_flag=True
        skip_while_flag=True
        collect_in_sequence=False
        #setvar cont=0;
        temp=None
        #print('TAMANYO de self._ops_list ' +  len(self._ops_list));
        while self.iterator.hasNext() :
            #cont+=1;
            #if cont == 100  : raise 'PARADA.............'; end;
            temp=self.iterator.next()
            #print("\n>>>>>temp: " + _tostring(temp_) + "\n");
            #Y aplicarle todas las funciones.
            for i in range(len(self._ops_list)):
                #print('------Vuelta del for--------');
                ftype=self._ops_list[i]
                f=self._ops_funcs[i][0]
                #Coger argumento si lo hay
                argument=None
                if  len(self._ops_funcs[i])>1:
                    argument=self._ops_funcs[i][1]
                    #print("Valor de argument: " + _tostring(argument));
                #Proceder segun tipo de funcion
                if ftype  ==  1 : #map,select
                    if temp != None :
                        #_print("temp en map: " + _tostring(temp));
                        temp =f(temp)
                elif ftype ==  2 : #filter,where
                    if temp != None and f(temp) == False: 
                        temp = None
                elif ftype  ==  3 : #take
                    t_counter=argument
                    if t_counter > f()-1:
                        temp=None
                        #print('Llamada a break!!');
                        break
                    else:
                        self._ops_funcs[i][1]+=1
                        #print('Por take');
                elif ftype  ==  4 : #takeWhile
                    #_print("f(temp) en takeWhile: " + _tostring(f(temp)));
                    t_while_flag=argument
                    if t_while_flag == True:
                        if f(temp) == False:
                            temp = None
                            self._ops_funcs[i][1]=False
                    else:
                        temp=None
                elif ftype  ==  5 : #skip
                    s_counter=argument
                    if s_counter < f():
                        temp=None
                        self._ops_funcs[i][1]+=1
                        break
                elif ftype  ==  6 : #skipWhile
                    s_while_flag=argument
                    if s_while_flag == True:
                        if f(temp) == True:
                            temp = None
                            break
                        else:
                            #_print("Poniendo flag a False!!");
                            self._ops_funcs[i][1]=False

                elif ftype  ==  7: #foreach
                    if temp !=  None:
                         f(temp)
                elif ftype  ==  8 : #zip
                    if temp != None:
                        temp=f(temp,argument.next() if argument.hasNext() else None)
                elif ftype  ==  9 : #multiZip
                    if temp != None:
                        _args=[]
                        _args.append(temp)
                        for item in argument :
                            _args.append((item.next() if item.hasNext() else None))
                        temp=f(*_args)
                elif ftype  ==  10 : #mix
                    if temp != None:
                        l=[f(temp)]
                        l.append(f(argument.next() if argument.hasNext() else None))
                        temp=l
                        collect_in_sequence=True
                elif ftype  ==  11 : #multiMix
                    if temp != None:
                        l=[f(temp)]
                        for item in argument:
                            l.append(f(item.next() if item.hasNext() else None))
                        temp=l
                        collect_in_sequence=True
                elif ftype  ==  12 : #concat
                    if temp != None  :
                        l=[temp]
                        if argument.hasNext():
                            l.append(f(argument.next()))
                        else:
                            l.append(None)
                        #l.append(f(argument.next() if argument.hasNext()else None);
                        temp=l
                        collect_in_sequence=True
                elif ftype  ==  13 : #multiConcat
                    if temp != None:
                        l=[temp]
                        for item in argument:
                            l.append(f(item.next() if item.hasNext() else None))
                        temp=l
                        collect_in_sequence=True
                elif ftype ==  14 : #join
                    it,p1,p2,mapf=argument
                    u=it.next()
                    if p1(temp) == p2(u):
                        temp= mapf(temp,u)
                    else:
                        temp=None
                elif ftype  ==  15 : #flatMap
                    if temp != None:
                        #assert issubclass(temp,Iterator);
                        collect_in_sequence=True
                        l=[]
                        #Parche para aprovechar si es una lista
                        if type(temp) == type([])  :
                            temp= ListIterator(iterable=temp)
                        while temp.hasNext() :
                            l.append(f(temp.next()))
                        temp=l
                elif ftype  ==  16 : #flatFilter
                    if temp != None:
                        collect_in_sequence=True
                        l=[]
                        while temp.hasNext():
                            k= temp.next()
                            if f(k) == True:
                                l.append(k)
                        temp=l
                else :
                    raise Exception(f"La opcion {i} no esta implementada")
                #print("Temp al final de los cases en vuelta del for: " + _tostring(temp_));
            #print('----SALIMOS DEL FOR-----');
            elem_counter+=1
            #print('collect_in_sequence: ' + str(collect_in_sequence));
            if temp  !=  None:
                if collect_in_sequence == True:
                    for el in temp :
                        collected.append(el)
                    collect_in_sequence=False
                else:
                    #print("Metiendo en collected: " + _tostring(temp_));
                    collected.append(temp)
        return ListIterator(iterable=collected)


    def toList(self : "Stream"):
        lst=[]
        collected=self.collect()
        cont=0
        while collected.hasNext():
            lst.append(collected.next())
            cont+=1
        return lst


    def copy(self : "Stream"):
        bs=  Stream(iterator=self.iterator.copy())
        #Como se puede copiar en uso, copiamos todo el estado tambien
        bs._ops_list=self._ops_list[:]
        bs._ops_funcs=self._ops_funcs[:]
        bs.num_takes=self.num_takes
        bs.num_skips=self.num_skips
        bs.num_takewhiles=self.num_takewhiles
        bs.num_skipwhiles=self.num_skipwhiles
        return bs


    #Interfaz Observer/Observable
    def addObserver(self : "Stream", observer : IteratorObserver) -> None:
        self._observers.append(observer)

    def removeObserver(self : "Stream", observer : IteratorObserver) -> None:
        if observer in self._observers:
            del self._observers[self._observers.index(observer)]

    def _notifyObservers(self : "Stream", evt : Any) -> None:
        for observer in self._observers:
            observer.onIterNext(evt)