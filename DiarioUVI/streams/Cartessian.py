#Cartessian

class Cartessian:
    '''
    Cartessian.
    '''
    def __init__(self,iterable=None):

        self.iterable=iterable
        self._closed=False
        if self.iterable== None: self.iterable=[] 
        self.numels=0
        self.conts=[]
        self.fullconts=[]
        print("self.iterable: " + str(self.iterable))
        self.cardinality=1
        for el in self.iterable:
            self.cardinality=self.cardinality * len(el)
        
        print("self.cardinality: " + self.cardinality)
        #Inicializar contadores
        for item in self.iterable:
            self.conts.append(0)
            self.fullconts.append(len(item)-1)
        
        if self.cycle==None: self.cycle=False 

    def hasNext(self):
        if self.numels < self.cardinality:
            return True
        else:
            return False
    
    def next(self):
        resul=[]
        actual=[]
        if self.hasNext():
            if self.numels==0: #Devolver primer elemento del producto
                #resul= map |(x):x[0]| in self.iterable
                resul = [x[0] for x in self.iterable]
                self.numels+=1
                return resul
            else:
                #Incrementar self.conts de fin a inicio hasta fullconts
                proposed=len(self.conts)-1
                #_print("proposed: " + proposed)
                while True:
                    if self.conts[proposed]<self.fullconts[proposed]:
                        self.conts[proposed]+=1
                        break
                    else:
                        self.conts[proposed]=0
                        proposed-=1
                    
                
                #_print("self.conts: "  + _tostring(self.conts))
                #_print("self.fullconts: " + _tostring(self.fullconts))
                #Coger elemento actual del producto cartesiano
                for i in range(len(self.conts)):
                    actual.append(self.iterable[i][self.conts[i]])
                self.numels+=1
                #_print("actual: " + _tostring(actual))
                return actual
            
        else:
            return None
    
        
    def close(self):
        self._closed=True

    def copy(self):
        return Cartessian(iterable=self.iterable)
    
      