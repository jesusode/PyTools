

from tkinter import *
from tkinter import ttk
from tksheet import Sheet
import Tix
from tkinterweb import HtmlFrame,HtmlLabel


#Soporte para obtener GUIElements por nombre---------------

__WIDGETS__ = dict()
def getGUIElement(name):
    if name in __WIDGETS__:
        return __WIDGETS__[name]
    else:
        return None

def registerGUIElement(name,elem):
    __WIDGETS__[name] = elem


__VALUES__=dict()
def __collectValues():
    print("Llamada a __collectValues...")
    for widget in __WIDGETS__:
        if hasattr(__WIDGETS__[widget],"get"):
            if __WIDGETS__[widget].winfo_exists():
                __VALUES__[widget] = __WIDGETS__[widget].get()
    #Para que se ejecute una y otra vez
    root.winfo_children()[0].after(20,__collectValues)

def getValues():
    return __VALUES__
#----------------------------------------------------------


root = Tk()


#Asegurarse de que se recogen los valores mientras
#existan los widgets
def onExitApp():
    print("Saliendo de la app...")
    root.destroy()
root.protocol("WM_DELETE_WINDOW",onExitApp)

#User code
def onBtnClicked(evt):
    print("Button Clicked!!!")
    getGUIElement("txt1").insert(0,"Cambiado desde dentro!!!!")
    print(f"Values:  {getValues()}")

def onExitFrame(evt):
    print("Se ha cerrado el Frame!!")

def onOpenFile():
    print("Llamada a onOpenFile!!")

def onExit():
    print("Llamada a onExit!!")

root.geometry("400x400")
root.title("Pruebas de Tkinter")
root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(0, weight = 1)

main_menu = Menu(tearoff=0)
filemenu = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label='Archivo',menu=filemenu)
editmenu = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label='Editar',menu=editmenu)
helpmenu = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label='Ayuda',menu=helpmenu)
filemenu.add_command(label='Abrir',command=onOpenFile,accelerator='Ctrl+O')
filemenu.add_separator()
filemenu.add_command(label='Salir',command=onExit,accelerator='Ctrl+S')
frame1 = Frame(root)
registerGUIElement('frame1',frame1)
frame1.configure(bg='blue')

txt1 = ttk.Entry(frame1)
registerGUIElement('txt1',txt1)
txt1.configure(text='Valor Inicial')

btn1 = ttk.Button(frame1)
registerGUIElement('btn1',btn1)
btn1.configure(text='Push Me!')

btn2 = Button(frame1)
registerGUIElement('btn2',btn2)
btn2.configure(text='Another one!')
btn2.configure(bg='red')
btn2.configure(fg='white')
btn2.configure(font='JohnDoe 24 bold')

sheet1 = Sheet(frame1,data=[[1,2,3],[4,5,6]])
registerGUIElement('sheet1',sheet1)


btn1.bind('<Button-1>', onBtnClicked)
#Hay que poner codigo para grid??
#frame1.grid(column=0,row=0,columnspan=4,rowspan=4,sticky="nsew")
frame1.pack(anchor="sw")
txt1.grid(column=1,row=0,rowspan=2)
btn1.grid(column=2,row=0,rowspan=2)
btn2.grid(column=0,row=3,columnspan=3,sticky="nsew")
sheet1.grid(column=0,row=4,columnspan=4,sticky="nsew")
print(frame1.grid_slaves())
root.config(menu=main_menu)

import tkinter.font
import pprint
pprint.pprint(tkinter.font.families())




root.winfo_children()[0].after(20,__collectValues)
root.mainloop()
print(getValues())


