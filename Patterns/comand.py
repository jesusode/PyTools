#Module patterns

from typing import *

class Command:
    '''
    Command
    '''
    def __init__(self, dofun : Callable, undofun : Callable,metadata = ""):

        self._dofun = dofun
        self._undofun = undofun
        self._metadata = metadata
    
    def do(self,*args,**kwargs):
        self._dofun(*args,**kwargs)
    
    def undo(self,*args,**kwargs):
        self._undofun(*args,**kwargs)
    
    @property
    def metadata(self):
        return self._metadata


class Macro(Command):
    '''
    Macro
    '''
    def __init__(self,cmdlist : List[Command],metadata = ''):
        #super(None,None,metadata)
        self._commands = cmdlist
        self._metadata = metadata
    
    @property
    def commands(self):
        return self._commands
    
    def do(self,*args,**kwargs):
        for cmd in self._commands : 
            cmd.do(*args,**kwargs)
    
    def undo(self,*args,**kwargs):
        for cmd in self._commands : 
            cmd.undo(*args,**kwargs)


if __name__ == '__main__':

    c1 = Command(print,lambda : print('Undoing print'),'print command')
    c2 = Command(lambda x,y : print(x+y),lambda : print("undoing sum command"),'sum command')
    m2 = Macro([Command(lambda *args: print('Command in macro2'),lambda : print('undoing command in macro2'),"macro2 metadata")])
    m1 = Macro([c2,c1,m2],'macro sum and print')
    m1.do(3,5)
    m1.undo()
    print(m1.metadata)
    for cmd in m1.commands:
        print(cmd)
        print(cmd.metadata)