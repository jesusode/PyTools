import sys
import os
from pila import *
import collections

HAS_PIL=1
HAS_TIX=1

#Excepcion si la plataforma es Java
if 'java' in sys.platform:
    raise Exception('Error: el modulo mini_tkbasic solo esta disponible para plataformas no Java')

#Aplicaciones Tkinter---------------
import tkinter.messagebox
import tkinter.colorchooser
import tkinter.filedialog
import tkinter.font
import tkinter
import tkinter.scrolledtext #ScrolledText nativo Tkinter
try:
    import tkinter.tix
except:
    HAS_TIX=0

#En darwin no encuentra el Tix
if 'darwin' in sys.platform:
    HAS_TIX=0

import tkinter.ttk
import ttkmultilistbox
import tkmultilistbox
import tkprogressbar
#import TreeWidget
import calendar
import ttkcalendar
import fontselect
try:
    import Image as PILImage
    import ImageTk as PILImageTk
except:
    HAS_PIL=0
import tscrolledframe
import spread
import time
import re
import copy

#Clases de utilidad para evitar el Tix en MacOs y Linux
class ScrollableListbox(tkinter.Listbox):
    def __init__(self, master, *arg, **key):
        self.frame = tkinter.Frame(master)
        self.yscroll = tkinter.Scrollbar(self.frame, orient='vertical')
        tkinter.Listbox.__init__(self, self.frame, yscrollcommand=self.yscroll.set, *arg, **key)
        self.yscroll['command'] = self.yview
    def grid(self, *arg, **key):
        self.frame.grid(*arg, **key)
        tkinter.Listbox.grid(self, row=0, column=0, sticky='NSEW')
        self.yscroll.grid(row=0, column=1, sticky='NS')


#Funcion de utilidad para saber si disponemos o no de los widgets Tix
def haveTix():
    return HAS_TIX

#Instancia de aplicacion global(cambiado para Minimal)-------------
__TK_APP__=None
CODES={} #??
#-----------------------------------------------------------------
 
_showform=0
_dictvalues={}
_alive_forms=Pila()
_mix_dict={}
_label_list=[]
_labels={}
_values={}
_widgets={}
_checkboxes={}
_progresses={}
_calendars={}
_regexps={}
_options={}
_top=None
_toplevel=None
_toplevelf=None
_main_menu=None
_date_var=None
_top_is_extern=0
_mainframe=None
_last_rowcount=0
_types=['text','textbox','textshow','password','regexp','combo','richtextbox',
        'list','label','labelimg','number','date','file','files','dir','dirs','font','color',
        'colors','spread','table','button','buttonimg','tree','progress','check','canvas',
        'multilist','progress2']
_entry=None
_rw=None
_cl=None
_w=0
_h=0
_x=0
_y=0
_imgbtitle=''
_imgsclicked=[]
#_formstack=Pila()

#print ttk.Style().theme_names()

_image=None
zoomlevel=1
rectangles=[]
canvas=None
canvas_item=None
#-----------------------------------------------------
#          Creacion de applets Tkinter
#-----------------------------------------------------


# Version: 0.7
# Author: Miguel Martinez Lopez
class DraggableWindow(object):

    def __init__(self, disable_draggingd =False, release_command = None):
        if disable_draggingd == False:
            self.bind('<Button-1>', self.initiate_motion)
            self.bind('<ButtonRelease-1>', self.release_dragging)

        self.release_command = release_command


    def initiate_motion(self, event) :
        mouse_x, mouse_y = self.winfo_pointerxy()

        self.deltaX = mouse_x - self.winfo_x()
        self.deltaY = mouse_y - self.winfo_y()

        self.bind('<Motion>', self.drag_window)


    def drag_window (self, event) :
        mouse_x, mouse_y = self.winfo_pointerxy()

        new_x = mouse_x - self.deltaX
        new_y = mouse_y - self.deltaY

        if new_x < 0 :
            new_x = 0

        if new_y < 0 :
            new_y = 0

        self.wm_geometry("+%s+%s" % (new_x, new_y))

    def release_dragging(self, event):
        self.unbind('<Motion>')

        if self.release_command != None :
            self.release_command()

    def disable_dragging(self) :
        self.unbind('<Button-1>')
        self.unbind('<ButtonRelease-1>')
        self.unbind('<Motion>')

    def enable_dragging(self):
        self.bind('<Button-1>', self.initiate_motion)
        self.bind('<ButtonRelease-1>', self.release_dragging)


#Hacked with permission :)
class Floating(tkinter.Toplevel, DraggableWindow):
    def __init__(self, parent,method="pack"):
        self.method=method
        tkinter.Toplevel.__init__(self, parent)
        DraggableWindow.__init__(self)
        self.overrideredirect(True)
    def addLabel(self,**kw):
        l=tkinter.Label(self,**kw)
        if self.method=='pack':
           l.pack()
        else:
           l.grid()
    def addTextarea(self,**kw):
        l=tkinter.Text(self,**kw)
        if self.method=='pack':
           l.pack()
        else:
           l.grid()
    def addText(self,**kw):
        l=tkinter.Entry(self,**kw)
        if self.method=='pack':
           l.pack()
        else:
           l.grid()
    def addButton(self,**kw):
        b=tkinter.Button(self,**kw)
        if self.method=='pack':
           b.pack()
        else:
           b.grid()



class Check(object):
    checkbox=None
    var=None


class TkRectangle(object):
    
    def __init__(self,name,x1,y1,x2,y2):
        #print 'Creado rectangulo con %s' %str((x1,y1,x2,y2))
        self.name=name
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        if self.x1>self.x2:
            t=self.x2
            self.x2=self.x1
            self.x1=t
        if self.y1>self.y2:
            t=self.y2
            self.y2=self.y1
            self.y2=t

    def getName(self):
        return self.name
            
    def inRect(self,x,y):
        if x>=self.x1 and x<=self.x2 and y>=self.y1 and y<=self.y2:
            return 1
        else:
            return 0

class TkScrolledCanvas:
    def __init__(self, master, **opts):
        if 'yscrollincrement' not in opts:
            opts['yscrollincrement'] = 17
        self.master = master
        self.frame = tkinter.ttk.Frame(master)
        self.current_coords=[]
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.canvas = tkinter.tix.Canvas(self.frame, **opts)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar = tkinter.tix.Scrollbar(self.frame, name="vbar")
        self.vbar.grid(row=0, column=1, sticky="nse")
        self.hbar = tkinter.tix.Scrollbar(self.frame, name="hbar", orient="horizontal")
        self.hbar.grid(row=1, column=0, sticky="ews")
        self.canvas['yscrollcommand'] = self.vbar.set
        self.vbar['command'] = self.canvas.yview
        self.canvas['xscrollcommand'] = self.hbar.set
        self.hbar['command'] = self.canvas.xview
        self.canvas.bind("<Key-Prior>", self.page_up)
        self.canvas.bind("<Key-Next>", self.page_down)
        self.canvas.bind("<Key-Up>", self.unit_up)
        self.canvas.bind("<Key-Down>", self.unit_down)
        self.canvas.bind("<Key-Left>", self.unit_left)
        self.canvas.bind("<Key-Right>", self.unit_right)        
        #if isinstance(master, Toplevel) or isinstance(master, Tk):
        self.canvas.focus_set()
    def page_up(self, event):
        self.canvas.yview_scroll(-1, "page")
        return "break"
    def page_down(self, event):
        self.canvas.yview_scroll(1, "page")
        return "break"
    def unit_up(self, event):
        self.canvas.yview_scroll(-1, "unit")
        return "break"
    def unit_down(self, event):
        self.canvas.yview_scroll(1, "unit")
        return "break"
    def unit_left(self, event):
        self.canvas.xview_scroll(-1, "unit")
        return "break"
    def unit_right(self, event):
        self.canvas.xview_scroll(1, "unit")
        return "break"

class DraggableCanvas(TkScrolledCanvas):
    def __init__(self, master, **opts):
        TkScrolledCanvas.__init__(self,master,**opts)
        self.lastx=0
        self.lasty=0
        self.current=None


    def createItem(self,klass,**options):
        if klass=='rectangle':
            item=self.canvas.create_rectangle(50, 25, 150, 75, fill="blue",tag='draggable')
            self.canvas.tag_bind(item,'<Button-1>',self._mouseclick)
            self.canvas.tag_bind(item,'<B1-Motion>',self._mousemove)
        else:
            pass

    def _mouseclick(self,event):
        self.current=self.canvas.find_closest(self.lastx,self.lasty)[0]
        self.lastx=self.canvas.canvasx(event.x)
        self.lasty=self.canvas.canvasy(event.y)        

    def _mousemove(self,event):
        #self.canvas.move(self.current,self.lastx-self.canvas.canvasx(event.x),self.lasty-self.canvas.canvasy(event.y))
        self.canvas.move(self.current,self.canvas.canvasx(event.x)-self.lastx,self.canvas.canvasy(event.y)-self.lasty)
        #Ahora las del evento son las ultimas
        self.lastx=self.canvas.canvasx(event.x)
        self.lasty=self.canvas.canvasy(event.y)
        

def messageBox(*args): #tkMessageBox    
    icons=['info','warning','error','question']
    title=args[0]
    msg=args[1]
    top=None
    if __TK_APP__==None:
        top=None
        if HAS_TIX:
            top=tkinter.tix.Tk()
        else:
            top=tkinter.Tk()
        top.withdraw()
        top.wm_iconbitmap('icono.ico')
        
    options={
        'ok': tkinter.messagebox.OK,
        'okcancel': tkinter.messagebox.OKCANCEL,
        'yesno': tkinter.messagebox.YESNO,
        'yesnocancel': tkinter.messagebox.YESNOCANCEL,
        'abortretryignore': tkinter.messagebox.ABORTRETRYIGNORE,
        'retrycancel': tkinter.messagebox.RETRYCANCEL
        }
    t=tkinter.messagebox.OK
    if  args[2] in options:
        t=options[args[2]]
    icon='info'
    if len(args)==4 and args[3] in icons:
        icon=args[3]
    retval=None
    if icon=='info':
        retval=tkinter.messagebox.showinfo(title,msg,type=t)
    elif icon=='warning':
        retval=tkinter.messagebox.showwarning(title,msg,type=t)
    elif icon=='error':
        retval=tkinter.messagebox.showerror(title,msg,type=t)
    elif icon=='question':
        retval=tkinter.messagebox.askquestion(title,msg,type=t)
    if top and top.winfo_children()==[]:
        top.quit()
    return retval


def getTkColor(*args):   
    top=None
    if __TK_APP__==None:
        top=None
        if HAS_TIX:
            top=tkinter.tix.Tk()
        else:
            top=tkinter.Tk()
        top.withdraw()
        top.wm_iconbitmap('icono.ico')
    color=tkinter.colorchooser.askcolor(title=args[0])
    if top and top.winfo_children()==[]:
        top.quit()    
    if color!=(None,None):
        r,g,b=color[0]
        return'#%02X%02X%02X'%(int(r),int(g),int(b))
    else:
        return None

def getTkFile(*args):   
    top=None
    if __TK_APP__==None:
        top=None
        if HAS_TIX:
            top=tkinter.tix.Tk()
        else:
            top=tkinter.Tk()
        top.withdraw()
        top.wm_iconbitmap('icono.ico')    
    file=None
    if args[1] not in ['open','save']:
        raise Exception('Error: el modo debe ser "open" o "save"')
    if args[1]=='save':
        file=tkinter.filedialog.asksaveasfilename(title=args[0])
    else:
        file=tkinter.filedialog.askopenfilename(title=args[0])
    if top and top.winfo_children()==[]:
        top.quit()            
    if file:
        return file
    else:
        return None
'''
Opciones a incorporar a estas funciones
options['initialdir'] = 'C:\\'
options['mustexist'] = False
options['parent'] = root
options['defaultextension'] = '.txt'
options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
'''

#Parche para convertir multiples archivos en una lista (no lo hace el Tkinter)
def fixlist(filenames):
    #do nothing if already a python list
    if isinstance(filenames,list): return filenames
    #http://docs.python.org/library/re.html
    #the re should match: {text and white space in brackets} AND anynonwhitespacetokens
    #*? is a non-greedy match for any character sequence
    #\S is non white space
    #split filenames string up into a proper python list
    result = re.findall("{.*?}|\S+",filenames)
    #remove any {} characters from the start and end of the file names
    result = [ re.sub("^{|}$","",i) for i in result ]
    return result

def getTkFiles(*args):
    top=None
    if __TK_APP__==None:
        top=None
        if HAS_TIX:
            top=tkinter.tix.Tk()
        else:
            top=tkinter.Tk()
        top.withdraw()
        top.wm_iconbitmap('icono.ico')        
    files=[]
    files=tkinter.filedialog.askopenfilename(title=args[0],multiple=True)
    if top and top.winfo_children()==[]:
        top.quit()    
    if files:
        if 'win32' in sys.platform:
            return fixlist(files)
        else:
            return list(files)
    else:
        return None
    

def getTkDir(*args):
    top=None
    if __TK_APP__==None:
        top=None
        if HAS_TIX:
            top=tkinter.tix.Tk()
        else:
            top=tkinter.Tk()
        top.withdraw()
        top.wm_iconbitmap('icono.ico')    
    dir=tkinter.filedialog.askdirectory(title=args[0])
    if top and top.winfo_children()==[]:
        top.quit()     
    if file:
        return dir
    else:
        return None     

def getTk():
    global _top
    return _top

def getToplevel():
    global _toplevelf
    return _toplevelf

def getMainFrame():
    global _mainframe
    return _mainframe

def getCheckStatus(checklabel):
    return _checkboxes[checklabel].get()

def quit():
    _exitForms()

def formBox(*args): #Deberia aceptar tb una configuracion con un JSON
    '''
    Contruye una plaicación Tkinter a partir de los parámetros que se le pasan.
    @param appopts : diccionario de configuración.
    @param labs : Lista de nombres para los widgets.
    @param labels : Diccionario de nombres-widgets .
    @param values : Diccionario de nombres-valores iniciales para los widgets.
    @param cancellable : Flag que determina si tiene o no botón de cancelar.
    @param noclose : Flag que determina si se puede cerrar o no el formulario.
    @param manulabels : Lista de nombres para los menús si los hay.
    @param menucode : Diccionario nombre-función para los menús.
    '''
    global __TK_APP__,HAS_PIL,HAS_TIX,_showform,_top,_dictvalues,_labels,_values,_label_list,_widgets,_toplevelf,_regexps,_checkboxes,_progresses,_alive_forms,_mix_dict,_main_menu,_popup_menu,_calendars,_options,_mainframe
    global _last_rowcount
    appopts=args[0]
    if not 'name' in appopts:
        raise Exception('Error: el diccionario de configuracion debe tener un campo "name"')
    appname=appopts['name']#ESTE CAMPO ES OBLIGATORIO
    style=appopts.get('style','default')
    title=appopts.get('title','Minimal tkinter App')
    icon=appopts.get('icon','icono.ico')
    w=appopts.get('width',300)
    h=appopts.get('height',300)
    x=appopts.get('x',50)
    y=appopts.get('y',50)
    sizer=appopts.get('sizer','grid')
    if sizer not in ['grid','pack']:
        sizer='grid'
    #Cambio para aceptar un popupmenu
    popmenu=appopts.get('popupmenu','')
    resize=appopts.get('resize',1)
    geom='%dx%d+%d+%d'%(w+5,h+44,x,y)   
    noclose=0
    if len(args)>=5:
        noclose=int(args[5])     
    if noclose!=0:
        geom='%dx%d+%d+%d'%(w,h,x,y)
    nolabels=appopts.get('nolabels',0)
    #FALTA POR CONTROLAR MINWIDTH,MINHEIGHT
    init_code=appopts.get('oninit',None)
    if init_code !=None:
            init_code=init_code
    if __TK_APP__==None:
        if _top==None:
            #print 'creando nuevo toplevel'
            _top=None
            if HAS_TIX:
                _top=tkinter.tix.Tk()
            else:
                _top=tkinter.Tk()
            _top.withdraw()
            if not 'linux' in sys.platform: #En linux no va
                _top.wm_iconbitmap(icon)
            
            __TK_APP__=_top
            _showform=1
               
    _label_list=args[1]   
    _labels=args[2]
    _values=args[3]

    _toplevelf=None
    if HAS_TIX:
        _toplevelf=tkinter.tix.Toplevel(_top)
    else:
        _toplevelf=tkinter.Toplevel(_top)
    _toplevelf.title(title)
    if not 'linux' in sys.platform:
        _toplevelf.wm_iconbitmap(icon)
    _toplevelf.geometry(geom)
    bodyframe=tkinter.ttk.Frame(_toplevelf)
    #Ocupar todo el espacio disponible
    bodyframe.pack(side='top', expand='yes', fill='both')
    #bodyframe.grid(column=0,row=0,sticky='NSEW')
    if resize==0:
        _toplevelf.resizable(0,0)
    _toplevelf.protocol("WM_DELETE_WINDOW", _delete_window)
    cancellable=1
    if len(args)>=5:
        cancellable=int(args[4])
    mainframe2=None
    #mainframe=None
    if noclose==1:
        mainframe2=tkinter.ttk.Frame(bodyframe) #(_toplevelf)
        _mainframe=mainframe2
    else:
        mainframe2=tscrolledframe.TScrolledFrame(bodyframe,usehullsize=True,width=w,height=h)
        _mainframe=mainframe2.frame()
    #Control del estilo--------------------------------
    if not style in  list(tkinter.ttk.Style().theme_names()):
        style='default'
    tkinter.ttk.Style().theme_use(style)
    #--------------------------------------------------
    if cancellable==0:
        mainframe2.grid(column=0,row=0,sticky='NSEW',padx=5,pady=5)
    else:
        #print 'ocupo 2 columnas'
        mainframe2.grid(column=0,row=0,sticky='NSEW',padx=5,pady=5,columnspan=2)
    #mainframe=mainframe2.frame()
    
    #Gestionar menu si lo hay--------------------------------------------------------
    if len(args)==8:
        mlabels=None
        menus=None

        mlabels=args[6]
        menus=args[7]
        #print menus        
        mbar=tkinter.Menu(_toplevelf,tearoff=0)
        for item in mlabels: #CAMBIO: para submenus se espera una lista con [[labels],[codes]]
            menu=tkinter.Menu(mbar,tearoff=0)
            if type(menus[item])==type([]):
                lbls=menus[item][0]
                codes=menus[item][1]
                submenu=tkinter.Menu(menu, tearoff=0)
                for i in range(len(lbls)):
                    if ' ' in lbls[i]:
                        raise Exception('Error: no se aceptan espacios en los nombres de menus')
                    if lbls[i]=='-':
                        submenu.add_separator()
                    else:
                        submenu.add_command(label=lbls[i].replace('_',' '),command=lambda c=codes[i]:c())
                mbar.add_cascade(label=item,menu=submenu)
            else:
                code=menus[item]
                menu.add_command(label=item,command=lambda c=code:c())
                mbar.add_cascade(label=item,menu=menu)
        _toplevelf.configure(menu=mbar)
        _main_menu=mbar
        geom='%dx%d+%d+%d'%(w+5,h+70,x,y)
        _toplevelf.geometry(geom)
    #Asignar manejadores para eventos del formulario(esto deberia ser configurable)
    _toplevelf.bind('<Button-1>',_OnFormClick)
    _toplevelf.bind('<Button-3>',_OnFormRClick)
    _toplevelf.bind("<Double-Button-1>",_OnFormDblClick)
    #--------------------------------------------------------------------------------
        
    #Crear las filas label-widget
    rowcont=0
    images_refs=[]#Hay que guardar una referencia a las imagenes o se pierden!!!!!!
    for label in _label_list: #Considerar separadores!!!!!
        #print 'Trabajando label: %s' % label 
        rowcont+=buildWidget(label,_mainframe,sizer,nolabels,rowcont)
    #Establecer _last_rowcount a la ultima fila creada
    _last_rowcount=rowcont
    #-------------------------------------------------
    if noclose==0:    
        ok=tkinter.ttk.Button(bodyframe,text='OK',command=_getFormValues)
        ok.grid(column=0,row=1,sticky='NSEW',padx=5,pady=5)
        if cancellable==1:
            cancel=tkinter.ttk.Button(bodyframe,text='Cancel',command=_cancelForm)
            cancel.grid(column=1,row=1,sticky='NSEW',padx=5,pady=5)
                
    #if _showform:
    #print 'Entrando por showform=1'

    #Ejecutar el codigo inicial si se ha definido---------------
    if init_code:
        init_code()
    #-----------------------------------------------------------
    #print 'showform al arrancar: %s' %_showform
    #print _top.winfo_children()
    #print 'toplevelf:%s' %_toplevelf
    _alive_forms.push([_toplevelf,_labels])
    #print '_alive_forms: %s' %_alive_forms.getList()
    #Ponerlo en lo alto de la pila Z
    #_toplevelf.wm_attributes('-topmost',1)
    _showform+=1
    if _showform==2:
        _top.mainloop()
    else:
        #print 'entrando por espera del formulario emergente??'
        _toplevelf.focus_set()
        _toplevelf.grab_set()
        _top.wait_window(_toplevelf)
    #print 'retonnando!'
    #print 'dictvalues: %s' % _dictvalues
    return _dictvalues


def addFormItem(fname,itemlabel,itemvalues,sizer,nolabels): #Anyade dinamicamente un widget
    global __TK_APP__,HAS_PIL,HAS_TIX,_showform,_top,_dictvalues,_labels,_values,_label_list,_widgets,_toplevelf,_regexps,_checkboxes,_progresses,_alive_forms,_mix_dict,_main_menu,_popup_menu,_calendars,_options,_mainframe
    global _last_rowcount
    if not fname : raise Exception('Error: el formulario "%s" no existe'%fname)
    _labels.update(itemlabel)
    _values.update(itemvalues)
    buildWidget(list(itemlabel.keys())[0],_mainframe,sizer,nolabels,_last_rowcount)

def deleteFormWidget(fname,name):
    global __TK_APP__,HAS_PIL,HAS_TIX,_showform,_top,_dictvalues,_labels,_values,_label_list,_widgets,_toplevelf,_regexps,_checkboxes,_progresses,_alive_forms,_mix_dict,_main_menu,_popup_menu,_calendars,_options,_mainframe
    global _last_rowcount
    if not fname : raise Exception('Error: el formulario "%s" no existe'%fname)
    w=_widgets[name]
    del _labels[name]
    del _widgets[name]
    w.destroy()

def buildWidget(label,mainframe,sizer,nolabels,rowcont):
        global __TK_APP__,HAS_PIL,HAS_TIX,_showform,_top,_dictvalues,_labels,_values,_label_list,_widgets,_toplevelf,_regexps,_checkboxes,_progresses,_alive_forms,_mix_dict,_main_menu,_popup_menu,_calendars,_options
        #print 'Trabajando label: %s' % label
        #Se requieren valores unicos para label-------------------------------------------------------------
        if _label_list.count(label)>1:
            raise Exception('Error: "%s" ya se ha usado. Los nombres de etiquetas no pueden repetirse'%label)
        #---------------------------------------------------------------------------------------------------
        if _labels[label]=='separator':
            widget=tkinter.ttk.Separator(mainframe)
            if sizer=='pack':
                widget.pack(side='top', expand='yes', fill='both',padx=5,pady=5)
            else:
                widget.grid(column=0,row=rowcont,columnspan=2,sticky='NSEW',padx=5,pady=5)
            return 1
        elif _labels[label]=='label':
            if label in _values:
                #Comprobar si es una imagen
                widget=None
                if os.path.exists(_values[label]):
                    if HAS_PIL==0: return 0
                    photo=PILImage.open(_values[label])
                    img=PILImageTk.PhotoImage(photo)                    
                    widget=tkinter.ttk.Label(mainframe,image=img)
                else:
                    widget=tkinter.ttk.Label(mainframe,text=_values[label])
                _widgets[label]=widget
                if sizer=='pack':
                    widget.pack(side='top', expand='yes', fill='both',padx=5,pady=5)
                else:                
                    widget.grid(column=0,row=rowcont,columnspan=2,sticky='NSEW',padx=5,pady=5)
                #print _widgets
                return 1


            if label+'_popupmenu' in _values:
                #construir menu y asignarlo al widget
                if label + '_menulabels' not in _values:
                    raise Exception('Error: Si se define un menu contextual para un widget debe definirse tambien una entrada "menulabels"')
                if label + '_menus' not in _values:
                    raise Exception('Error: Si se define un menu contextual para un widget debe definirse tambien una entrada "menus"')
                mlbs=_values[label + '_menulabels']
                mnus=_values[label + '_menus']
                widget.bind('<Button-3>', buildPopupFunction(mlbs,mnus))
            return 0

        elif _labels[label]=='labelimg':
            if label in _values:
                if HAS_PIL==0: return 0
                #Espera una cadena con formato: texto|imgfile|estilo(compound)
                #valores posibles para compound:none,text,image,top,bottom,left,right
                widget=None
                txt,imgf,comp=_values[label].split('|')
                photo=PILImage.open(imgf)
                img=PILImageTk.PhotoImage(photo)
                images_refs.append(img)
                widget=tkinter.ttk.Label(mainframe,image=img,text=txt,compound=comp)
                _widgets[label]=widget
                if sizer=='pack':
                    widget.pack(side='top', expand='yes', fill='both',padx=5,pady=5)
                else:                
                    widget.grid(column=0,row=rowcont,columnspan=2,sticky='NSEW',padx=5,pady=5)
                return 1
            
        if nolabels==0:
            lbl=tkinter.ttk.Label(mainframe,text=label)
            if sizer=='pack':
                lbl.pack(side='top', expand='yes', fill='both',padx=5,pady=5)
            else:            
                lbl.grid(column=0,row=rowcont,sticky='NSEW',padx=5,pady=5)
        widget=None
        if _labels[label] not in _types:
            raise Exception('Error: El tipo "%s" no se admite para un widget en un _formBox'%label)
        
        if _labels[label]=='text':
            widget=tkinter.ttk.Entry(mainframe)
            _widgets[label]=widget
            if label in _values:
                widget.insert('end',_values[label])
        elif _labels[label]=='regexp':
            widget=tkinter.ttk.Entry(mainframe)
            #Controlar que lo metido cumple la expresion regular
            widget.bind('<FocusOut>',_checkRegexp)
            _widgets[label]=widget
            if label in _values:
                _regexps[widget]=_values[label]                
        elif _labels[label]=='number':
            initval=0
            if label in _values:
                initval=int(_values[label])
            widget=tkinter.Spinbox(mainframe,from_=initval,to=sys.maxsize)
            _widgets[label]=widget
        elif _labels[label]=='password':
            widget=tkinter.ttk.Entry(mainframe,show='*')
            _widgets[label]=widget
        elif _labels[label]=='date': 
            #widget=ttk.Entry(mainframe, state='disabled')
            _calendars[label]=tkinter.StringVar()
            widget=dlgTkCalendar.tkCalendar(mainframe, time.localtime()[0], time.localtime()[1], time.localtime()[2], _calendars[label] )
            _widgets[label]=widget
            #widget.insert('end','click here')
            #widget.configure(state='disabled')
            #widget.bind('<Button-1>',_showCalendar)
        elif _labels[label]=='textbox':  #Tix dependiente!
            if HAS_TIX:
                widget=tkinter.tix.ScrolledText(mainframe,height=80,scrollbar='both')
                _widgets[label]=widget
                if label in _values:
                    widget.text.config(wrap=tkinter.WORD)
                    widget.text.insert('end',_values[label])
            else:
                widget=tkinter.scrolledtext.ScrolledText(mainframe,height=5)
                _widgets[label]=widget
                if label in _values:
                    widget.config(wrap=tkinter.WORD)
                    widget.insert('end',_values[label])                
        elif _labels[label]=='textshow':
            if not HAS_TIX:
                return 0
            widget=tkinter.tix.ScrolledText(mainframe,height=80,state='readonly',scrollbar='none')
            _widgets[label]=widget
            if label in _values:
                widget.text.config(wrap=tkinter.WORD)
                widget.text.insert('end',_values[label])                
        elif _labels[label]=='combo':
            if label in _values:
                values=_values[label]
                widget=tkinter.ttk.Combobox(mainframe,values=values,state='normal')
                _widgets[label]=widget
            widget.current(0)
        elif _labels[label]=='list':
            if label in _values:
                if not HAS_TIX:
                    values=_values[label]
                    widget=ScrollableListbox(mainframe)
                    _widgets[label]=widget
                    widget.configure(background='white',selectmode='multiple')
                    for item in values:
                        widget.insert('end',item)
                else:
                    values=_values[label]
                    widget=tkinter.tix.ScrolledListBox(mainframe,height=60)
                    _widgets[label]=widget
                    widget.listbox.configure(background='white',activestyle='dotbox',selectmode='multiple')
                    for item in values:
                        widget.listbox.insert('end',item)
                                           
        elif _labels[label]=='font':
            widget=fontselect.FontSelect(mainframe)
            _widgets[label]=widget
        elif _labels[label]=='colors': 
            widget=tkinter.tix.ScrolledListBox(mainframe,height=60)
            _widgets[label]=widget
            if HAS_TIX:
                widget.listbox.configure(state='disabled')
                widget.listbox.configure(background='white')
                widget.listbox.bind('<Button-1>',_showColor)
            else:
                widget.configure(state='disabled')
                widget.configure(background='white')
                widget.bind('<Button-1>',_showColor)
                
        elif _labels[label]=='color': 
            widget=tkinter.ttk.Entry(mainframe, state='readonly')
            _widgets[label]=widget
            widget.insert('end','choose a color...')
            widget.configure(state='disabled')
            widget.bind('<Button-1>',_showColor)             
        elif _labels[label]=='files': 
            widget=tkinter.tix.ScrolledListBox(mainframe,height=60)
            _widgets[label]=widget
            if HAS_TIX:
                widget.listbox.configure(state='disabled')
                widget.listbox.configure(background='white')
                widget.listbox.bind('<Button-1>',_showFiles)
            else:
                widget.configure(state='disabled')
                widget.configure(background='white')
                widget.bind('<Button-1>',_showColor)
                
        elif _labels[label]=='file': 
            widget=tkinter.ttk.Entry(mainframe, state='readonly')
            _widgets[label]=widget
            widget.insert('end','choose a file...')
            widget.configure(state='disabled')
            widget.bind('<Button-1>',_showFile)            
        elif _labels[label]=='dirs': 
            widget=tkinter.tix.ScrolledListBox(mainframe,height=60)
            _widgets[label]=widget
            if HAS_TIX:
                widget.listbox.configure(state='disabled')
                widget.listbox.configure(background='white')
                widget.listbox.bind('<Button-1>',_showDir)
            else:
                widget.configure(state='disabled')
                widget.configure(background='white')
                widget.bind('<Button-1>',_showColor)
                
            #
        elif _labels[label]=='dir': 
            widget=tkinter.ttk.Entry(mainframe, state='readonly')
            _widgets[label]=widget
            widget.insert('end','choose a directory...')
            widget.configure(state='disabled')
            widget.bind('<Button-1>',_showDir)             
        elif _labels[label]=='table':
            if label in _values:
                editable=0
                if int(_values[label])==1:
                    editable=1
                #Tienen que estar definidos label_columns y label_values
                label_list= _values[label+'_columns']
                data_list=_values[label+'_values']
                widget=ttkmultilistbox.TtkMultiListbox(mainframe,label_list,data_list,editable,None)
                _widgets[label]=widget
        elif _labels[label]=='multilist':
            if label in _values:
                editable=0
                if int(_values[label])==1:
                    editable=1
                #Tienen que estar definidos label_columns y label_values
                label_list= _values[label+'_columns']
                label_list=[[el,20] for el in label_list] #Esto deberia ser configurable
                data_list=_values[label+'_values']
                widget=tkmultilistbox.MultiListbox(mainframe,label_list)
                for item in data_list:
                    widget.insert('end',item)
                _widgets[label]=widget                
        elif _labels[label]=='tree': #?????
            if label in _values:
                #Tienen que estar definidos label_values
                data_list=_values[label+'_values']
                #El primer elemento de la lista no puede ser una lista
                if type(data_list[0])==type([]):
                    raise Exception('Error: el primer elemento de un tree no puede ser una lista')
                widget=tkinter.ttk.Treeview(mainframe,show="tree headings")
                tree= widget.insert('','end',text='|')
                _populateTree(widget,tree,data_list)                
                _widgets[label]=widget                
        elif _labels[label]=='button':
                #Tienen que estar definidos button_text y el codigo
                if label not in _values:
                    raise Exception('Error: Debe definirse un codigo a ejecutar para el boton "%s"'%label)
                bcode= _values[label]
                btext=label
                if label + '_text' in _values:
                    btext=_values[label+'_text']                
                widget=tkinter.ttk.Button(mainframe,text=btext,command=lambda c=bcode:bcode())
                _widgets[label]=widget
        elif _labels[label]=='buttonimg':
                if HAS_PIL==0: return 0
                #Tienen que estar definidos button_text y el codigo
                if label not in _values:
                    raise Exception('Error: Debe definirse un codigo a ejecutar para el boton "%s"'%label)
                bcode= _values[label]
                btext=label
                bimage='mind_small.jpg'
                bstyle='left'
                if label + '_text' in _values:
                    btext=_values[label+'_text']
                if label + '_image' in _values:
                    bimage=_values[label+'_image']
                if label + '_style' in _values:
                    bstyle=_values[label+'_style']
                photo=PILImage.open(bimage)
                img=PILImageTk.PhotoImage(photo)
                images_refs.append(img)                    
                widget=tkinter.ttk.Button(mainframe,text=btext,image=img,compound=bstyle,command=lambda c=bcode:bcode())
                _widgets[label]=widget                
        elif _labels[label]=='check':
                v=tkinter.IntVar()
                widget=tkinter.ttk.Checkbutton(mainframe, variable=v)
                _checkboxes[label]=v
                _widgets[label]=widget          
        elif _labels[label]=='progress':
                length=200
                v=tkinter.IntVar()
                widget=tkinter.ttk.Progressbar(mainframe,orient ="horizontal",length = length, mode ="determinate",maximum=100,variable=v)
                if label in _values:
                    widget.value=int(_values[label])
                _progresses[label]=v
                widget.step(int(_values[label]))
                _widgets[label]=widget
        elif _labels[label]=='progress2':
                length=50
                widget=tkprogressbar.Meter(mainframe,fillcolor='blue')
                if label in _values:
                    widget.set(float(_values[label]/100.0))
                _widgets[label]=widget                
        elif _labels[label]=='canvas':
                cv=DraggableCanvas(mainframe)
                widget=cv.frame
                _widgets[label]=cv.canvas
                cv.createItem('rectangle')
        #print 'gridding widget: %s' % widget
        if sizer=='pack':
            widget.pack(side='top', expand='yes', fill='both',padx=5,pady=5)
        else: #grid()               
            if nolabels==1:
                widget.grid(column=0,row=rowcont,columnspan=2,sticky='NSEW',padx=5,pady=5) #NSEW
            else:
                widget.grid(column=1,row=rowcont,sticky='NSEW',padx=5,pady=5) #NSEW?
        #Asignar popupmenu si se ha definido(entrada en data_dict "label_popupmenu"
        #Si es asi, debe haber una entrada 'label_menulabels' y otra 'label_menus' eb data_dict
        if label+'_popupmenu' in _values:
            #construir menu y asignarlo al widget
            if label + '_menulabels' not in _values:
                raise Exception('Error: Si se define un menu contextual para un widget debe definirse tambien una entrada "menulabels"')
            if label + '_menus' not in _values:
                raise Exception('Error: Si se define un menu contextual para un widget debe definirse tambien una entrada "menus"')
            mlbs=_values[label + '_menulabels']
            mnus=_values[label + '_menus']
            if isinstance(widget,tkinter.tix.ScrolledText):
                widget.text.bind('<Button-3>', buildPopupFunction(mlbs,mnus)) 
            widget.bind('<Button-3>', buildPopupFunction(mlbs,mnus)) 
        return 1


def buildPopupFunction(_mlabels,_menus):
    global _toplevelf
    mlabels=None
    menus=None
    mlabels=_mlabels
    menus=_menus  
    def popupFunction(event):
        menu.tk_popup(event.x_root+10, event.y_root+10,0)
        return 'break'
    menu=tkinter.Menu(_toplevelf,tearoff=0)
    for item in mlabels:
        #menu=Tkinter.Menu(mbar,tearoff=0)
        if item=='-':
            menu.add_separator()
        elif item in menus and type(menus[item])==type([]): #????????
            codes=menus[item]
            submenu=tkinter.Menu(menu, tearoff=0)
            for code in codes:
                if code=='-':
                    submenu.add_separator()
                else:
                    submenu.add_command(label=code.replace('_',' '),command=lambda c=code:code())
            #mbar.add_cascade(label=item,menu=submenu)
        else:
            code=menus[item]
            menu.add_command(label=item,command=lambda c=code:code())
            #mbar.add_cascade(label=item,menu=menu)
    return popupFunction
      


def _populateTree(widget,tree,elems): #En pruebas!!
    #print 'Valor de tree: %s'%tree
    if tree=='':
        tree= widget.insert(tree,'end',text='|')
    for item in elems:
        #print 'Valor de item: %s' % item
        if type(item)==type([]):#recursivo
            tree2= widget.insert(tree,'end',text='|')
            #print 'Creando nodo nuevo'
            for el in item:
               #print 'valor de el: %s'%el
               if type(el)==type([]):
                   #print 'llamada recursiva'
                   tree3= widget.insert(tree2,'end',text='|')
                   _populateTree(widget,tree3,el)
               else:
                   #print 'insertando en nodo interior %s -> %s' %(tree2,el)
                   widget.insert(tree2,'end',text=el)
        else:  #trivial
           #print 'insertando en nodo %s -> %s' %(tree,item)
           widget.insert(tree,'end',text=item)


            
def _getFormValues2():
    global _top,_dictvalues,_labels,_values,_widgets,_toplevelf,_checkboxes,_progresses ,_alive_forms,_calendars   
    _dictvalues={}
    #print _labels
    #print _widgets
    for label in _labels:
        if label in _widgets:
            if _labels[label] in ['text','password','number','combo','regexp','file','dir','color']:
                _dictvalues[label]=_widgets[label].get()                
            elif _labels[label] in ['textbox','richtextbox','textshow']:
                if HAS_TIX:
                    _dictvalues[label]=_widgets[label].text.get('0.0','end')
                else:
                    _dictvalues[label]=_widgets[label].get('0.0','end')
            elif _labels[label]=='list':
                if HAS_TIX:
                    _dictvalues[label]=[_widgets[label].listbox.get(el) for el in _widgets[label].listbox.curselection()]
                else:
                    _dictvalues[label]=[_widgets[label].get(el) for el in _widgets[label].curselection()]
            elif _labels[label] in ['colors','files','dirs']:
                if HAS_TIX:
                    _dictvalues[label]=list(_widgets[label].listbox.get(0,'end'))
                else:
                    _dictvalues[label]=list(_widgets[label].get(0,'end'))
            elif _labels[label]=='spread':
                _dictvalues[label]=_widgets[label].getCellValues()
            elif _labels[label]=='table':
                _dictvalues[label]=_widgets[label].lists
            elif _labels[label]=='multilist':
                _dictvalues[label]=[list(el) for el in _widgets[label].get(0,'end')]
            elif _labels[label]=='check':
                _dictvalues[label]=_checkboxes[label].get()
            elif _labels[label]=='date':
                _dictvalues[label]=_calendars[label].get()                
            elif _labels[label]=='progress':
                _dictvalues[label]=_progresses[label].get()
            elif _labels[label]=='progress2':
                _dictvalues[label]=_widgets[label].get()[0]                
            elif _labels[label]=='font':
                f=_widgets[label].get()#.getName()
                if f is None: #Hay que usar is o falla por un problema con el __eq__ de tkFont
                    _dictvalues[label]=None
                else:
                    _dictvalues[label]=f.actual()
    return _dictvalues


def _getFormValues():
    #print 'en getformvalues()'
    #print '_alive_forms: %s' % _alive_forms.getList()
    global _top,_dictvalues,_labels,_toplevelf,_alive_forms
    #print '_toplevelf: %s' % str(_toplevelf)
    _dictvalues={}
    _dictvalues=_getFormValues2()
    if _toplevelf:
        _toplevelf.destroy()
    if not _alive_forms.isEmpty():
        #print 'haciendo pop'
        t,l=_alive_forms.pop()
        if _alive_forms.isEmpty():
            _alive_forms.push([t,l])
        #print '(t,l): %s-->%s:'%(t,l)
        #print _toplevel==t
        if _toplevelf==t and not _alive_forms.isEmpty():
            _toplevelf,_labels=_alive_forms.pop()
            if  _alive_forms.isEmpty():
               _alive_forms.push([_toplevelf,_labels]) 
    #print '_alive_forms ahora: %s' % _alive_forms.getList()
    #print [_top]
    #print 'Ventanas activas: %s' % _top.winfo_children()
    #Salir de la aplicacion si ya no hay mas ventanas activas
    if _top.winfo_children()==[]:
        _top.quit()
    return _dictvalues
    #Resetear globales


def _cancelForm():#corregir??
    global _top,_dictvalues,_toplevelf,_labels,_alive_forms
    _dictvalues={}
    #Cancelar entrada
    if not _alive_forms.isEmpty():
        #print 'sacando el ultimo'
        _alive_forms.pop()
    #print 'pila en cancel: %s' %_alive_forms.getList()
    #print '_toplevelf en cancel: %s' %_toplevelf
    if _toplevelf:
        _toplevelf.destroy()
    #Recuperar valores anteriores
    if not _alive_forms.isEmpty():
        #print 'restableciendo el anterior'
        _toplevelf,_labels=_alive_forms.pop()
        _alive_forms.push([_toplevelf,_labels])
        #print 'pila ahora en cancel: %s' %_alive_forms.getList()
        #print '(toplevelf,labels): %s-->%s:'%(_toplevelf,_labels)
    #Salir de la aplicacion si ya no hay mas ventanas activas
    if _top.winfo_children()==[]:
        _top.quit()        
    return None


def _exitForms():
    global _top
    if _top.winfo_exists():
        _dictvalues=_getFormValues2()
        #print 'pila: %s' %_alive_forms.getList()
        #_top.destroy()
        _top.quit() 
    return None


def _delete_window():
    pass
    
    
def _OnFormClick(event):
    global _toplevelf
    #print 'Se ha hecho click en el formulario!!!'
    return None
    
def _OnFormDblClick(event):
    global _toplevelf
    #print 'Se ha hecho doble click en el formulario!!!'
    
def _OnFormRClick(event):
    global _toplevelf,_main_menu
    #print 'Se ha hecho click derecho en el formulario!!!'
    if _main_menu:
        _main_menu.post(event.x_root,event.y_root)
    
def _showColors(event):
    global _toplevelf
    event.widget.configure(state='normal')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)
    color=tkinter.colorchooser.askcolor(title='Color')
    _toplevelf.wm_attributes('-disabled',0)
    if color!=(None,None):
        r,g,b=color[0]
        event.widget.insert('end','#%02X%02X%02X'%(r,g,b))
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0)

def _showColor(event):
    global _toplevelf
    event.widget.configure(state='normal')
    event.widget.delete(0,'end')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)
    color=tkinter.colorchooser.askcolor(title='Choose a color')
    if color!=(None,None):
        r,g,b=color[0]
        event.widget.insert('end','#%02X%02X%02X'%(r,g,b))
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0)
    event.widget.configure(state='disabled')    
    

def _showFiles(event):
    global _toplevelf
    event.widget.configure(state='normal')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)
    file=tkinter.filedialog.askopenfilename(title='Choose a file')
    if file:
        event.widget.insert('end',file)
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0)
    event.widget.configure(state='disabled') 
        
    
def _showFile(event):
    global _toplevelf
    event.widget.configure(state='normal')
    event.widget.delete(0,'end')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)
    file=tkinter.filedialog.askopenfilename(title='Choose a file')
    if file:
        event.widget.insert('end',file)
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0)
    event.widget.configure(state='disabled') 
        

def _showDirs(event):
    global _toplevelf
    event.widget.configure(state='normal')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)
    _dir=tkinter.filedialog.askdirectory()
    if _dir:
        event.widget.insert('end',_dir)
    _toplevelf.wm_attributes('-disabled',0)
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0)
    event.widget.configure(state='disabled') 
        

def _showDir(event):
    global _toplevelf
    event.widget.configure(state='normal')
    event.widget.delete(0,'end')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)
    file=tkinter.filedialog.askdirectory(title='Choose a directory')
    if file:
        event.widget.insert('end',file)
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0)  
    event.widget.configure(state='disabled') 
        

def _showCalendar(event):
    global _toplevelf,_date_var,_top
    widget=event.widget
    widget.configure(state='normal')
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',1)  
    date=tkinter.StringVar()    
    cal=dlgTkCalendar.tkCalendar(_top, time.localtime()[0], time.localtime()[1], time.localtime()[2], date,update=widget )
    _toplevelf.wm_attributes('-disabled',0)
    if 'win32' in sys.platform:
        _toplevelf.wm_attributes('-disabled',0) 
    event.widget.configure(state='disabled') 
    
def _checkRegexp(event):
    try:
        global _regexps
        widget=event.widget
        text=widget.get()
        pat=_regexps[widget]
        m=re.match(pat,text)
        if m!=None and m.start()==0 and m.end()==len(text):
            #print 'The text match'#?
            pass
        else:
            #print 'No matches no'
            widget.delete(0,'end')
            tkinter.messagebox.showerror('Wrong input!','Validation error: the text "%s" doesn\'t match the expression "%s"' %(text,pat))
            widget.focus_set()
    except:
        pass


def getFormItemValue(*args):
    global _widgets,_labels,_progresses,_checkboxes
    form=args[0]
    if not form:
        raise Exception('Error: El formulario "%s" no esta definido'%args[0])
    item=_widgets.get(args[1],None)
    if not item:
        raise Exception('Error: El item de formulario "%s" no esta definido'%args[1])
    #Proceder segun elemento(asumimos que vale get en todos para probar
    if _labels[args[1]] in ['text','password','number','combo','date','regexp','file','dir','color']:
        return item.get()
    elif _labels[args[1]]=="check":
        return _checkboxes[args[1]].get()
    elif _labels[args[1]]=='textbox':
        if HAS_TIX:
            return item.text.get('0.0','end')
        else:
            return item.get('0.0','end')
    elif _labels[args[1]]=='list':
        if HAS_TIX:
            return [item.listbox.get(el) for el in item.listbox.curselection()] 
        else:
            return [item.get(el) for el in item.curselection()] 
    elif _labels[args[1]] in ['colors','files','dirs']:
        if HAS_TIX:
             return list(item.listbox.get(0,'end'))
        else:
             return list(item.get(0,'end'))
    elif _labels[args[1]]=='spread':
        return item.getCellValues()
    elif _labels[args[1]]=='table':
        return item.lists
    elif _labels[args[1]]=='progress':
        return _progresses[args[1]].get()
    elif _labels[args[1]]=='progress2':
        return item.get()[0]   
    elif _labels[args[1]]=='font':
        f=item.getName()
        if f==None:
            return None
        else:
            return f

def setFormItemValue(*args):
    global _widgets,_labels
    form=args[0]
    if not form:
        raise Exception('Error: El formulario "%s" no esta definido'%args[0])

    item=_widgets.get(args[1],None)
    if not item:
        raise Exception('Error: El item de formulario "%s" no esta definido'%args[1])
    
    #Proceder segun elemento
    if _labels[args[1]] in ['text','password','number','combo','date','regexp','file','dir','color']:
        item.delete(0,'end')
        item.insert(0,args[2])
    elif _labels[args[1]]=='textbox':
      if HAS_TIX:
        item.text.delete('0.0','end')
        item.text.insert('0.0',args[2])
      else:
        item.delete('0.0','end')
        item.insert('0.0',args[2])
    elif _labels[args[1]]=='progress':
        item.step(int(args[2]))
        item.value+=int(args[2])
        if item.value>=100:
            item.value=0
    elif _labels[args[1]]=='progress2':
        v=float(item.get()[0]) + float(args[2])
        if v>=1:
            v=0
        item.set(v)
           
    elif _labels[args[1]]=='font':
        font=tkinter.font.Font(**args[2])
        item['font']=font
           
    elif _labels[args[1]] in ['list','colors','files','dirs']:
        #Value debe ser una lista
        if HAS_TIX:
            item.listbox.delete(0,'end')
            for el in args[2]:
                item.listbox.insert('end',el)
        else:
            item.delete(0,'end')
            for el in args[2]:
                item.insert('end',el)
        

def getFormItem(*args):
    global _widgets,_labels
    form=args[0]
    if not form:
        raise Exception('Error: El formulario "%s" no esta definido'%args[0])
    #Se deben poder pasar nombres de subwidgets ('item1@text)
    item=None
    is_multilist=0
    if '@' in args[1]:
        pref,suf=args[1].split('@')
        item=getattr(_widgets[pref],suf)
    elif _labels[args[1]]=='multilist':
        is_multilist=1
        item=_widgets.get(args[1],None)
    else:
        item=_widgets.get(args[1],None)
    if item == None:
        raise Exception('Error: El formulario "%s" no contiene el item "%s"'%(args[0],args[1]))
    return item


def callFormItem(*args):
    global _widgets,_labels
    form=args[0]
    if not form:
        raise Exception('Error: El formulario "%s" no esta definido'%args[0])
    #Se deben poder pasar nombres de subwidgets ('item1@text)
    item=None
    is_multilist=0
    if '@' in args[1]:
        pref,suf=args[1].split('@')
        item=getattr(_widgets[pref],suf)
    elif _labels[args[1]]=='multilist':
        is_multilist=1
        item=_widgets.get(args[1],None)
    else:
        item=_widgets.get(args[1],None)
    if is_multilist==0 and not hasattr(item,args[2]):
        raise Exception('Error: El item de formulario "%s" no tiene definida la funcion o propiedad "%s"'%(args[1],args[2]))
    func=getattr(item,args[2])
    _args=None
    resul=None
    
    _args=args[3]
     
    if type(_args)==type([]):    
        if isinstance(func, collections.Callable):
            resul=func(*_args)
            #Convertir tuplas a listas
            if type(resul)==type((1,)):
                resul=list(resul)
        else:
            setattr(item,func,*_args)
    else:
        if isinstance(func, collections.Callable):
            resul=func(**_args)
            #Convertir tuplas a listas
            if type(resul)==type((1,)):
                resul=list(resul)            
        else:
            setattr(item,func,**_args)
            resul=None   
    #Proceder segun elemento(asumimos que vale get en todos para probar
    return resul


def setFormItemFont(*args):
    global _widgets,_labels
    form=args[0]
    #print 'form: %s' % form
    if not form:
        raise Exception('Error: El formulario "%s" no esta definido'%args[0])
    #Se deben poder pasar nombres de subwidgets ('item1@text)
    item=None
    if '@' in args[1]:
        pref,suf=args[1].split('@')
        item=getattr(_widgets[pref],suf)
    else:
        item=_widgets.get(args[1],None)
    #print 'valor de item: %s' % item
    props=args[2]
    font=tkinter.font.Font(**props)
    item.configure(font=font)
    return 1

