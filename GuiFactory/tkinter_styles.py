from typing import *

class TkinterStyle:
    '''
    Clase que representa un estilo aplicable en tkinter.
    Aceptamos: font,bg,fg,border,pad,width,height
    '''
    def __init__(self,**options):
        _allowed = ("fgcolor","bgcolor","fg","bg","font","width","height","border","height")
        self.options = options
        for item in self.options:
            assert item in _allowed


def spreadConfig(widget,config : TkinterStyle):
    #Usar esto para aplicar estilos!!!!!
    for w in widget.winfo_children():
        try:
            w.configure(**config.options)
        except:
            pass


