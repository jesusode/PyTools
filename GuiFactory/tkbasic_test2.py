#Pruebas de tkbasic


import  tkbasic


def btncode():
    print("Boton pulsado!!")
    tkbasic.setFormItemValue("applet1","label2","En un lugar de La Mancha...")
    tkbasic.callFormItem("applet1","pass","configure",{"background":"blue","foreground":"red"})
    tkbasic.callFormItem("applet1","button1","state",[["disabled"]])

def init_code():
    print("Codigo de inicio del formulario")

def guardarNota():
    print("Guardar nota")
    nn = tkbasic.getTkFile("File picker","open")
    print(nn)


  



#print(tkbasic.messageBox("titulillo","mensajillo","ok","info"))
# print(tkbasic.messageBox("titulillo","mensajillo 2","yesno","warning"))
# print(tkbasic.messageBox("titulillo","mensajillo 3","yesnocancel","question"))
#print(tkbasic.getTkColor("Color picker"))
# print(tkbasic.getTkFile("File picker","open"))
# print(tkbasic.getTkFile("File picker","save"))
# print(tkbasic.getTkFiles("Multiple file picker"))
# print(tkbasic.getTkDir("Dir picker"))


appopts= {"name":"applet1",
          "title":"Titulo del formbox",
          "width":800
          ,"height":600,
          "x":200,
          "y":200,
          "resize":0,
          "oninit":init_code,
          "minwidth":100,
          "minheight":100,
          "sizer":"grid",
          "style":"xpnative"
        }

labs=["Elegir fecha","Texto de la nota","Guardar nota"]

labels= {"Elegir fecha":"text",
         "Texto de la nota":"text",
         "Guardar nota":"button"
        }


values={"Texto de la nota":"Texto de la nota",
        "Guardar nota": guardarNota
    }


notitas=tkbasic.formBox(appopts,labs,labels,values,1,0)

print(notitas)

print("Ok!")