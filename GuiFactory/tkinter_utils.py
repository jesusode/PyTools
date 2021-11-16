#utilidades para tkinter

from typing import *

import tkinter
import tkinter.font



def getTkWidgetParent(widget):
    '''
    Obtiene el parent de un widget tkinter.
    '''
    return widget.master


class LayoutItem:
    '''
    LayoutItem
    --------

    Composite que representa un item utilizable
    para un layout.
    '''
    def __init__(self,widget,children=[],**kwargs):
        self.widget = widget
        self.children = children
        self.props = kwargs


LI = LayoutItem #alias corto

def layout(layout : List[List[LayoutItem]],fun : str = "grid"):
    '''
    layout
    ------
    Realiza un layout con fun en tkinter,
    que por defecto es grid,
    a partir de una lista de listas de LayoutItem.
    Deberia admitir y renderizar sublistas
    dentro de las listas??.
    '''
    nrows = len(layout)
    ncols=0
    for l in layout:
        if len(l) > ncols: ncols=len(l)
    for r in range(nrows):
        for c in range(ncols):
            if c < len(layout[r]):
                if fun == "grid":
                    layout[r][c].widget.grid(column=c,row=r,**layout[r][c].props)
                elif fun == "pack":
                    layout[r][c].widget.pack(**layout[r][c].props)
                else:
                    layout[r][c].widget.place(**layout[r][c].props)



def buildTkinterTreeview(tv,dct,start_level=""):
    '''
    Monta un treeview a partir de un diccionario.
    '''
    level = ""
    actual_level = ""
    #print(tv)
    for item in dct:
        actual_level = tv.insert(level if start_level=="" else start_level,tkinter.END,text = item)
        #Segun sea, metemos text,columnas o tree
        els=dct[item]
        if type(els) == str:
            tv.insert(actual_level,tkinter.END,text=els)
        elif type(els)==dict:
            #print("Llamada recursiva!")
            buildTkinterTreeview(tv,els,actual_level)
        elif type(els) == list:
            #Naif: si el[0] es str todos str
            # y si es [],todos []
            if type(els[0])== str:
                for it in els:
                    tv.insert(actual_level,tkinter.END,text=it)
            elif type(els[0])==dict:
                #print("Llamada recursiva intenna!")
                buildTkinterTreeview(tv,els,actual_level)
            elif type(els[0]) == list:
                for it in els:
                    tv.insert(actual_level,tkinter.END,values=it)
            else:
                raise Exception("Error: Tipo no valido para un elemento de un Treeview")



