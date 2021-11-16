#Pruebas de typefactoies

import sys
sys.path.append('.')

from typefactories import *




r = anonymObjectFactory(a=90,b=80,c='tralari',square=lambda x : x*x)
rp = anonymObjectFactory(**{'a':90,'b':80,'c':'tralari','square' : lambda x : x*x})
print(r)
print(r.c)
print(r.square(9))
print(rp)
print(rp.c)
#Classfactory
def Rob_init(self, name):
    self.name = name

Robot2 = classFactory("Robot2", 
            (), 
            {"counter":0, 
            "__init__": Rob_init,
            "sayHello": lambda self: "Hi, I am " + self.name})
print(Robot2)
bob = Robot2("Bob")
bob.sayHello()
#Pruebas de typed tuples
tpl = typedTuplesFactory("IntStr",["intfld","strfld"],["int",'str'],file = "IntStr.py",install=True)
print(tpl)

tpl2 = tpl.IntStr(666,"arrepienetete")
#Tambien puede ser exec(tpl,globals() si install es False)
print(tpl2.intfld)
print(tpl2.strfld)
print(len(tpl2))
for item in tpl2:
    print(item)
print(tpl2[0])
print(tpl2[1])
print('----------------------')
union = typedUnionFactory("IntOrStr",["intval","strval"],["int","str"],file ="IntOrStr.py",install = True)
print(union)
union1 = union.IntOrStr(989)
print(union1)
print(union1.type)
print(union1.strval)
print(union1.intval)
print('----------------------')
reg = typedRegisterFactory("PersonReg",["name","age","alive"],["str","int","bool"],file="PersonReg.py",install = True)
reg1 = reg.PersonReg(name = "Paco",age = 32,alive = True)
print(reg1)
print(reg1.name)
print(reg1.age)
print(reg1.alive)
print(reg1.keys())
print(reg1.values())
print('-------------------------------')
switch = switchFactory(["x==1","x==2","x==3","x==4"],
["print('value_1')","print('value_2')","print('value_3')", "print('value_4')"],
"print('default_value')")
print(switch)
a = pyCompile("l='abcd'")
print(a)
exec(a)
print(l)
x=1
exec(switch)
f = dynFunFactory("foo","def foo() : return 'bar'")
print(f())
switchf = switchFunFactory("x",["x==1","x==2","x==3","x==4"],
["print('value_1')","print('value_2')","print('value_3')", "print('value_4')"],
"print('default_value')")
print(switchf)
switchf(x)
x=3
switchf(x)