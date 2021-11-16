
import sys
sys.path.append('.')

from functypes import *

null = NullValue()
print(null.value)
strvalue = MutableValue("tralari")
strvalue.value = 777
print(strvalue.value)
iors = MutableOneOfValue(666,int,str,float)
print(iors.type)
print(iors.value)
print(iors.options)
iors.value = "xx"
print(iors.value)
intval = TypedValue(999,int)
print(intval.value)
intfloat = MutableEitherValue(65535,int,float)
print(intfloat.left)
print(intfloat.right)
print(intfloat.hasLeft())
print(intfloat.hasRight())
intfloat.left = 354
print(intfloat.left)
print(intfloat.right)
print(intfloat.hasLeft())
print(intfloat.hasRight())
print('------------------------------')
opt1 = OptionalValue()
opt2 = MutableOptionalValue(54321)
print(opt1)
print(opt1.value)
print(opt1.hasValue())
print(opt2)
print(opt2.value)
print(opt2.hasValue())
opt2.value="XXY"
print(opt2.value)
m3 = MutableTypedValue(3.25,float)
print(m3)
print(m3.type)
print(m3.value)
m3.value= 2.717215
print(m3)
m4 = MutableOptionalTypedValue(None,str)
print(m4)
print(m4.hasValue())
m4.value="qwerty"
print(m4)
print(m4.value)
print(m4.hasValue())
auto1 = AutoTypedValue(6789)
print(auto1)
print(auto1.type)
print(auto1.value)
#auto1.value=45
mauto = MutableAutoTypedValue("ww")
print(mauto)
mauto.value= "ZZZ"
print(mauto.type)
print(mauto.value)
print('-------------------------------------')
fun = TypedFunction(lambda x,y : x+y,[int,int],int)
print(fun)
print(fun(2,2))