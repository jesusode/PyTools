#Pruebas de tkbasic


import  tkbasic


def btncode():
    print("Boton pulsado!!")
    tkbasic.setFormItemValue("applet1","label2","En un lugar de La Mancha...")
    tkbasic.callFormItem("applet1","pass","configure",{"background":"blue","foreground":"red"})
    tkbasic.callFormItem("applet1","button1","state",[["disabled"]])

def init_code():
    print("Codigo de inicio del formulario")

def archivo():
    print("Menu archivo")

def editar():
    print("Menu editar")

def submenucode():
    print("submenu code")

def init_code():
    print("Codigo de inicio")
  



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
          "sizer":"pack",
          "style":"xpnative"
        }

labs=["pass","label1","label2","list1","button1","image1"]

labels= {"pass":"password",
         "label1":"text",
         "label2":"textbox",
         "list1":"combo",
         "image1":"label",
         "button1":"button"
        }

valores=["one","two","three","four"]

values={"label1":"Valor por defecto",
        "list1":valores,
        "image1":"lena.jpg",
        "button1":btncode
    }

#Menus
menulabels=["menu1","menu2","menu3"]

submenu=[ ["ayuda","-","ayuda2","-","ayuda3"],
          [submenucode,None,submenucode,None,submenucode]
        ]

menucodes= {"menu1": archivo,
            "menu2": editar,
            "menu3": submenu
        }


formvals=tkbasic.formBox(appopts,labs,labels,values,1,0,menulabels,menucodes)

print(formvals)

print("Ok!")