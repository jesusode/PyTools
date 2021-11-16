from typing import *
#Tablas de lenguajes->templates----------------------

#Plantillas para aplicacion wxPython
wxPyAppTemplate="""
import sys
import wx
import wx.grid
import wx.html
import wx.html2
from wx_support import *


#Soporte para obtener GUIElements por nombre---------------

__WIDGETS__ = dict()
def getGUIElement(name):
    if name in __WIDGETS__:
        return __WIDGETS__[name]
    else:
        return None

def registerGUIElement(name,elem):
    __WIDGETS__[name] = elem


#----------------------------------------------------------

app = wx.App()


#User code
{0}

app.MainLoop()
"""  

tkinterTemplate='''

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
{1}

#Inicia la secuencia de llamadas programadas a __collectValues-
root.winfo_children()[0].after(200,__collectValues)
#--------------------------------------------------------------

#main_menu
{0}

#title
{2}

#icon
{3}

root.mainloop()
print(getValues())


'''

pyQtTemplate="""


"""

xhtmlTemplate="""
<!DOCTYPE html"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>--Put your title here--</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
<script>%%SUPPORT_CODE%%</script>
<script>
$(document).ready(function() {

%%INIT_CODE%%

});
</script>
%%HEADER_CODE%%
</head>
<body>
<div id="root">
%%GUI_CODE%%
</div>
</body>
</html>"""

TEMPLATES = {
    "wx" : wxPyAppTemplate,
    "qt" : pyQtTemplate,
    "tkinter" : tkinterTemplate,
    "xhtml" : xhtmlTemplate
}



def addTemplate(name : str,template : str) -> NoReturn:
    TEMPLATES[name] = template

def getTemplate(name : str) -> str:
    assert name in TEMPLATES
    return TEMPLATES[name]