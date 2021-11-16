#
from types import CodeType
from typing import *
from xmlutils import (xpath,flat)
#import streams
from streams import dictutils
from streams.dictutils import splitDictByPreds

from GuiFactory.bases import *
from GuiFactory.templates import *
from GuiFactory.utils import *

import sys
sys.path.append("../..")

import pprint

#Funciones de utilidad----------------------------------------------
def readf(path, encoding = "utf-8"):
    '''
    readf
    -----
    Lee el contenido de un archivo.
    '''
    return open(path,"r",encoding=encoding).read()

def compileCode(code : str) -> CodeType:
    '''
    compileCode
    ------------
    Compila y devuelve code en el 
    contexto actual.
    '''
    return compile(code,"<string>","exec")

#--------------------------------------------------------------------


#-----------------------------------------------------------------
#Estos tienen elementos dentro que hay que coger y guardar para
#meter despues de que se creen!!----------------------------------
special_containers = ["ttk.Notebook","Grip??"]
special_containers_code = []
#-----------------------------------------------------------------



class PyWxEventRenderer(EventRendererBase):
    '''
    Implementación de eventtRenderer para wxPython
    ---------------------------------------------------
    '''

    def __init__(self):
        self.events_code = []

    def render(self,event_descriptors):
        for event in event_descriptors:
            #print(event.attrib)
            self.events_code.append(f"{event.attrib['for']}.Bind({event.attrib['name']}, {event.attrib['code']}, id={event.attrib['for']}.Id)")
        return "\n".join(self.events_code)

class PyWxRenderer(GUIElementRendererBase):
    '''
    Implementación de GUIElementRenderer para wxPython
    ---------------------------------------------------
    '''
    def __init__(self):
        self.template=""

    def render(self,guielem):
        preds=[lambda x: x=="constructor",
                lambda x:x!="constructor" and x in ["parent","id","pos","size","style","name","title","label","validator","value"],
                lambda x:x not in ["parent","id","pos","size","style","name","title","label","constructor","validator","value"]]
        constructor,celems,nocelems= splitDictByPreds(guielem.properties,preds)
        #print(constructor)
        #print(celems)
        #print(nocelems)
        self.template=""
        #Patch para el WebView
        guiel_paren="("
        if "WebView" in guielem.class_ :
            guiel_paren=".New("
        self.template+= guielem.name + " = " + guielem.class_ + guiel_paren
        #Buscar elementos del constructor en propiedades
        self.template+= constructor["constructor"] if constructor!={} else ""
        consels=[]
        for item in celems:
            #print(f"Procesando item {item}")
            consels.append(item + " = " + celems[item])
        self.template += ",".join(consels) + ")\n"

        #Cambio: registrar el nombre para uso posterior-----------
        self.template += f"registerGUIElement('{guielem.name}',{guielem.name})\n"
        #---------------------------------------------------------

        #print("self.template aqui: " + self.template)
        noconsels=[]
        for item in nocelems:
            noconsels.append(guielem.name + "." + "Set" + item + "(" + nocelems[item] + ")")
        #Procesar elementos de elements si hay que hacerlo
        #proportion=0, flag=0, border=0,

        if "Sizer" in guielem.class_ :
            for item in guielem.elements:
                #_print("procesando item: " + _tostring(item))
                self.template+= guielem.name + ".Add(" + item[0].name # + ")\n"
                self.template+= ", proportion=" + item[1]["proportion"] + ", flag=" + item[1]["flag"] +  ", border=" + item[1]["border"] + ")\n"
        self.template+= "\n".join(noconsels) + "\n"
        return self.template

class PyWxMenuRenderer(MenuRendererBase):
    def __init__(self):
        self.menus_code = []

    def render(self,menu_descriptors):
        menubars,menuitems = menu_descriptors

class tkinterEventRenderer(EventRendererBase):
    '''
    Implementación de EventRenderer para tkinter
    ---------------------------------------------------
    '''

    def __init__(self):
        self.events_code = []

    def render(self,event_descriptors):
        for event in event_descriptors:
            #print(event.attrib)
            name_corrected = event.attrib['name'] if event.attrib['name'][0:3]=="WM_" else "<" + event.attrib['name'] + ">"
            self.events_code.append(f"{event.attrib['for']}.bind('{name_corrected}', {event.attrib['code']})")
        return "\n".join(self.events_code)

class tkinterMenuRenderer(EventRendererBase):
    '''
    Implementación de MenuRenderer para tkinter
    ---------------------------------------------------
    '''

    def __init__(self):
        self.menus_code = []

    def render(self,menu_descriptors):
        menubars,menuitems = menu_descriptors
        for menu in menubars:
            print(menu.attrib)
            #Buscar si parent es "" entonces es el principal. Si no, ponerlo en su padre
            parent = menu.attrib["parent"]
            if parent=="":
                self.menus_code.append(f"{menu.attrib['name']} = Menu(tearoff={menu.attrib['tearoff']})")
            else:
                mcode=f"{menu.attrib['name']} = Menu({parent},tearoff={menu.attrib['tearoff']})"
                mcode += f"\n{parent}.add_cascade(label='{menu.attrib['text']}',menu={menu.attrib['name']})"
                self.menus_code.append(mcode)
        for item in menuitems:
            #print(item.attrib.items())
            #Proceder segun el tipo de menu a crear
            #[check,radio,separator,text]
            kind = item.attrib['kind']
            if kind == "separator":
                mcode = f"{item.attrib['parent']}.add_separator()"
            elif kind == "radio":
                mcode = f"{item.attrib['parent']}.add_separator()"
            elif kind == "check":
                mcode = f"{item.attrib['parent']}.add_separator()"
            else: #text
                mcode = f"{item.attrib['parent']}.add_command(label='{item.attrib['text']}'"
                if "code" in item.attrib and item.attrib["code"]!="":
                    mcode+= f",command={item.attrib['code']}"
                if "image" in item.attrib and item.attrib["image"]!="":
                    mcode+= f",image={item.attrib['image']}"
                if "compound" in item.attrib and item.attrib["compound"]!="":
                    mcode+= f",compound={item.attrib['compound']}"
                if "accelerator" in item.attrib and item.attrib["accelerator"]!="":
                    mcode+= f",accelerator='{item.attrib['accelerator']}'"
                mcode +=")"
            self.menus_code.append(mcode)
        #print("\n".join(self.menus_code))
        return "\n".join(self.menus_code)

class tkinterRenderer(GUIElementRendererBase):
    '''
    Implementación de GUIElementRenderer para tkinter
    ---------------------------------------------------
    '''
    def __init__(self):
        self.template=""

    def render(self,guielem):
        #print(guielem)
        global special_containers,special_containers_code
        preds=[lambda x: x=="constructor",
                lambda x:x!="constructor" and x in ["parent","id","pos","size","style","name","title","label","validator","value"],
                lambda x:x not in ["parent","id","pos","size","style","name","title","label","constructor","validator","value"]]
        constructor,celems,nocelems= splitDictByPreds(guielem.properties,preds)

        #print(f"constructor:{constructor}")
        #print(f"celems:{celems}")
        #print(f"nocelems:{nocelems}")
        self.template=""
        guiel_paren="("
        self.template += guielem.name + " = " + guielem.class_ + guiel_paren
        #Buscar elementos del constructor en propiedades si lo hay
        self.template+= constructor["constructor"] if constructor!={} else ""
        consels=[]
        for item in celems:
            #print(f"Procesando item {item}")
            if item not in ["parent","_"]:
                consels.append(item + " = '" + celems[item] + "'")
            else:
                consels.append(celems[item])
        self.template += ",".join(consels) + ")\n"

        #Cambio: registrar el nombre para uso posterior-----------
        self.template += f"registerGUIElement('{guielem.name}',{guielem.name})\n"
        #---------------------------------------------------------


        #Cambio para crear las variables de los widgets que dependen de ellas----------
        if guielem.class_ in ["Checkbutton", "Radiobutton","Scale"]:
            #Creamos una variable con el nombre del widget y el sufijo "_var"
            if guielem.class_!="Scale":
                self.template += guielem.name + "_var = IntVar()\n"
            else:
                self.template += guielem.name + "_var = DoubleVar()\n" 
            self.template += f"{guielem.name}.config(variable={guielem.name + '_var'})\n"               

        #Cambio coger codigo de elementos para luego----------------
        if guielem.class_ in special_containers:
            #print("Cogiendo codigo especial!!!!!")
            if guielem.class_ =="ttk.Notebook":
                for cnt in guielem.elements:
                    #print(cnt)
                    special_containers_code.append(f"{guielem.name}.add({cnt[1]['name']},text='{cnt[1]['text']}')")
                    #print(f"CODIGOS ESPECIALES AQUI: {special_containers_code}")
        #-----------------------------------------------------------
        #print("self.template aqui: " + self.template)
        noconsels=[]
        for item in nocelems:
            #Metodos especiales para sizers, tabs y demas containers
            if item in ["grid","pack","place"]:
                self.template += guielem.name + "." + item + "(" + nocelems[item] + ")\n"
            else:
                noconsels.append(guielem.name + "." + "configure(" + item + "='" + nocelems[item] + "')")
        #Procesar elementos de elements si hay que hacerlo!!!
        #PENDIENTE!!!!!!!!!! 
        self.template+= "\n".join(noconsels) + "\n"
        return self.template


RENDERERS = {
    "tkinter" : [tkinterRenderer(),tkinterEventRenderer(),tkinterMenuRenderer()],
    "wx" : [PyWxRenderer(),PyWxEventRenderer(),PyWxMenuRenderer()]
}

def addRenderer(name : str,renderer,event_renderer,menu_renderer) -> NoReturn:
    '''
    DocString
    '''
    #Comprobar que el tipo es correcto
    assert isinstance(renderer,GUIElementRendererBase)
    assert isinstance(event_renderer,EventRendererBase)
    assert isinstance(menu_renderer,MenuRendererBase)
    RENDERERS[name] = [renderer,event_renderer,menu_renderer]

def renderAppDescriptor(xmlstr : str,lang : str,tofile : bool = False):
    '''
    DocString
    '''
    global special_containers,special_containers_code
    assert lang in RENDERERS
    #Coger renderers registrados segun lang
    renderer,evt_renderer,menu_renderer = RENDERERS[lang]
    codes=[]
    #Coger nombre de la aplicacion
    appname=xpath(xmlstr,".//application[@name]")[0].attrib["name"]
    #print(appname)
    #Cpger lenguaje de la aplicacion
    applang=xpath(xmlstr,".//application[@lang]")[0].attrib["lang"]
    #Coger titulo si esta definido
    apptitle=xpath(xmlstr,".//application[@title]")[0].attrib["title"]
    #Coger menu si esta definido
    appicon=xpath(xmlstr,".//application[@icon]")[0].attrib["icon"]
    #Coger menu si esta definido
    appmenu=xpath(xmlstr,".//application[@menu]")[0].attrib["menu"]
    #coger codigo de inicio si lo hay
    initcode=xpath(xmlstr,".//application/initCode[@href]")
    if initcode[0].attrib["href"]!="" :
        codes.append(readf(initcode[0].attrib["href"]))

    #Menus (nuevo)---------------------------------------------
    menubars = xpath(xmlstr,".//application/menus/menubar")
    menuitems = xpath(xmlstr,".//application/menus/menuitem")
    codes.append(menu_renderer.render([menubars,menuitems]))
    #----------------------------------------------------------

    #renderizar los widgets
    widget_table={}
    widgets= xpath(xmlstr,".//application/widgets/widget")
    print(widgets)
    els = None
    props = None
    cls = None
    name = None
    ps = None
    guiel = None
    for w in widgets:
        #print(w.attrib)
        name= w.attrib["name"]
        cls=w.attrib["class"]
        ps={}
        props= xpath(w,".//properties/property")
        for p in props:
            for k in p.attrib:
                ps[k]=p.attrib[k]
        els= xpath(w,".//elements/element")
        els= [[ widget_table.get(el.attrib["name"],None),el.attrib] for el in els] if els!=[] else []
        #pprint.pprint(els)
        guiel = GUIElement(cls,name,els,ps)
        widget_table[name]=guiel
        #print(guiel)
        codes.append(guiel.render(renderer,False))
        #print(f"CODIGOS ESPECIALES: {special_containers_code}")
    #pprint.pprint(codes)

    #Nuevo: Gestion de eventos
    events = xpath(xmlstr,"//application/events/event")
    #print(f"Events: {events}")
    #Todo event DEBE tener como atributos name, for y code
    codes.append(evt_renderer.render(events))

    #Coger codigo postWidgets si lo hay
    postwidgetscode= xpath(xmlstr,".//application/postCode[@href]")
    if postwidgetscode[0].attrib["href"]!="" :
        codes.append(readf(postwidgetscode[0].attrib["href"]))

    #Meter el codigo de los special_containers si lo hay----------------
    codes += special_containers_code
    #--------------------------------------------------------------------

    #print(appname)
    #print(applang)
    #pprint.pprint(flat(codes))
    #print("\n".join(flat(codes)))
    #Asignar menu principal si esta definido
    if appmenu not in [None,""]:
        appmenu = f"root.config(menu={appmenu})"
    else:
        appmenu=""
    #Asignar titulo si esta definido
    if apptitle not in [None,""]:
        apptitle = f"root.title('{apptitle}')"
    else:
        apptitle=""
    #Asignar icono si esta definido
    if appicon not in [None,""]:
        #Proceder segun sea ico o no:
        ext = appicon.split('.')[-1]
        if ext != 'ico':
            appicon = f"root.iconphoto(False, PhotoImage(file='{appicon}'))"
        else:
            appicon = f"root.wm_iconbitmap('{appicon}')"        
    else:
        appicon=""

    rendered = [appname,applang,appmenu,apptitle,appicon,"\n".join(flat(codes))]

    #Guardar a archivo si se especifica
    if tofile == True:
        tpl = getTemplate(lang)
        with open(appname + ".py","w") as f:
            f.write(tpl.format(rendered[2],rendered[5],rendered[3],rendered[4]))
            f.close()

    return rendered