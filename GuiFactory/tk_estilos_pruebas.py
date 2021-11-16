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