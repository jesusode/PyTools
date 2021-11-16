import typing
from typing import *


lst : List[int] = [1,2,3,4,5]

print(type(lst))
print(typing._type_check(List[List[int]],"Es una lista de ints",False))
