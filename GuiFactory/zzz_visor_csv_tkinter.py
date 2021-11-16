

from tkinter import *
from tkinter import ttk
from tksheet import Sheet
from tkinterweb import HtmlFrame,HtmlLabel
from GuiFactory.utils import ScrollableListbox,buildTkinterTreeview
from GuiFactory.tkinter_styles import TkinterStyle,spreadConfig
from fontselect import FontSelect


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
    #print("Llamada a __collectValues...")
    for widget in __WIDGETS__:
        if hasattr(__WIDGETS__[widget],"get"):
            if __WIDGETS__[widget].winfo_exists():
                if type(__WIDGETS__[widget]) != Text:
                    __VALUES__[widget] = __WIDGETS__[widget].get()
                else:
                    __VALUES__[widget] = __WIDGETS__[widget].get("1.0","end") 
        elif type(__WIDGETS__[widget]) in [Radiobutton,Checkbutton,Scale]:
            #print("Buscando variables....")
            __VALUES__[widget] = eval(widget + "_var").get()
        elif type(__WIDGETS__[widget]) == Sheet: 
            __VALUES__[widget] = __WIDGETS__[widget].get_sheet_data(get_header=True) 
        elif type(__WIDGETS__[widget]) == ScrollableListbox:
            __VALUES__[widget] = [__WIDGETS__[widget].listbox.get(x) for x in __WIDGETS__[widget].listbox.curselection()]
        elif type(__WIDGETS__[widget]) == ttk.Treeview:
            __VALUES__[widget] = [__WIDGETS__[widget].set(x) for x in __WIDGETS__[widget].selection()]
    #Para que se ejecute una y otra vez
    root.winfo_children()[0].after(200,__collectValues)

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
main_menu = Menu(tearoff=0)
filemenu = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label='Archivo',menu=filemenu)
editmenu = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label='Editar',menu=editmenu)
helpmenu = Menu(main_menu,tearoff=0)
main_menu.add_cascade(label='Ayuda',menu=helpmenu)
filemenu.add_command(label='Abrir',accelerator='Ctrl+O')
filemenu.add_separator()
filemenu.add_command(label='Salir',command=onExitApp,accelerator='Ctrl+S')
Tab1 = ttk.Notebook(root)
registerGUIElement('Tab1',Tab1)
Tab1.pack(expand='1',fill='both')


frame1 = Frame(Tab1)
registerGUIElement('frame1',frame1)
frame1.grid(row=0,column=0)
frame1.configure(bg='blue')

text1 = Text(frame1)
registerGUIElement('text1',text1)
text1.grid(row=0,column=0)


fs1 = FontSelect(frame1)
registerGUIElement('fs1',fs1)
fs1.grid(row=0,column=1)


tv1 = ttk.Treeview(frame1,columns = ['header1','header2','header3','header4'])
registerGUIElement('tv1',tv1)
tv1.grid(row=0,column=2)


sheet1 = Sheet(frame1,data=[['No data']],headers=['Sin Encabezados'])
registerGUIElement('sheet1',sheet1)
sheet1.grid(row=1,column=0)


chk1 = Checkbutton(frame1, text='Check me if you can!!')
registerGUIElement('chk1',chk1)
chk1_var = IntVar()
chk1.config(variable=chk1_var)
chk1.grid(row=1,column=1)


scale1 = Scale(frame1, from_=0,to=50)
registerGUIElement('scale1',scale1)
scale1_var = DoubleVar()
scale1.config(variable=scale1_var)
scale1.grid(row=1,column=2)


list1 = ScrollableListbox(frame1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,selectmode='extended')
registerGUIElement('list1',list1)
list1.grid(row=2,column=1)


spin1 = Spinbox(frame1, from_=0,to=10)
registerGUIElement('spin1',spin1)
spin1.grid(row=2,column=2)


combo1 = ttk.Combobox(frame1, values=['uno','dos','tres','cuatro'])
registerGUIElement('combo1',combo1)
combo1.grid(row=2,column=0)



#Crear un estilo simple
from tkinter_utils import buildTkinterTreeview


estilo1 = TkinterStyle(font = "Arial 12 bold",fg = "red",bg="black")
#Y aplicarlo
spreadConfig(frame1,estilo1)
#--------

#Montar un Treeview a partir de un diccionario
_tree = {"root" : {
                     "level1" : ["uno","dos","tres"],
                     "level12" : ["cuatro",
                                  {"cinco" : ["seis,siete"]},
                                  ["ocho","nueve","diez"]
                                 ]
                  }

}

buildTkinterTreeview(tv1,_tree)
Tab1.add(frame1,text='aqui el frame1')

#Inicia la secuencia de llamadas programadas a __collectValues-
root.winfo_children()[0].after(200,__collectValues)
#--------------------------------------------------------------

#main_menu
root.config(menu=main_menu)

#title
root.title('Titulo de la aplicacion')

#icon
root.wm_iconbitmap('iconos/brush.ico')

root.mainloop()
print(getValues())


