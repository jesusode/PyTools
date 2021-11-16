#tk_treeview

from typing import *

import tkinter as tk
from tkinter import ttk
import Tix

import functools
import pprint


def getTkWidgetParent(widget):
    '''
    Obtiene el parent de un widget tkinter.
    '''
    return widget.master

class GridItem:
    '''
    GridItem
    --------

    Clase que guarda widgets tkinter
    junto con un diccionario de propiedades.
    Para usar con widget.grid(...).
    '''
    def __init__(self,widget,**kwargs):
        self.widget = widget
        self.props = kwargs

GI = GridItem #alias corto

def gridLayout(layout : List[List[GridItem]]):
    '''
    Realiza un layout con grid() en tkinter
    a partir de una lista de listas de GridItem.
    Deberia admitir y renderizar sublistas
    dentro de las listas.
    '''
    nrows = len(layout)
    ncols=0
    for l in layout:
        if len(l) > ncols: ncols=len(l)
    for r in range(nrows):
        for c in range(ncols):
            if c < len(layout[r]):
                layout[r][c].widget.grid(column=c,row=r,**layout[r][c].props)







def buildTkinterTreeview(tv,dct,start_level=""):
    '''
    Monta un treeview a partir de un diccionario.
    '''
    level = ""
    actual_level = ""
    #print(tv)
    for item in dct:
        actual_level = tv.insert(level if start_level=="" else start_level,tk.END,text = item)
        #Segun sea, metemos text,columnas o tree
        els=dct[item]
        if type(els) == str:
            tv.insert(actual_level,tk.END,text=els)
        elif type(els)==dict:
            print("Llamada recursiva!")
            buildTkinterTreeview(tv,els,actual_level)
        elif type(els) == list:
            #Naif: si el[0] es str todos str
            # y si es [],todos []
            if type(els[0])== str:
                for it in els:
                    tv.insert(actual_level,tk.END,text=it)
            elif type(els[0])==dict:
                print("Llamada recursiva intenna!")
                buildTkinterTreeview(tv,els,actual_level)
            elif type(els[0]) == list:
                for it in els:
                    tv.insert(actual_level,tk.END,values=it)
            else:
                raise Exception("Error: Tipo no valido para un elemento de un Treeview")



tree = {
    "Level One" : ["one","two","three"],
    "Level Two" : ["uno","dos","tres"],
    "Level Three" : ["ein", "schwai","thrai"],
    "Level Four" : "Hell!",
    "List" : [["the","list","is","here"],["the","list","is","here"]],
    "complicated" : {"subl1" : "item1",
                    "sub2" : "item2"
                    }
}


main_window = tk.Tk()
main_window.title("Vista de árbol en Tkinter")

frame = ttk.Frame(main_window)
'''
treeview = ttk.Treeview(frame,columns=("c1", "c2","c3","c4"))
treeview.pack()
bt = tk.Button(frame,text="Click me!")
bt.place(x= 50,y=50,height = 100,width = 100)

buildTkinterTreeview(treeview,tree)
'''
btns = []
for i in range(5):
    row=[]
    for j in range(6):
        row.append(GridItem(tk.Button(frame,text=f"\uE002 A...Boton [{i},{j}]",font="Arial 12 bold",fg="green",bg="white"),sticky="nsew"))
    btns.append(row)
#pprint.pprint(btns)
lbl = tk.Label(frame,text="\u274fMira qué hermoso ramillete de botones!")

gridLayout([[GridItem(lbl)]] + btns)

frame.pack(fill=tk.BOTH)

for opt in frame.configure():
    print(opt)

def spreadConfig(widget,config : Dict[str,Any]):
    #Usar esto para aplicar estilos!!!!!
    for w in widget.winfo_children():
        w.configure(**config)


spreadConfig(frame,{'font':"JohnDoe 18 italic",'border':"2"})

#Usar esto para aplicar estilos!!!!!
#for w in frame.winfo_children():
#    w.configure(font="Arial 18 italic",border="2")
#    print(w)

main_window.mainloop()
print('\u2620')