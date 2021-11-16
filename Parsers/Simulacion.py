#Soporte para simulacion de sistemas
import time 
import copy 
import math 
from typing import * 
class SystemEvent :
  def  __init__ (self, type_ : str  , source, timestamp : str  , value : Dict[str,float]  ):
    self.type_ = type_
    self.source = source
    self.timestamp = timestamp
    self.value = value
  def  toString (self):
    return f'''<<Class SystemEvent: type:{self.type_} , source:{self.source} , timestamp:{self.timestamp} , value: {str(self.value)}>>'''
  def  __repr__ (self):
    return self.toString()

class SystemVariable :
  def  __init__ (self, name : str  , dependencies : Dict[str,float]  , updatefun, info = ""):
    self.name = name
    self.dependencies = dependencies
    assert self.dependencies != {} 
    self.updatefun = updatefun
    self.value = 0
    self.observers = []
    self.info = ""
    self.update(SystemEvent("", self, str(time.time()), self.dependencies))
  def  addObserver (self, observer : "SystemVariable"  ):
    self.observers.append(observer)

        #Notify new observer
    news = copy.deepcopy(self.dependencies)
    news[self.name] = self.value
    observer.update(SystemEvent("", self, str(time.time()), news))
  def  removeObserver (self, observer : "SystemVariable"  ):
    if observer in self.observers:
      del self.observers[self.observers.index(observer)]

  def  update (self, changes : SystemEvent  ):

        #print(f"Recibido evento en var : {self.name}\n");

        #print(changes);
    for item  in changes.value.keys():
      if item in self.dependencies.keys():
        self.dependencies[item] = changes.value[item]


    self.value = self.updatefun(self)

        #Meter el nombre y el nuevo valor en los cambios y reenviarlo
    if changes.source != self:
      evt = SystemEvent("", self, str(time.time()), copy.deepcopy(changes.value))
      evt.value[self.name] = self.value

            #print(f"Broadcasting event from {self.name}";
      self.notify(evt)

  def  notify (self, changes : SystemEvent  ):
    for observer  in self.observers:
      observer.update(changes)

  def  toString (self):
    return f'''<<Class SystemVariable: name: {self.name}, dependencies: {self.dependencies}, updatefun: {self.updatefun}, value: {self.value}, observers:{self.observers}>>'''
  def  __repr__ (self):
    return self.toString()

class System :
  def  __init__ (self, name : str  , variables : List[SystemVariable]  , info = ""):
    self.name = name
    self.variables = variables
    self.info = info
    self.vartable = {} 
    for var  in self.variables:
      self.vartable[var.name] = var

  def  toString (self):
    return f'''<<Class System: name: {self.name}, variables: \n,{self.variables}, info:{self.info}>>'''
  def  __repr__ (self):
    return self.toString()
  def  getVariable (self, varname):
    if varname in self.vartable.keys():
      return self.vartable[varname]
    else:
      return None

  def  getValues (self):
    values = {} 
    for variable  in self.variables:
      values[variable.name] = variable.value

    return values
  def  updateVariable (self, vname, evt):
    if vname in self.vartable.keys():
      self.vartable[vname].update(evt)


def  ln (x):
  return math.log(x, math.e)

#let evt1 as SystemEvent = new SystemEvent("cambio temporal",null,"2018-03-04 14:00:67",{"conc":234.89});
#print(evt1);
Vd = SystemVariable("Vd", {"vd":50.0}, lambda x : x.dependencies["vd"]
)
conc_inic = SystemVariable("Co", {"dosis":100.0, "Vd":20.0}, lambda x : x.dependencies["dosis"] / x.dependencies["Vd"]
)
kelim = SystemVariable("Kelim", {"Ke":0.003}, lambda x : x.dependencies["Ke"]
)
timer = SystemVariable("timer", {"t":1.0}, lambda x : x.dependencies["t"]
)
t12 = SystemVariable("t12", {"Kelim":1.0}, lambda x : ln(2) / x.dependencies["Kelim"]
)
clr = SystemVariable("Cl", {"Kelim":1.0, "Vd":1.0}, lambda x : x.dependencies["Vd"] * x.dependencies["Kelim"]
)
AUCiv = SystemVariable("AUCiv", {"Co":1.0, "Kelim":1.0}, lambda x : x.dependencies["Co"] / x.dependencies["Kelim"]
)
conc_plasm = SystemVariable("Cp", {"Co":1.0, "Ke":1.0, "timer":1.0}, lambda x : x.dependencies["Co"] * math.exp(-x.dependencies["Ke"] * x.dependencies["timer"])
)
conc_inic.addObserver(conc_plasm)
conc_inic.addObserver(AUCiv)
kelim.addObserver(conc_plasm)
kelim.addObserver(t12)
kelim.addObserver(clr)
Vd.addObserver(conc_inic)
Vd.addObserver(clr)
timer.addObserver(conc_plasm)
print("--------------------------")
print(conc_plasm)
print(conc_plasm.value)

#print(_type(@(x){x;}));
print("--------------------------")
conc_inic.update(SystemEvent("cambio temporal", None, str(time.time()), {"dosis":23.489}))
print(conc_plasm.value)
print("-----------------------------")
sys = System("Conc plasmatica", [Vd, t12, clr, AUCiv, conc_inic, kelim, timer, conc_plasm])
print(sys)
print("-----------------------")
print(sys.getValues())
print("-----------------------")
sys.updateVariable("timer", SystemEvent("cambio temporal", None, "2018-03-04 14:00:67", {"t":20000.0}))
print("-----------------------")
print(sys.getValues())
print(conc_plasm.value)
