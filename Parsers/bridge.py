#!Python
import sys
import re
import itertools
import shutil
import pprint

#Añadir las carpetas builders y modules al path----------------------
sys.path.append("./builders")
sys.path.append("./modules")
#-------------------------------------------------------------------

#Cambio para configuracion en archivo aparte-------------
from bridge_config import *
#Fin cambio----------------------------------------------

#Plantillas para los lenguajes a generar------
from templates import *
#---------------------------------------------

#Soporte JavaScript----
import js_builder
#----------------------

#Soporte C++-----------
import cpp_builder
#----------------------

#Soporte C-----------
import c_builder
#----------------------

#Soporte Java----------
import java_builder
#----------------------

#Soporte CSharp--------
import csharp_builder
#----------------------

#Soporte Python------------
import python_builder
#----------------------

#Configuracion global de bridge
#accesible por todos los builders
import bridge_config
#----------------------

#Cambio para preprocesador externo-------------------
from preprocessor import *
#----------------------------------------------------



#Lenguajes permitidos--------------------------------
old_langs=['python','csharp','java','js','c++','cython','c','fsharp']
#allowed_langs=['python','csharp','java','js','c++','cython','c','swig','fsharp','groovy']
allowed_langs= old_langs[:]
#----------------------------------------------------

#---------------------------------------------------
#---Tabla de traductores a lenguajes soportados-----
#---------------------------------------------------

LANG_TABLE={
    'python': python_builder,
    'cython' : None,
    'js': js_builder,
    'csharp' : csharp_builder,
    'c' : c_builder,
    'c++' : cpp_builder,
    'java' : java_builder
}

#Funcion para importar un modulo dinamicamente en el actual
def importModule(name):
    setattr(sys.modules[__name__],name,__import__(name))
    return sys.modules[name]

#Esto permite un sencillo sistema de plugins para lenguajes
#Es necesario que cada funcion de la gramatica se mapee en el builder
#para que funcione
def addLanguage(name):
    global allowed_langs,LANG_TABLE
    if name in allowed_langs:
        raise Exception("Error: el lenguaje '%s' ya existe")
    allowed_langs.append(name)
    #Hay que importar el builder!!!!!
    LANG_TABLE[name]= importModule(name + '_builder')
    #print(LANG_TABLE)

#---------------------------------------------------
#---------------------------------------------------
#---------------------------------------------------

#Para medir eficiencia------------------------------------------------
if not 'time' in sys.modules: 
    time=__import__('time')
else:
    time=sys.modules['time']
#print 'Comenzando carga de modulos: %s' % time.strftime('%H:%M:%S')
#---------------------------------------------------------------------
from ply import lex
from ply import yacc
import ply #Vigilar esto!!!

if not 'os' in sys.modules:
    os=__import__('os')
else:
    os=sys.modules['os']
if not 'os.path' in sys.modules:
    os.path=__import__('os.path')
else:
    os.path=sys.modules['os.path']
if not 'math' in sys.modules:
    math=__import__('math')
else:
    math=sys.modules['math']
if not 're' in sys.modules:
    re=__import__('re')
else:
    re=sys.modules['re']
if not 'random' in sys.modules:
    random=__import__('random')
else:
    random=sys.modules['random']

#Esto para que no molesten los warnings------------------------
if not 'warnings' in sys.modules:
    warnings=__import__('warnings')
else:
    warnings=sys.modules['warnings']
sys.modules['warnings'].filterwarnings('ignore')
#--------------------------------------------------------------
#print 'Antes de llegar a las que dependen del sistema operativo: %s' % time.strftime('%H:%M:%S')

if not 'stlex2' in sys.modules:
    stlex2=__import__('stlex2')
else:
    stlex2=sys.modules['stlex2']

#Flag global para permitir crear generadores en JavaScript(necesitan marcar la funcion como function*)-------
JS_GENERATOR=0
#------------------------------------------------------------------------------------------------------------

#Variables globales controlables por directivas de linea de comandos
active_lang='python' #Por defecto traducimos a python
create_exe=0 #Crear o no un ejecutable
print_script=0 #Imprimir codigo generado en consola
exec_script=0 #Ejecutar script despues de generarlo
exe_props='' #Archivo de propiedades para generar el ejecutable
outputfile='bridge_output.py' #Nombre del archivo de salida
outputdir='.' #Directorio de salida donde se pondra el archivo generado y/o el ejecutable
extra_files=[] #Archivos de usuario a copiar el el dir del ejecutable
#Archivos de los que depende para compilar con py2exe
__dependencies=['bridge.py','RegExp.py',
                'RegExp2.py','stlex2.py','templates.py',
                'xmltodict.py','lex.py','yacc.py','js_builder.py','csharp_builder.py','cpp_builder.py',
                'java_builder.py','pila.py','prologpy.py',
                'matrix.py','lispy.py']
__dependencies=['RegExp.py','RegExp2.py','xmltodict.py','pila.py','prologpy.py','matrix.py','lispy.py']
prolog_mode=0
minimal_mode=0
repl_mode=0
scheme_mode=0 
clojure_mode=0 
lisp_mode=0 
tk_mode=0

#Flag que controla que se importe el interprete (bridge)
embed_ply=0
#-------------------------------------------------------------------

#Flag que controla el encoding para el codigo fuente(solo Python)
_encoding="utf-8"
#-------------------------------------------------------------------

#Flag para mostrar el resultado del preprocesador-------------------
_show_preproc=False
#-------------------------------------------------------------------

#Flag para mostrar cadenas de documentacion-------------------
_show_doc=False
#-------------------------------------------------------------------

#Flag para no usar preprocesador (mas rapido)----------------------
_use_preproc=True
#-------------------------------------------------------------------

#Global que contiene el programa en ejecucion
__program=''

#Bases de datos soportadas------------------------------------
allowed_databases=['ado','mysql']
#-------------------------------------------------------------

#Flags para traduccion condicional----------------------------
__flags=[]
#-------------------------------------------------------------

#Flags para no poner los runtimes al traducir si los hay----------------------------
__noruntime = False #Con directiva --noruntime
#-----------------------------------------------------------------------------------

#Mensaje de error para p_error----------------------------
ERROR_MSG = ''
#-------------------------------------------------------------

#Nombre generico para listas,arrays y dicts
l_name='list'
l_counter=0
a_counter=0
a_name='array'
d_counter=0
d_name='dict'
o_counter=0
o_name='objdict'
t_name='text'
t_counter=0
u_name='update'
u_counter=0
re_name='regex'
re_counter=0
s_name='split'
s_counter=0
m_name='match'
m_counter=0
aux_name='aux'
aux_counter=0
x_name='xml'
x_counter=0
pl_name='prolog'
pl_counter=0
db_name='dbase'
db_counter=0
f_name='file'
f_counter=0
srv_name='servlet'
srv_counter=0
cnd_name='cond'
cnd_counter=0
g_name='groupby'
g_counter=0
rule_name='rule'
rule_counter=0
let_name='let'
let_counter=0
lazy_name='lazy'
lazy_counter=0
deconstruct_name='deconstruct'
deconstruct_counter=0
tr_name='thread'
tr_counter=0
pr_name='process'
pr_counter=0
enum_counter=0
let_counter=0


#Flag para permitir usar el parser en el codigo generado----
__reflected=0
#-----------------------------------------------------------

#Contador de funciones para python
fun_counter=0

#cadena auxiliar para definiciones auxiliares
aux_string=''

#tabla de sustituciones y contador de sustituciones
table_sust={}
cont_sus=0

#Lista de modulos importados--------
imported=[]
#-----------------------------------

#Lista de clases definidas----------
__classes=[]
#Clases a comprobar en runtime
__pyBases=[]
#-----------------------------------


#Funciones globales definidas----------
__functions=[]
#--------------------------------------

#Directorio base para los environs-----------
__ENVIRON_PATH='.'
__current_namespace=''
__namespaces=[]
#--------------------------------------------
#Archivo que esta siendo procesado-----------
__program_file=''
#--------------------------------------------

# Get the token map from the lexer.  This is required.
tokens=stlex2.tokens

#Lista de urls a manejar
urls=[]

#Tabla de identificadores definidos-tipo
defined_ids={}

#Tabla de funciones de sistema
system_func={}

#Tabla de funciones definidas por el usuario
user_funcs={}

#Cadena que contiene las importaciones nativas a realizar
nativestring=''

#Cadena que contiene las importaciones a realizar
importstring=''

#Cadena que contiene las funciones definidas
funcstring=''

#Cadena de salida para compilar
outstring=""

#Cadena para las clases de usuario en C# y Java
class_string=''

#Cadena con flags de compilacion condicional para C#
csflags=''

#Cadena con flags de compilacion condicional para C++
cppflags=''

#Flag para generar o no un archivo .h C++ (opcion -h de linea de comandos)
cppheader=0

#Cadena con flags de compilacion condicional para C
cflags=''

#Flag para generar o no un archivo .h C (opcion -h de linea de comandos)
cheader=0

#Cadena que contiene las definiciones de funciones anonimas para C
anonymstring=''

#Contador de funciones anonimas para C
c_anonym_counter=0

#Cadena con flags de compilacion condicional para F#
fsflags=''

#Flag para saber si estamos dentro de bucles
INSIDE_LOOP=0

#Flag para saber si un return_st es correcto
INSIDE_FUNC=0

#Flag para saber si estamos definiendo clases
__inclass=0

#Flag para saber si estamos definiendo una funcion lambda
__inlambda=0

#OBSOLETO!!!!
#Para python con soporte de tipos--------------------------------
py_checks=[] #Comprobaciones para funciones y funciones miembro
py_typeclass=[] #Comprobaciones para variables miembro
py_statictypeclass=[]#Comprobaciones para miembros estaticos
_ftype=''#Tipo del campo si se ha definido
#----------------------------------------------------------------

#Clases selladas
__sealed=[]

#Path de busqueda para los imports-------------------------------
MINIMAL_PATH=['.']
#----------------------------------------------------------------

#OBSOLETO!!
#Flag que indica que estamos dentro de un servidor web----------
IN_WEBSERVER=0
#----------------------------------------------------------------

#Flag que indica que estamos procesando pass_st----------
PASS_ST=False
#----------------------------------------------------------------

#Cadena para estilos(obsoleto)---------------------------------------------
STYLES_STRING = ''
_just_styles=False
#----------------------------------------------------------------

def _indent(code):
    indent='    '
    val=''
    for it in code.split('\n'):
        val+=indent + it + '\n'
    #val+='\n'
    return val


def _split(s,tk):
    return s.split(tk)

def _strip(s,it=None):
    if it==None:
        return s.strip()
    else:
        return s.strip(it)

def _join(lst,el):
    return lst.join(el)

def _replace(s,old,new):
    return s.replace(old,new)

def _find(s,el,begin=0,end=None):
    if end==None:
        end=len(s)
    return s.find(el,begin,end)

def _sublist(s,b,e=None):
    if e:
        return s[b:e]
    else:
        return s[b:]

def _index(el,lst):
    return lst.index(el)

#Soporte de operadores python-------------------------------------------
py_opers={
    '+' : '__add__',
    '-' : '__sub__',
    '*' : '__mul__',
    '/' : '__truediv__',
    '=' : '__equal__',
    '!=' : '__ne__',
    '<' : '__lt__',
    '>' : '__gt__',
    '<=' : '__le__',
    '>=' : '__ge__',
    '()' : '__call__'
}
#-----------------------------------------------------------------


#Asignar opciones de linea de comando si las hay-----------
#Disponibles:
# -o <file> Nombre del archivo de salida
# -l <lang> Lenguaje al que se traducira
# -e Crear ejecutable
# -r Ejecutar despues de traducir
# -p Imprimir en consola el codigo generado
#-----------------------------------------------------------
def setCommandLineOptions(opts):
    global create_exe,print_script,exec_script,outputfile,active_lang,extra_files,outputdir,outstring,active_lang,prolog_mode,minimal_mode,scheme_mode,clojure_mode,lisp_mode,repl_mode,__flags,allowed_langs,csflags,cppflags,MINIMAL_PATH,cppheader,embed_ply,_encoding,_show_preproc,_use_preproc,cheader,cflags,_show_docs,_just_styles,defines,defines_list
    #print 'opts: %s' % opts
    #Nuevo: instalar lenguajes nuevos------------------------------------------------------
    while '--install' in opts:
        i=opts.index('--install')
        addLanguage(opts[i+1].strip())
        del opts[i]
        del opts[i]
    #--------------------------------------------------------------------------------------
    if '-e' in opts: #exe
        create_exe=1
        del opts[opts.index('-e')]
        bridge_config.config_table['-e']= 1
    if '--config' in opts: #archivo de propiedades para el ejecutable si se genera
        i=opts.index('--config')
        bridge_config.config_table['--config']=opts[i+1]
        del opts[i]
        del opts[i]
    if '-r' in opts: #run
        exec_script=1
        del opts[opts.index('-r')]
        bridge_config.config_table['-r']= 1
    if '-d' in opts: #dir de salida
        i=opts.index('-d')
        outputdir=opts[i+1]
        del opts[opts.index('-d')]
        bridge_config.config_table['-d']= 1
    if '-p' in opts: #debug print
        print_script=1
        del opts[opts.index('-p')]
        bridge_config.config_table['-p']=1
    if '-o' in opts: #output file
        i=opts.index('-o')
        outputfile=opts[i+1]
        del opts[i]
        del opts[i]
        bridge_config.config_table['-o']= outputfile
    if '-s' in opts: #self-reflective
        embed_ply=1
        del opts[opts.index('-s')]
        bridge_config.config_table['-s']= 1
    if '--encoding' in opts: #codec para codigo fuente
        i=opts.index('--encoding')
        _encoding=opts[i+1]
        del opts[i]
        del opts[i]
        bridge_config.config_table['--encoding']= _encoding
    if '--noruntime' in opts: #no usar codigo de runtime
        i=opts.index('--noruntime')
        __noruntime = True
        bridge_config.config_table['--noruntime']= True
        del opts[i]
    while '-i' in opts: #extra files
        i=opts.index('-i')
        if not '-i' in bridge_config.config_table:
            bridge_config.config_table['-i']= [opts[i+1]]
        else:
            bridge_config.config_table['-i'].append(opts[i+1])
        extra_files.append(opts[i+1])
        del opts[i]
        del opts[i]
    while '--flag' in opts: #opciones para trad. condic.
        i=opts.index('--flag')
        if opts[i+1] not in __flags and opts[i+1] not in allowed_langs:  __flags.append(opts[i+1])
        if not '--flag' in bridge_config.config_table:
            bridge_config.config_table['--flag']= [opts[i+1]]
        else:
            bridge_config.config_table['--flag'].append(opts[i+1])
        del opts[i]
        del opts[i]
        #meter los flags en defines y defines_list-----------------------
        for item in __flags:
            defines_list.append(item)
            defines[item] = PreProcMacro(item,'',[],False,False)
        #----------------------------------------------------------------
    while '--csflag' in opts: #opciones para trad. condic. en C#
        i=opts.index('--csflag')
        csflags+='#define ' + opts[i+1]
        if not '--csflag' in bridge_config.config_table:
            bridge_config.config_table['--csflag']= [opts[i+1]]
        else:
            bridge_config.config_table['--csflag'].append(opts[i+1])
        del opts[i]
        del opts[i]
    while '--cppflag' in opts: #opciones para trad. condic. en C++
        i=opts.index('--cppflag')
        cppflags+='#define ' + opts[i+1] + '\n'
        if not '--cppflag' in bridge_config.config_table:
            bridge_config.config_table['--cppflag']= [opts[i+1]]
        else:
            bridge_config.config_table['--cppflag'].append(opts[i+1])
        del opts[i]
        del opts[i]
    while '--cflag' in opts: #opciones para trad. condic. en C++
        i=opts.index('--cflag')
        cflags+='#define ' + opts[i+1]
        if not '--cflag' in bridge_config.config_table:
            bridge_config.config_table['--cflag']= [opts[i+1]]
        else:
            bridge_config.config_table['--cflag'].append(opts[i+1])
        del opts[i]
        del opts[i]
    while '--path' in opts: #Busqueda para imports
        i=opts.index('--path')
        if not opts[i+1] in MINIMAL_PATH:
            MINIMAL_PATH.append(opts[i+1])
        if not '--path' in bridge_config.config_table:
            bridge_config.config_table['--path']= [opts[i+1]]
        else:
            bridge_config.config_table['--path'].append(opts[i+1])
        del opts[i]
        del opts[i]
    if not '-l' in opts: #establecer flag de python
        __flags.append('python')
    if '-l' in opts: #language
        i=opts.index('-l')
        if opts[i+1] not in allowed_langs:
            raise Exception('Error: "%s" no es un lenguaje soportado'%opts[i+1])
        active_lang=opts[i+1]
        bridge_config.config_table['-l']= active_lang
        #Para c++ ponemos cpp pq c++ no es un identificador para bridge
        __flags.append(active_lang) if active_lang!="c++" else __flags.append("cpp")
        del opts[i]
        del opts[i]
    if '-h' in opts: #generar archivo .h
        if active_lang not in ['c++','c']: raise Exception('Error: solo se permite generar archivos de cabecera cuando el lenguaje activo es C o C++')
        if active_lang=='c++':
            cppheader=1
            bridge_config.config_table['-o']= cppheader
        else:
            cheader=1
            bridge_config.config_table['-o']= cheader
        del opts[opts.index('-h')]
    if '--tk' in opts: #incorporar Tkinter(para permitir _formbox)
        i=opts.index('--tk')
        tkpath='import mini_tkbasic\n'
        if active_lang=='python':
            outstring+=tkpath
            bridge_config.config_table['--tk']= 1
        del opts[opts.index('--tk')]
        #tk_mode=1
    if '--repl' in opts: #-repl arranca en modo repl minimal, prolog, hy, scheme o clojure
        i=opts.index('--repl')
        if active_lang!='python':
            raise Exception('Error: No se puede arancar en modo -repl si el lenguaje no es Python')
        del opts[opts.index('-repl')]
        bridge_config.config_table['--repl']= 1
        repl_mode=1
    #Comprobar que no haya opciones incompatibles
    if active_lang!='python' and create_exe==1:
        raise Exception('Error: Solo se pueden generar ejecutables cuando el lenguaje es Python')
    if exec_script==1 and active_lang!='python':
        raise Exception('Error: Solo se permite ejecutar el codigo generado cuando el lenguaje es Python')
    if '--pre' in opts: #Flag para mostrar salida del preprocesador
        i=opts.index('--pre')
        _show_preproc=True
        bridge_config.config_table['--pre']= 1
        del opts[i]
    if '--doc' in opts: #Flag para mostrar las cadenas de documentacion
        i=opts.index('--doc')
        _show_docs=True
        bridge_config.config_table['--doc']= 1
        del opts[i]
    if '--nopre' in opts: #Flag para no usar preprocesador (mas rapido)
        i=opts.index('--nopre')
        _use_preproc=False
        bridge_config.config_table['--nopre']= 1
        del opts[i]
    sys.argv=opts[:] #Ver que pasa con primer y segundo componenente y cuando es un exe!!!

def findInPath(name): #Tambien deberiamos admitir zips como posibles paths. Si
    global MINIMAL_PATH
    #print( 'MINIMAL_PATH: %s' %MINIMAL_PATH)
    exts=['.mini','.txt','.bridge','.zip']
    #print os.getcwd()
    for item in MINIMAL_PATH:
        if item=='.': item=''
        #Probar como archivo y como directorio
        for i in exts:
            #print 'buscando: %s' %repr(item + name + i )
            #print os.path.exists(item + name + i )
            if os.path.isdir(item):
                if os.path.exists(item + '/' + name + i):
                    return item + '/' + name + i
            if os.path.exists(item + name + i):
                return item + name + i
    return ''

#-----------------------------------------------------------------------------------
#Variable global para mapear las lineas del codigo con los archivos a los
#que corresponden, para corregir el efecto de los imports
PROG_LINES=[]
CUR_FILE=''
imported_files=[]

def guessFile(lineno):#Si
    global PROG_LINES,__program_file,imported_files
    cur_file = __program_file
    last_file=__program_file
    cont=1
    for line in PROG_LINES:
        #print('PROCESANDO LINE: %s'%line)
        #print('cont: %s'%cont)
        if line[0:6]=='#from ':
            last_file= cur_file
            cur_file=line[5:].strip()
            #print('cur_file cambiado a: %s'%cur_file)
        elif line[0:5]=='#end ':
            cur_file= last_file
            last_file=__program_file
            #print('cur_file cambiado a last_file: %s'%cur_file)
        if lineno==cont:
            return cur_file
        cont+=1
        

def preprocess(prog): #Cambiado para importacion multiple. REVISAR!!!!
    #Quitar comentarios
    #print(repr(prog))
    #print(prog)
    global imported,MINIMAL_PATH,__program_file,PROG_LINES,CUR_FILE
    callrec=False
    #exp="\n?(\s*imports\s*[a-zA-Z_0-9]+\s*?;)"
    exp="\n?\s*(imports\s*[a-zA-Z_0-9]+\s*?;)"
    strexp=r"[@|r|u|b]?\"\"\"[\s\S]*?\"\"\"|[@|r|u|b]?\"[^\"\\]*(?:\\.[^\"\\]*)*\""
    comexp=r'\#[^\n]*[\n]?|\#[^\r\n]*[\r\n]|/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
    results=[[x.group(1),x.start(1),x.end(1)] for x in sys.modules['re'].finditer(exp,prog,flags=0)]
    results=[y for y in results if y[0]!=None]
    strresults=[[x.start(),x.end()] for x in sys.modules['re'].finditer(strexp,prog,flags=0)]
    strresults=[y for y in strresults if y[0]!=None]
    comresults=[[x.start(),x.end()] for x in sys.modules['re'].finditer(comexp,prog,flags=0)]
    comresults=[y for y in comresults if y[0]!=None]
    #print('IMPORTS results: %s' % results)
    #print('STR results: %s' % strresults)
    #print('COM results: %s' % comresults)
    #Ahora cogemos solo los imports detectados que no esten dentro de un string o un comment
    tmp= []
    for item in results:#Esto falla si el import esta repetido????
        #print("probando item: %s"%[item[1],item[2]])
        instr=False
        incom=False
        for s in strresults:
            #print("Probando str: %s" % s)
            if item[1]>=s[0] and item[2]<=s[1]:
                instr=True
        for c in comresults:
            #print("Probando com: %s" % s)
            if item[1]>=c[0] and item[2]<=c[1]:
                incom=True
        if incom==False and instr==False:
            #print("METIENDO ITEM")
            tmp.append(item)
    results=tmp
    #print('IMPORTS VERDADEROS: %s' % results)
    if results==[]:
        return prog
    #Guardar los nombres de los archivos ya importados
    #Solo se puede procesar un item cada vez, porque cambia
    #la longitud de prog y hay que recalcular los indices
    elem=results[0]
    #print("PROCESANDO ITEM: %s"%elem)
    arch=''.join(elem[0].strip(";").split()[1:])
    #print("arch: %s" % arch)
    if arch!='' and arch in imported:
        prog=prog[:elem[1]] + "\n" + prog[elem[2]:]#Cambiar esto por StringIO
        #print "prog: " + prog
        #raise Exception("Parada temporal")
    else:
        #Sustituir la linea del import por el codigo del archivo
        #OJO: esto cambia la longitud y ya no valen los indices de la proxima sustitucion
        item=findInPath(arch)
        if item=='':
            raise Exception("Error en la importacion:\n\tEl modulo \"%s\" no existe en el path de bridge." % arch)
        #code=open(item).read()
        code=open(item).read()

        CUR_FILE=item

        prog= prog[:elem[1]] + '#from ' + CUR_FILE + '\n' + code + '\n#end ' + CUR_FILE + '\n' + prog[elem[2]:] #Cambiar esto por StringIO
        imported.append(arch)
        imported_files.append(item)
        #print('\n---PROG:\n %s\n---'%prog)
        #print ("prog: " + prog)
        #input("SIGUIENTE?")
        #raise Exception("Parada temporal")
    results=results[1:]
    #Si quedan imports por procesar,hacemos llamada recursiva
    if len(results)>0:
        return preprocess(prog)
    else: 
        results=[[x.group(1),x.start(1),x.end(1)] for x in sys.modules['re'].finditer(exp,prog,flags=0)]
        results=[y for y in results if y[0]!=None]
    #Si todavia hay imports por procesar despues de lo hecho, llamada recursiva
    if len(results)>0:
        return preprocess(prog)

    #Guardar las lineas del programa para control de errores--------------------------------
    PROG_LINES= prog.split('\n')
    #pprint.pprint(PROG_LINES)
    #---------------------------------------------------------------------------------------
    return prog


precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIV'),
    )


def p_program(t):#LANG: revisar las globales: la mitad ya no sirven!!!
    '''program : program_elems_list'''
    global outstring,py_template,py_template2,cs_template,js_template,importstring,funcstring
    global outputfile,outputdir,class_string,csflags,cppflags,__sealed, __noruntime
    global cppheader,embed_ply,__embed_ply,cflags,cheader,cppheader,anonymstring,c_template
    global fs_template,fsflags,_encoding,LANG_TABLE,active_lang,STYLES_STRING,_just_styles
    if t[1]==None: t[1]=''
    t[0]=t[1]
    outstring+=t[0]
    #print 'outstring despues: %s' % outstring + '\n-------------------------'
    t[0]=outstring
    #Hacer un define para cada flag
    template=''
    if active_lang=='python':
        template = LANG_TABLE[active_lang].process_program(t,__sealed) 
    elif active_lang=='cython':
        template=template.replace("%%__main_code__%%",outstring)#!!!!!!!!!!!!
    elif active_lang=='java':
        template = LANG_TABLE[active_lang].process_program(t,importstring)
    elif active_lang=='csharp':
        template = LANG_TABLE[active_lang].process_program(t,importstring,csflags,class_string,outputfile)
    elif active_lang=='c++':
        template = LANG_TABLE[active_lang].process_program(t,importstring,cppheader,cppflags)
    elif active_lang=='c':
        template = LANG_TABLE[active_lang].process_program(t,importstring,cflags,anonymstring,cheader)
    else:
        template = LANG_TABLE[active_lang].process_program(t,importstring)
    #escribirlo en un archivo
    #Asegurarse de que existe outputdir
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    #Cambio para opcion --styles: solo escribimos la cadena de estilos------------------------
    if _just_styles==True:
        template = STYLES_STRING
    #-----------------------------------------------------------------------------------------
    #print('Escribiendo en : %s' % outputfile)
    f=open(outputdir + '/' + outputfile,'w')
    f.write(template)
    f.close()
    t[0]=template
    class_string=''#?de verdad hay que resetearlo?
    outstring=''#?????????Esto se corrige para el run . Comprobar el resto!!!!!

def p_program_elems_list(t): #ok
    '''program_elems_list : program_elem program_elems_list
    | program_elem'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_program_elems_list(t)

def p_program_elem(t): #ok
    '''program_elem : order_list'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_program_elem(t)

def p_native(t): #LANG
    '''native : NATIVE generic
    | NATIVE generic STATIC
    | NATIVE generic FROM expr
    | NATIVE TIMES FROM expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_native(t)

def p_idchain(t): #ok
    '''idchain : idchain_item idchain_sep idchain
    | idchain_item'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_idchain(t)
    #print('t[0] en idchain: %s' % t[0])

#CAMBIO PARA USERDEF: EXPERIMENTAL!!!!
def p_idchain_sep(t): #ok
    '''idchain_sep : DOT
    | DOTDOT
    | USERDEF'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_idchain_sep(t)

def p_idchain_item(t): #ok
    '''idchain_item : ID'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_idchain_item(t)

def p_set_environ(t): #ok
    '''set_environ : cls_mod ENVIRON idchain'''
    global __current_namespace,active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_set_environ(t)
    __current_namespace=t[3]

def p_namespace(t):#ok
    '''namespace : set_environ order_list END idchain'''
    global py_template,__current_namespace,__namespaces,active_lang,class_string,LANG_TABLE
    curdir=__ENVIRON_PATH
    t[0]=LANG_TABLE[active_lang].process_namespace(t,curdir = curdir,py_template=py_template)
    #Poner en namespaces
    __namespaces.append(t[1])
    #Restablecer __current_namespace
    __current_namespace=''

def p_class_section(t):#ok
    '''class_section : begin_class_section class_list end_class_section
    | empty'''
    global __classes,__pyBases,active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_class_section(t,__classes=__classes,__pyBases=__pyBases)

def p_begin_class_section(t): #ok
    '''begin_class_section : BEGIN'''
    global __inclass,INSIDE_FUNC,active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_begin_class_section(t)
    #Poner a 1 el flag de funciones para permitir la definicion de funciones miembro
    INSIDE_FUNC=1
    __inclass=1

def p_end_class_section(t): #ok
    '''end_class_section : ENDSEC'''
    global __inclass,INSIDE_FUNC,__pyBases,active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_program_elem(t)
    #restablecer flag de funciones
    INSIDE_FUNC=0
    __inclass=0

#    | target_comment_st
def p_class_list(t):#ok??
    '''class_list : classtype classname class_or_interface base_list inner_class_list field_list member_list END class_list
    | classtype classname class_or_interface base_list inner_class_list field_list  member_list END'''
    global __classes,__pyBases,__current_namespace,active_lang,__sealed
    #Excepciones para structs-interfaces
    py_typeclass=[]#????????????
    t[0]=LANG_TABLE[active_lang].process_class_list(t,__classes=__classes,__pyBases=__pyBases,__current_namespace=__current_namespace,__sealed=__sealed)

def p_class_or_interface(t):#ok
    '''class_or_interface : friend_list EXTENDS
    | friend_list IMPLEMENTS'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_class_or_interface(t)

def p_friend_list(t):#ok
    '''friend_list : friend_st
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_friend_list(t)

def p_classname(t): #ok
    '''classname : annotation_list generic'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_classname(t)

def p_generics_defs(t):#ok
    '''generic_defs : GENERIC LPAREN generic_items RPAREN
    | GENERIC LPAREN NULL RPAREN'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_generic_defs(t)

def p_generic_items(t):#ok
    '''generic_items : generic_item
    | generic_item COMMA generic_items'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_generic_items(t)

def p_generic_item(t):#ok
    '''generic_item : generic
    | generic AS generic
    | generic AS generic EQUAL expr
    | generic EQUAL expr
    | fptr2
    | generic_defs
    | generic_defs generic_item'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_generic_item(t)

def p_classtype(t): #ok
    '''classtype : cls_mod CLASS
    | cls_mod STRUCT
    | cls_mod INTERFACE
    | cls_mod ARROBA INTERFACE
    | cls_mod UNION
    | cls_mod TRAIT
    | cls_mod generic
    | cls_mod CLASS generic_defs
    | cls_mod STRUCT generic_defs
    | cls_mod INTERFACE generic_defs
    | cls_mod UNION generic_defs
    | cls_mod TRAIT generic_defs
    | cls_mod generic generic_defs'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_classtype(t)

def p_cls_mod(t): #ok
    '''cls_mod : AMPERSAND id_space
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_cls_mod(t)

def p_id_space(t): #ok
    '''id_space : ids_elem
    | ids_elem id_space'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_id_space(t)

def p_ids_elem(t): #ok
    '''ids_elem : ID
    | ambit'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_ids_elem(t)

def p_ambit(t): #ok
    '''ambit : PUBLIC
    | PRIVATE
    | PROTECTED
    | STATIC
    | PUBLIC STATIC
    | PRIVATE STATIC
    | PROTECTED STATIC'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_ambit(t)

def p_base_list(t): #ok
    '''base_list : generic_list
    | OBJECT
    | OBJECT COMMA generic_list'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_base_list(t)

#Clases anidadas
def p_inner_class(t):#Vigilar target_comment_st!!
    '''inner_class : PIPE classtype classname class_or_interface base_list field_list member_list END PIPE
    | PIPE expr_list PIPE
    | target_comment_st
    | generic_block'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_inner_class(t)

def p_inner_class_list(t):#ok
    '''inner_class_list : inner_class
    | inner_class inner_class_list
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_inner_class_list(t)

#    | target_comment_st
def p_field_list(t): #ok
    '''field_list : field_item COLON ambit field_list 
    | field_item COLON ambit
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_field_list(t)

#    | target_comment_st
def p_field_item(t):#ok
    '''field_item : ID
    | ID opt_get opt_set
    | ID AS generic EQUAL expr SEMI 
    | ID AS generic opt_get opt_set
    | enum_st
    | fptr2
    | typedef_st
    | variant_record_st'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_field_item(t)

def p_opt_get(t):#ok
    '''opt_get : GET order_list END
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_opt_get(t)

def p_opt_set(t):#ok
    '''opt_set : SET order_list END
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_opt_set(t)

def p_member_list(t): #ok
    '''member_list : member_fun_list
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_member_list(t)

def p_member_fun(t): #ok
    '''member_fun : ambit fundef
    | target_comment_st'''
    global active_lang, LANG_TABLE
    if len(t)==3:
        t[0]= LANG_TABLE[active_lang].process_member_fun(t)
    else:
        t[0] = LANG_TABLE[active_lang].process_target_comment_st(t)
    #print('t[0] en p_member_fun: %s'%t[0])

def p_member_fun_list(t): #ok
    '''member_fun_list : member_fun_ext  member_fun_list
    | member_fun_ext'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_member_fun_list(t)
        
def p_member_fun_ext(t): #ok
    '''member_fun_ext : member_fun
    | friend_st
    | BLOCK STATIC order_list END'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_member_fun_ext(t)

def p_oper_type(t): #ok
    ''' oper_type : PLUS
    | MINUS
    | TIMES
    | DIV
    | EQ
    | EQUAL
    | GE
    | NE
    | GT
    | LT
    | LE
    | EXTRACTOR
    | INSERTOR
    | INSERTOREQ
    | EXTRACTOREQ
    | AMPERSANDEQ
    | PTR
    | PTREQ
    | PLUSEQ
    | MINUSEQ
    | TIMESEQ
    | DIVEQ
    | ARROW
    | ARROW TIMES
    | AMPERSAND
    | LPAREN RPAREN
    | LBRACK RBRACK
    | DOTDOT
    | INCR
    | INCR PLUS
    | INCR MINUS
    | AND
    | OR
    | NOT
    | DESTR
    | COMMA
    | DOT
    | PIPE
    | PIPE EQUAL
    | ID'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_oper_type(t)
#---------------------------------------------------------------------------------------------------------        

def p_fundef_section(t): #ok
    '''fundef_section : begin_fun_section funlist end_fun_section'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_fundef_section(t)

def p_begin_fun_section(t): #ok
    '''begin_fun_section : BEGIN'''
    global active_lang, LANG_TABLE,INSIDE_FUNC
    t[0]= LANG_TABLE[active_lang].process_begin_fun_section(t)
    #Poner a 1 el flag de funciones para permitir la definicion de funciones miembro
    INSIDE_FUNC+=1

def p_end_fun_section(t): #ok
    '''end_fun_section : ENDSEC'''
    global active_lang, LANG_TABLE,INSIDE_FUNC
    t[0]= LANG_TABLE[active_lang].process_end_fun_section(t)
    #restablecer flag de funciones
    INSIDE_FUNC-=1
    
def p_funlist(t): #ok
    '''funlist : funlist_elem
    | funlist_elem funlist'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_funlist(t)

def p_fundef(t): #LANG (REVISAR BIEN ANTES DE CAMBIAR)
    '''fundef : annotation_list cls_mod funtype generic LPAREN funcargs RPAREN COLON order_list END
    | annotation_list cls_mod funtype generic LPAREN funcargs RPAREN COLON empty END
    | annotation_list cls_mod funtype generic LPAREN funcargs RPAREN  AS generic COLON order_list END
    | annotation_list cls_mod funtype generic LPAREN funcargs RPAREN  AS generic COLON empty END'''
    global user_funcs,__functions,__inclass,__current_namespace,py_checks,funcstring,py_opers,LANG_TABLE,active_lang
    t[0]= LANG_TABLE[active_lang].process_fundef(t,user_funcs=user_funcs,__functions=__functions,__inclass=__inclass,__current_namespace=__current_namespace,py_checks=py_checks,funcstring=funcstring,py_opers=py_opers)


def p_funtype(t):#ok
    '''funtype : FUNCTION
    | CFUNCTION
    | DELEGATE
    | OPERATOR oper_type'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_funtype(t)

def p_funlist_elem(t): #ok
    '''funlist_elem : fundef
    | enum_st
    | asyn_fun'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_funlist_elem(t)

#Nuevo
def p_annot_st(t):#ok
    '''annot_st : annotation_list'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_annot_st(t)

def p_annotation_list(t):#ok
    '''annotation_list : annotation annotation_list
    | annotation
    | generic_defs
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_annotation_list(t)

def p_annotation(t):#ok
    '''annotation : LBRACK PTR annot_elems_list RBRACK'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_annotation(t)

def p_annot_elems_list(t):#ok
    '''annot_elems_list : annot_elem
    | annot_elem annot_elems_list'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_annot_elems_list(t)

#Cambio para permitir idchain en annotations
def p_annot_elem(t):#No
    '''annot_elem : funcall
    | idchain'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_annot_elem(t)

def p_funcargs(t): #ok
    '''funcargs : idfunlist optional_args
    | optional_args'''
    global active_lang,LANG_TABLE,__inclass
    t[0] = LANG_TABLE[active_lang].process_funcargs(t,__inclass=__inclass)

def p_funcargs2(t): #ok
    '''funcargs2 : idfunlist optional_args
    | optional_args'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_funcargs2(t)

def p_optional_args(t): #ok
    '''optional_args : PIPE TIMES defaults_item COMMA EXP defaults_item
    | PIPE EXP defaults_item
    | PIPE TIMES defaults_item
    | PIPE defaults_chain
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_optional_args(t)

def p_defaults_chain(t): #ok
    '''defaults_chain : defaults_ex COMMA defaults_chain
    | defaults_ex'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_defaults_chain(t)

def p_defaults_ex(t):#ok
    '''defaults_ex : QUESTION ID EQUAL defaults_item
    | QUESTION ID AS generic EQUAL defaults_item
    | QUESTION TIMES defaults_item
    | QUESTION defaults_item'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_defaults_ex(t)

def p_defaults_item(t):#ok
    '''defaults_item : expr
    | path_elem'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_defaults_item(t)

def p_idlist(t): #ok
    '''idlist : idel
    | idel COMMA idlist
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_idlist(t)

def p_idel(t): #ok
    '''idel : idchain
    | idexlist'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_idel(t)

def p_idexlist(t): #ok
    '''idexlist : ID DOTDOT ID
    | ID DOTDOT idexlist'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_idexlist(t)

def p_idfunlist(t): #ok
    '''idfunlist : idfunitem
    | idfunitem COMMA idfunlist'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_idfunlist(t)

def p_idfunitem(t): #ok
    '''idfunitem : ID
    | THIS DOT ID
    | ID AS generic
    | TRIDOT path_elems_list
    | fptr2'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_idfunitem(t)  

#Enums------------------------------------------------

def p_enum_st(t):#ok
    ''' enum_st : ENUM generic COLON enum_item_list field_list member_list opt_implem END'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_enum_st(t)

def p_opt_implem(t):
    '''opt_implem : IMPLEMENTS generic_list
    | empty'''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_opt_implem(t)

def p_enum_item_list(t):#ok
    ''' enum_item_list : enum_item
    | enum_item COMMA enum_item_list'''
    global active_lang, LANG_TABLE,enum_counter
    t[0]= LANG_TABLE[active_lang].process_enum_item_list(t)       
    enum_counter=0

def p_enum_item(t):#ok
    ''' enum_item :  ID
    | ID EQUAL expr
    | ID AS generic'''
    global active_lang, LANG_TABLE,enum_counter
    t[0]= LANG_TABLE[active_lang].process_enum_item(t,enum_counter=enum_counter)
    enum_counter+=1

#Esto fallara en JavaScript al menos
def p_global_vars(t):#ok?? Revisar javascript
    '''global_vars : GLOBAL idlist'''
    global active_lang,defined_ids,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_global_vars(t)
    
#----NUEVA VERSION DE order_list----------------------------------------------

def p_order_list(t): #ok?? REvisar pass_st
    '''order_list : valid_st SEMI
    | valid_st SEMI order_list'''
    global active_lang,PASS_ST,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_order_list(t,PASS_ST=PASS_ST)#??hace falta pass_st

#----FIN NUEVA VERSION--------------------------------------------------------

#Gestion de threads-----------------------------------------------------------
#    | empty -> ver si esto es necesario
def p_valid_st(t): #ok
    '''valid_st : var_decl
    | assign_exp
    | expr_list
    | incr_st
    | return_st
    | break_st
    | continue_st
    | yield_st
    | if_st
    | cond_st
    | while_st
    | loopwhen_st
    | foreach_st
    | for_st
    | delete_st
    | try_st
    | assert_st
    | raise_st
    | run_st
    | run_native_st
    | multassign_st
    | multassign2_st
    | typedef_st
    | serialize_st
    | native
    | namespace
    | fundef_section
    | class_section
    | pipeline_st
    | global_vars
    | thread_st
    | array
    | cast_st
    | with_block
    | linq_st
    | dictsetlist_comprehension
    | fptr_decl
    | pass_st
    | pat_match_st
    | fs_fun_def
    | let_st
    | fs_call
    | type_st
    | left_arrow_st
    | module_st
    | type_checker_st
    | do_statement
    | annot_st
    | fptr2
    | using_st
    | asyn_fun
    | generic_block 
    | label_st
    | userdef_st
    | goto_st
    | nop_st
    | equal_list_st
    | asm_like_st
    | await_st
    | switch_st
    | target_comment_st
    | do_let_st
    | s_exp_block
    '''
    global active_lang, LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_valid_st(t)

#-----------------------------------------------------------------------
#--------------------------SOPORTE PARA S-Expresiones-------------------
#-----------------------------------------------------------------------

def p_s_exp_block(t):
    '''s_exp_block : SEXP BLOCK s_exp_sequence END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_s_exp_block(t)

def p_s_exp_sequence(t):
    '''s_exp_sequence : s_exp
    | s_exp s_exp_sequence'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_s_exp_sequence(t)

def p_s_exp(t):
    '''s_exp : atom
    | s_exp_begin s_exp_end
    | s_exp_begin s_exp_list s_exp_end'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_s_exp(t)

def p_s_exp_begin(t):
    '''s_exp_begin : LPAREN
    | LBRACK'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_s_exp_begin(t)

def p_s_exp_end(t):
    '''s_exp_end : RPAREN
    | RBRACK'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_s_exp_end(t)

def p_s_exp_list(t) :
    '''s_exp_list : s_exp
    | s_exp s_exp_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_s_exp_list(t)

def p_atom(t):
    '''atom : ID
    | USERDEF
    | LISPID
    | DOT
    | COLON
    | STRING
    | NUMBER
    | COMPLEX
    | COMPLEX_OP
    | PLUS
    | MINUS
    | TIMES
    | DIV
    | LT
    | GT
    | ARROBA
    | SEMI
    | PIPE
    | AMPERSAND
    | QUESTION
    | DOLLAR
    | TRUE
    | FALSE
    | ARROW
    | LEFTARROW
    | target_comment_st'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_atom(t)

#-----------Fin soporte para S-Expresiones------------------------------

#Nuevo: Soporte para switch------------------------------------------------------------------------------
def p_switch_st(t): #ok
    '''switch_st : SWITCH condic_expr switch_case_list ELSE DO order_list END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_switch_st(t)

def p_switch_case_list(t): #ok
    '''switch_case_list : CASE  condic_expr DO order_list
    | CASE  condic_expr DO order_list switch_case_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_switch_case_list(t)
#fin soporte para switch--------------------------------------------------------------------------------

#NUEVO: soporte para comentarios en lenguaje destino------------------------------
def p_target_comment_st(t): #ok
    '''target_comment_st : TARGETCOM '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_target_comment_st(t)
#---------------------------------------------------------------------------------

#NUEVO: soporte para await expr---------------------------------------
def p_await_st(t): #ok
    '''await_st : AWAIT expr '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_await_st(t)
#---------------------------------------------------------------------

#---------------------------------------------------------------------
#Soporte para declaraciones tipo ensamblador--------------------------
#---------------------------------------------------------------------
def p_asm_like_st(t): #ok
    '''asm_like_st : ARROBA LBRACK asm_items_block RBRACK'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_asm_like_st(t)

def p_asm_items_block(t):#ok
    '''asm_items_block : asm_items_list
    | asm_items_list COMMA asm_items_block'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_asm_items_block(t)

def p_asm_items_list(t):#ok
    '''asm_items_list : asm_item
    | asm_item asm_items_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_asm_items_list(t)

def p_asm_item(t):#ok
    ''' asm_item : condic_expr
    | condic_expr EQUAL condic_expr
    | generic_block
    | TRIDOT'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_asm_item(t)
#-----------------------------------------------------------------------


#Soporte para equal_list-----------------------
def p_equal_list_st(t): #ok
    '''equal_list_st : expr LEFTARROW expr LEFTARROW equal_list_st
    | expr LEFTARROW expr '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_equal_list_st(t)


#NUEVO Y EXPERIMENTAL
def p_nop_st(t):#ok
    '''nop_st : NOP'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_nop_st(t)


#NUEVO Y EXPERIMENTAL
def p_userdef_st(t):#ok
    '''userdef_st : USERDEF
    | USERDEF expr'''
    #print ('En userdef_st:%s'%[el for el in t])
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_userdef_st(t)

def p_generic_block_st(t):#ok
    '''generic_block : BLOCK generic FOR generic COLON order_list END
    | BLOCK generic COLON order_list END
    | BLOCK COLON order_list END
    | LCURLY order_list RCURLY'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_generic_block_st(t)


#NUEVO REVISAR!!!!
def p_label_st(t):#ok
    '''label_st : LABEL ID'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_label(t)

#NUEVO REVISAR!!!!
def p_goto_st(t):#ok
    ''' goto_st : GOTO idchain'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_goto_st(t)


#SOPORTE PARA REGISTROS VARIANTES--------------------------------------------------

#NUEVO REVISAR!!!!
def p_variant_record_st(t):#ok
    ''' variant_record_st : CASE idchain AS generic COLON variant_elems_list END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_variant_record_st(t)

#NUEVO REVISAR!!!!
def p_variant_elems_list(t):#ok
    ''' variant_elems_list : expr THEN LPAREN def_list RPAREN
    | expr THEN LPAREN def_list RPAREN variant_elems_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_variant_elems_list(t)

#NUEVO REVISAR!!!!
def p_def_list(t):#ok
    ''' def_list : idchain AS generic
    | idchain AS generic COMMA def_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_def_list(t)

#FIN SOPORTE PARA REGISTROS VARIANTES--------------------------------------------------


#Soporte para async fun en JS
def p_asyn_fun_st(t): #ok
    '''asyn_fun : ASYNC fundef'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_asyn_fun(t)

#Para dar soporte al friend de C++
def p_friend_st(t): #ok
    '''friend_st : FRIEND CLASS generic_list
    | FRIEND FUNCTION generic LPAREN funcargs RPAREN AS generic'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_friend_st(t)

#Para dar soporte a using en C++
def p_using_st(t): #ok
    '''using_st : USING path_elems_list
    | USING path_elems_list AS idlist
    | USING TYPEDEF generic EQUAL init_item'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_using_st(t)

def p_pass_st(t): #ok
    '''pass_st : PASS'''
    global active_lang,LANG_TABLE,PASS_ST
    t[0]=LANG_TABLE[active_lang].process_pass_st(t,PASS_ST)
    PASS_ST=True
    #print("t[0] en PASS: " + t[0])


def p_dictsetlist_comprehension(t):#ok
    '''dictsetlist_comprehension : LCURLY expr COLON expr FOR LPAREN expr COMMA expr RPAREN IN expr opt_cond RCURLY
    | LCURLY dictsetlist_comprehension_elems RCURLY
    | LBRACK dictsetlist_comprehension_elems RBRACK
    | LPAREN dictsetlist_comprehension_elems RPAREN'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_dictsetlist_comprehension(t)

def p_dictsetlist_comprehension_elems(t):#ok
    ''' dictsetlist_comprehension_elems : comprehension_list
    | pat_match_st '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_dictsetlist_comprehension_elems(t)

def p_comprehension_list(t):#ok
    ''' comprehension_list : expr FOR expr IN expr opt_cond
    | expr FOR expr IN expr opt_cond comprehension_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_comprehension_list(t)

def p_opt_cond(t):#ok
    '''opt_cond : IF condic_expr
    | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_opt_cond(t)


def p_with_block(t):#ok
    '''with_block : WITH ID AS expr COLON order_list END
    | ASYNC WITH ID AS expr COLON order_list END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_with_block(t)



def p_c_pointer_st(t):#ok
    '''c_pointer_st : path_elems_list ARROW funcall 
    | path_elems_list ARROW path_elems_list
    | LPAREN TIMES idchain RPAREN ARROW path_elems_list 
    | TIMES LPAREN expr RPAREN '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_c_pointer_st(t)


def p_thread_st(t):#ok
    '''thread_st : THREAD ID IS ID opt_ptcargs opt_join'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_thread(t)

def p_opt_join(t):#ok
    '''opt_join : JOIN
    | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_opt_join(t)

def p_opt_ptcargs(t):#ok
    '''opt_ptcargs : WITH expr_list
    | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_opt_ptcargs(t)

#-----------------------------------------------------------------------
#--------------------------SOPORTE PARA F#------------------------------
#-----------------------------------------------------------------------

def p_do_statement(t):#ok
    '''do_statement : DO order_list END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_do_statement(t)
    #print('t[0] en do_st: %s'%t[0])

def p_do_let_st(t):#ok
    '''do_let_st : DO let_init expr_list BEGIN order_list END'''
    global active_lang,let_counter,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_do_let_st(t)

def p_let_init(t):
    '''let_init : LET
    | LET TIMES
    | LET REC
    | LET ID'''
    global active_lang,let_counter,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_let_init(t)

def p_pat_match_st(t):#ok
    ''' pat_match_st : MATCH match_condition WITH match_options_list END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pat_match_st(t)

def p_match_condition(t):#ok
    ''' match_condition : expr '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_match_condition(t)

def p_match_options_list(t):#ok
    ''' match_options_list : pat_match_item match_options_list
    | pat_match_item'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_match_options_list(t)

def p_pat_match_item(t): #ok
    ''' pat_match_item : PIPE match_pat opt_when THEN  valid_st SEMI
    | PIPE match_pat opt_when THEN  do_statement'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pat_match_item(t)

def p_match_pat(t):#ok
    ''' match_pat : expr
    | expr AS generic
    | dict
    | binor_list
    | LBRACK idlist RBRACK
    | LPAREN idlist RPAREN
    | path_elem EXCLAMATION path_elem'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_match_pat(t)

def p_binor_list(t):#ok
    ''' binor_list : ARROBA binor_st ARROBA'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_binor_list(t)   

#Guardas when para match en F#
def p_opt_when(t):#ok
    ''' opt_when : WHEN condic_expr
    | empty '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_opt_when(t)

def p_fs_fun_def(t):#ok??????
    ''' fs_fun_def : fs_start FUNCTION idchain fs_fun_sep idseq fs_fun_sep2  EQUAL order_list fs_end
    | fs_start FUNCTION idchain fs_fun_sep idseq fs_fun_sep2  AS path_elems_list EQUAL order_list fs_end'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_fs_fun_def(t)

def p_fs_start(t):#ok
    '''fs_start : LET
    | LET REC'''
    global active_lang,LANG_TABLE,INSIDE_FUNC
    #Poner a 1 el flag de funciones para permitir la definicion de funciones
    INSIDE_FUNC+=1
    t[0] = LANG_TABLE[active_lang].process_fs_start(t)

def p_fs_end(t): #ok
    '''fs_end : END'''
    global active_lang,LANG_TABLE,INSIDE_FUNC
    t[0] = LANG_TABLE[active_lang].process_fs_end(t)
    #restablecer flag de funciones
    INSIDE_FUNC-=1

def p_idseq(t):#ok
    ''' idseq : idchain idseq
    | idchain
    | empty'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_idseq(t)

def p_fs_fun_sep(t):#ok
    '''fs_fun_sep : PIPE
    | LPAREN'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_fs_fun_sep(t)        

def p_fs_fun_sep2(t):#ok
    '''fs_fun_sep2 : PIPE
    | RPAREN'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_fs_fun_sep2(t)

def p_fs_call(t):#ok
    '''fs_call :  idchain AMPERSAND  fs_funcall_chain '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_fs_call(t)

def p_fs_funcall_chain(t):#ok
    '''fs_funcall_chain : condic_expr fs_funcall_chain
    | condic_expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_fs_funcall_chain(t)


def p_let_st(t):#ok
    '''let_st : LET IN idlist EQUAL order_list END'''
    global active_lang,let_counter,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_let_st(t,let_counter=let_counter)
    let_counter+=1


def p_module_st(t): #ok
    '''module_st : MODULE idlist EQUAL order_list END'''
    global active_lang,LANG_TABLE,importstring
    t[0]=LANG_TABLE[active_lang].process_module_st(t,importstring=importstring)
    importstring = ''

def p_type_st(t):#ok
    ''' type_st : TYPE generic EQUAL type_items opt_members END
    | TYPE generic EQUAL union_item END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_type_st(t)

def p_opt_members(t):#ok
    '''opt_members : WITH let_members_list
    | empty'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_opt_members(t)

def p_letmembers_list(t):#ok
    '''let_members_list : let_item let_members_list
    | let_item'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_letmembers_list(t)

def p_let_item(t):#ok
    '''let_item : fs_fun_def
    | THIS ID AS generic EQUAL expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_let_item(t)

def p_type_items(t):#ok
    ''' type_items : type_items_list
    | LCURLY pair_list2 RCURLY'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_type_items(t)

def p_type_items_list(t):#ok
    ''' type_items_list : type_item type_items_list
    | type_item'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_type_items_list(t)

def p_type_item(t):#ok
    ''' type_item : union_fields'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_type_item(t)

def p_union_fields(t):#ok
    ''' union_fields : PIPE generic OF union_item'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_union_fields(t)

def p_union_item(t):#ok
    ''' union_item : generic_list2
    | array
    | LCURLY pair_list2 RCURLY'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_union_item(t)

def p_pair2(t): #ok
    '''pair2 : idchain COLON generic'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pair2(t)

def p_pair_list2(t): #ok
    '''pair_list2 : pair2 COMMA pair_list2
    | pair2'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pair_list2(t)

def p_generic_list2(t):#ok
    ''' generic_list2 : generic generic_list2
    | generic'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_generic_list2(t)

def p_type_checker_st(t):#ok
    ''' type_checker_st : TYPE CHECKER ID EQUAL funcall'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_type_checker_st(t)

def p_left_arrow_st(t):#ok
    ''' left_arrow_st : assignable LEFTARROW expr_list '''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_left_arrow_st(t)

#-----------------------------------------------------------------------
#------------------FIN SOPORTE PARA F#----------------------------------
#-----------------------------------------------------------------------

def p_new_st(t): #ok
    '''new_st : NEW generic
    | NEW dict
    | NEW CLASS generic field_list member_list END 
    | NEW generic LPAREN defaults_chain RPAREN
    | NEW generic LCURLY expr_list RCURLY
    '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_new_st(t)


def p_typedef_st(t): #ok
    '''typedef_st : TYPEDEF generic AS generic 
    | TYPEDEF generic
    | TYPEDEF generic generic_list ARROW generic'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_typedef_st(t)


def p_list_compr(t):#ok
    '''list_compr : TAKE take_var ARROW expr FROM PIPE expr_list PIPE
    | TAKE take_var ARROW expr FROM PIPE list_compr PIPE
    | TAKE take_var ARROW expr FROM PIPE expr_list PIPE WHERE condic_expr
    | TAKE take_var ARROW expr FROM PIPE list_compr PIPE WHERE condic_expr
    | TAKE LAZY take_var ARROW expr FROM PIPE expr_list PIPE
    | TAKE LAZY take_var ARROW expr FROM PIPE list_compr PIPE
    | TAKE LAZY take_var ARROW expr FROM PIPE expr_list PIPE WHERE condic_expr
    | TAKE LAZY take_var ARROW expr FROM PIPE list_compr PIPE WHERE condic_expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_list_compr(t)

def p_take_var(t): #ok
    '''take_var : idlist
       | ID AS generic'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_take_var(t)

def p_functional_st(t): #ok
    '''functional_st :
    | filter_st
    | map_st
    | reduce_st
    | slice_st
    | group_st
    | order_st
    | list_compr
    | linq_st
    | dictsetlist_comprehension
    '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_functional_st(t)

def p_run_st(t):#ok
    '''run_st : RUN expr
    | RUN expr AS ID'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_run_st(t)

def p_run_native_st(t):#ok
    '''run_native_st : RUN NATIVE expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_run_native_st(t)


def p_serialize_st(t):#ok
    '''serialize_st : SERIALIZE path_elems_list IN expr
    | SERIALIZE path_elems_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_serialize_st(t)


def p_deserialize_st(t):#ok
    '''deserialize_st : DESERIALIZE FROM expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_deserialize_st(t)
    

def p_multassign_st(t): #ok???
    '''multassign_st : LBRACK multassign_elems_list RBRACK  EQUAL expr'''
    global deconstruct_name,deconstruct_counter,active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_multassign_st(t,deconstruct_name=deconstruct_name,deconstruct_counter=deconstruct_counter)
    deconstruct_counter+=1

def p_multassign_elems_list(t):#ok
    '''multassign_elems_list : multassign_elem COMMA multassign_elems_list
    | multassign_elem'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_multassign_elems_list(t)

def p_multassign_elem(t): #ok
    '''multassign_elem : path_elems_list
    | LBRACK multassign_elems_list RBRACK
    | LPAREN multassign_elems_list RPAREN
    | NULL'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_multassign_elem(t)

def p_multassign2_st(t):#ok 
    '''multassign2_st : path_elems_list_list  EQUAL expr
    | path_elems_list_list PIPE path_elems_list EQUAL expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_multassign2_st(t)
    
def p_pipeline_st(t): #LANG
     '''pipeline_st : PIPE GT expr_list pipeline_list'''
     global active_lang,LANG_TABLE
     if active_lang!='python':
         t[0] = LANG_TABLE[active_lang].process_pipeline_st(t)
     else:
         t[0]=''
         funcs=[ el for el in t[4].split('|>') if el!='']
         #print 'funcs: %s' % funcs
         #root=''
         for i in range(len(funcs)):
             if i==0:
                 t[0]=funcs[0] + '(' + t[3] + ')'
             else:
                 t[0]=funcs[i] + '(' + t[0] + ')'
     #print 't[0] en pipeline_st: %s'%t[0]

def p_pipeline_list(t): #No
     '''pipeline_list : PIPE GT pipeline_item pipeline_list
     | PIPE GT pipeline_item'''
     if len(t)==5:
         t[0]=t[1]+t[2]+t[3] + t[4]
     else:
         t[0]=t[1]+t[2]+t[3]

def p_pipeline_item(t): #No
     '''pipeline_item : path_elems_list
     | generic_list
     | curried_item
     | PUT IN path_elems_list'''
     if len(t)==2:
        t[0]=t[1]
     else:
        t[0]=t[3] + '.send'

def p_curried_item(t):#LANG
    '''curried_item : ARROBA idseq'''
    global active_lang,old_langs,LANG_TABLE
    if active_lang not in ['python','cython']:
        t[0] = LANG_TABLE[active_lang].process_curried_item(t)
    else:
        #print('Devuelto por idseq: %s'%t[2])
        t[0]='_curry(' + t[2] + ')'

def p_var_decl(t): #ok????
    '''var_decl : var_type idlist
    | var_type idlist EQUAL init_item
    | var_type idlist AS generic
    | var_type idlist AS generic EQUAL init_item
    | var_type idlist AS generic LPAREN expr_list RPAREN
    | var_type idlist LBRACK expr RBRACK AS generic
    | var_type idlist LBRACK expr RBRACK AS generic EQUAL init_item'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_var_decl(t)

def p_var_type(t):#ok
    '''var_type : SETVAR
    | SETCVAR
    | LET
    | CONST
    | REF'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_var_type(t)

def p_init_item(t):#ok
    ''' init_item : expr_list
    | new_st
    | struct_initializer
    | curried_item
    | anonym_st
    | incr_st
    | pat_match_st'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_init_item(t)

def p_fptr2(t):#ok
    '''fptr2 : FUNCTION TIMES generic generic_list ARROW generic'''
    global active_lang,LANG_TABLE
    t[0] =  LANG_TABLE[active_lang].process_fptr2(t)

def p_fptr_decl(t):#ok
    '''fptr_decl : fptr2 EQUAL fptr_decl_val'''
    global active_lang,LANG_TABLE
    t[0] =  LANG_TABLE[active_lang].process_fptr_decl(t)

def p_fptr_decl_val(t):#ok
    '''fptr_decl_val : init_item
    | array'''
    global active_lang,LANG_TABLE
    t[0] =  LANG_TABLE[active_lang].process_fptr_decl_val(t)

def p_c_address(t): #ok(Python entra por aqui en cosas como "f(*args)")
    '''c_address : AMPERSAND path_elems_list
    | TIMES path_elems_list'''
    global active_lang,LANG_TABLE
    t[0] =  LANG_TABLE[active_lang].process_c_address(t)


#-----Cambio en generic para aceptar declaraciones de tipos array en C y C++--------------
def p_generic(t): #ok
    '''generic : idchain
    | LT generic_list GT
    | idchain LT generic_list GT
    | idchain dimensions_list
    | idchain LBRACK generic_list RBRACK
    | idchain AMPERSAND LPAREN generic_list RPAREN
    | generic sufix_list
    | generic sufix_list dimensions_list
    | generic DOTDOT generic
    | generic TRIDOT
    | generic AS generic
    | generic opt_where_list END'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_generic(t)

def p_dimensions_list(t): #ok
    '''dimensions_list : dimensions_elem
    | dimensions_elem dimensions_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_dimensions_list(t)

def p_dimensions_elem(t): #ok
    '''dimensions_elem : LBRACK RBRACK
    | LBRACK expr RBRACK'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_dimensions_elem(t)

#------------------------Fin Cambio----------------------------------------------------------

def p_sufix_list(t): #ok
    '''sufix_list : sufix_elem
    | sufix_elem sufix_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_sufix_list(t)

def p_sufix_elem(t): #ok
    '''sufix_elem : AMPERSAND
    | TIMES'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_sufix_elem(t)

def p_generic_list(t):#ok
    '''generic_list : generic_list_item
    | generic_list_item TRIDOT
    | generic_list_item COMMA generic_list
    | generic_list_item DOTDOT generic_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_generic_list(t)

def p_generic_list_item(t):#ok
    '''generic_list_item : generic
    | PIPE condic_expr PIPE
    | PIPE wildcards PIPE'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_generic_list_item(t)

def p_wildcards(t):#ok
    '''wildcards : QUESTION wc_items
    | QUESTION EXTENDS wc_items
    | QUESTION FROM wc_items'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_wildcards(t)

def p_wc_items(t):#ok
    '''wc_items : wc_list
    | empty'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_wc_items(t)

def p_wc_list(t):#ok
    '''wc_list : idchain 
    | idchain AMPERSAND wc_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_wc_list(t)

#-----------------------------------------------------------------------------------------------|
#No se puede poner condic_expr en el lado derecho, porque no interpreta bien la expresion!!!!!!!|
#-----------------------------------------------------------------------------------------------|
def p_assign_exp(t):#ok
    '''assign_exp : assignable EQUAL expr_list
    | assignable short_op expr
    | assignable EQUAL curried_item
    | assignable EQUAL functional_st
    | assignable EQUAL anonym_st
    | assignable EQUAL lambda_st
    | assignable EQUAL new_st
    | assignable EQUAL pipeline_st
    | assignable EQUAL let_st
    | assignable EQUAL YIELD expr
    | assignable EQUAL PIPE YIELD PIPE
    | assignable EQUAL lazy_expr
    | assignable EQUAL THREAD IS ID opt_ptcargs opt_join
    | assignable EQUAL ASYNC PIPE ID expr_list PIPE
    | assignable EQUAL AWAIT expr
    | assignable EQUAL AWAIT expr THEN expr
    | assignable EQUAL incr_st'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_assign_exp(t)

def p_short_op(t):#ok
    '''short_op : MINUSEQ
    | TIMESEQ
    | DIVEQ
    | PLUSEQ'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_short_op(t)

def p_next_expr(t): #ok
    '''next_expr : GET expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_next_expr(t)

def p_send_expr(t): #ok
    '''send_expr : PUT expr IN expr_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_send_expr(t)

def p_lazy_expr(t): #ok
    '''lazy_expr : LAZY iterable_expr'''
    global lazy_counter,lazy_name,active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_lazy_expr(t,lazy_name=lazy_name,lazy_counter=lazy_counter)
    lazy_counter+=1

def p_iterable_expr(t):#ok
    '''iterable_expr : expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_iterable_expr(t)

def p_ifelse(t): #ok
    '''ifelse_st : expr IF condic_expr ELSE expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_ifelse(t)

def p_assignable(t): #No
    '''assignable : path_elems_list
    | c_pointer_st
    | c_address'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_assignable(t)

def p_return_st(t): #ok
    '''return_st : RETURN ret_item'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_return_st(t)

def p_ret_item(t):#ok
    '''ret_item : condic_expr
    | condic_expr AS generic
    | anonym_st
    | empty'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_ret_item(t)

def p_yield_st(t): #ok
    '''yield_st : YIELD condic_expr
    | YIELD FROM condic_expr
    | YIELD EXCLAMATION condic_expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_yield_st(t)

def p_incr_st(t): #ok
    '''incr_st : path_elems_list INCR
       | c_pointer_st INCR
       | c_address INCR
       | INCR path_elems_list
       | INCR c_pointer_st
       | INCR c_address'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_incr_st(t)

      
#----COMIENZO PRUEBAS CATCH MULTIPLE--------------------------          
def p_try_st(t): #ok
    '''try_st : TRY COLON order_list catch_list FINALLY COLON order_list END
       | TRY COLON order_list catch_list END'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_try_st(t)

def p_catch_list(t):#ok
    '''catch_list : CATCH opt_id COLON order_list opt_where_list
    | CATCH opt_id COLON order_list opt_where_list catch_list
    | empty'''
    #print([el for el in t])
    #print(len(t))
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_catch_list(t)

def p_opt_where_list(t): #ok
    '''opt_where_list : WHERE expr_list
    | WHERE fptr2 
    | empty '''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_opt_where_list(t)

def p_opt_id(t):#ok
    '''opt_id : idchain
    | idchain AS generic
    | empty'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_opt_id(t) 

#----FIN PRUEBAS CATCH MULTIPLE--------------------------           

def p_assert_st(t): #ok
    '''assert_st : ASSERT condic_expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_assert_st(t)

def p_raise_st(t): #ok
    '''raise_st : RAISE expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_raise_st(t)

def p_if_st(t): #ok??
    '''if_st : if_mark if_elem THEN order_list END
    | if_mark if_elem THEN order_list ELSE order_list END
    | if_mark if_elem THEN order_list elif_list ELSE order_list END'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_if_st(t)

#Nuevo: Soporte para elif------------------------------------------------------------------------------
def p_elif_list(t): #ok
    '''elif_list : ELIF  condic_expr THEN order_list
    | ELIF  condic_expr THEN order_list elif_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_elif_list(t)
#fin soporte para elif--------------------------------------------------------------------------------


def p_if_mark(t):#ok
    '''if_mark : IF
    | CHECKER'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_if_mark(t)


def p_if_elem(t):#ok
    ''' if_elem : condic_expr
    | LET expr EQUAL expr
    | LET expr EQUAL incr_st
    | expr IS expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_if_elem(t)

def p_cond_st(t): #ok
    '''cond_st : COND expr case_list ELSE DO order_list END'''
    global active_lang,cnd_counter,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_cond_st(t,cnd_counter=cnd_counter)
    cnd_counter+=1

def p_case_list(t): #ok
    '''case_list : CASE relop_plus expr DO order_list
    | CASE relop_plus expr DO order_list case_list'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_case_list(t)

def p_while_st(t): #ok
    '''while_st : start_while while_cond_elem DO order_list END end_loop'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_while_st(t)

def p_while_cond_elem(t):#ok
    ''' while_cond_elem : condic_expr
    | LET expr EQUAL expr
    | LET expr EQUAL incr_st'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_while_cond_elem(t)

def p_start_while(t):#ok
    '''start_while : WHILE'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    INSIDE_LOOP+=1 
    t[0] = LANG_TABLE[active_lang].process_start_while(t)

def p_loopwhen_st(t): #ok
    '''loopwhen_st : start_loop order_list UNTIL while_cond_elem END'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_loopwhen_st(t)

def p_start_loop(t):#ok
    '''start_loop : REPEAT'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    INSIDE_LOOP+=1
    t[0] = LANG_TABLE[active_lang].process_start_loop(t)

def p_start_for(t):#ok
    '''start_for : FOR'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    INSIDE_LOOP+=1
    t[0] = LANG_TABLE[active_lang].process_start_for(t)

#Nueva opcion para el for
def p_for(t): #ok
    '''for_st : start_for for_option1 COMMA for_option2 COMMA for_option3 DO order_list END end_loop'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_for_st(t)

def p_for_option1(t):#ok
    '''for_option1 : COLON
    | for_var EQUAL expr
    | DO order_list END'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_for_option1(t)

def p_for_option2(t):#ok
    '''for_option2 : COLON
    | condic_expr
    | DO order_list END'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_for_option2(t)

def p_for_option3(t):#ok
    '''for_option3 : COLON
    | incr_st
    | ID EQUAL expr
    | DO order_list END'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_for_option3(t)

#Fin nueva opcion for

#REcuperar esto si va mal. Sobra ID????
#'''foreach_st : start_foreach foreach_var foreach_selector expr DO order_list END end_loop
#    | start_foreach foreach_var foreach_selector ID DO order_list END end_loop'''
def p_foreach_st(t): #ok
    '''foreach_st : start_foreach foreach_var foreach_selector expr DO order_list END end_loop'''
    global active_lang,LANG_TABLE
    t[0]= LANG_TABLE[active_lang].process_foreach_st(t)

def p_foreach_selector(t):#ok
    '''foreach_selector : IN
    | OF
    | CONST OF'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_foreach_selector(t)

def p_foreach_var(t):#ok
    '''foreach_var : idlist
       | ID AS generic'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_foreach_var(t)

def p_for_var(t):#ok
    '''for_var : ID
       | ID AS generic'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_for_var(t)

def p_start_foreach(t):#ok
    '''start_foreach : FOREACH'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    INSIDE_LOOP+=1
    t[0] = LANG_TABLE[active_lang].process_start_foreach(t)

def p_break_st(t):#ok
    '''break_st : BREAK
    | BREAK idchain'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    if INSIDE_LOOP==0: raise Exception('Error: solo se puede usar la sentencia "break" dentro de un bucle')#??
    t[0] = LANG_TABLE[active_lang].process_break_st(t)

def p_continue_st(t):#ok
    '''continue_st : CONTINUE
    | CONTINUE idchain'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    if INSIDE_LOOP==0: raise Exception('Error: solo se puede usar la sentencia "continue" dentro de un bucle')
    t[0] = LANG_TABLE[active_lang].process_continue_st(t)

def p_end_loop(t):#ok
    '''end_loop : empty'''
    global INSIDE_LOOP,active_lang,LANG_TABLE
    INSIDE_LOOP-=1
    if INSIDE_LOOP<0: INSIDE_LOOP=0
    t[0] = LANG_TABLE[active_lang].process_end_loop(t)
 
def p_pair(t): #ok
    '''pair : expr COLON condic_expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pair(t)

def p_pair_list(t): #ok
    '''pair_list : pair COMMA pair_list
    | pair
    | empty'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pair_list(t)

def p_condic_expr(t): #ok
    '''condic_expr : condic_expr OR condic_expr
    | and_exp'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_condic_expr(t)
   
def p_and_exp(t): #ok
    '''and_exp : and_exp AND not_exp
    | not_exp'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_and_exp(t)
   
def p_not_exp(t): #ok
    '''not_exp : NOT condic_expr
    | bool_exp'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_not_exp(t)

def p_bool_exp(t): #ok
    '''bool_exp : expr relop_list
    | LPAREN condic_expr RPAREN
    | MATCH expr IN expr'''
    #print("en bool_exp: %s" % [el for el in t])
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_bool_exp(t) 

def p_relop_list(t):
    '''relop_list : relop expr
    | relop expr relop_list
    | empty'''
    global ERROR_MSG
    #print("en relop_list: %s" % [el for el in t])
    #Correccion para error por permitir exppr_list como valid_st:
    #permite cosas como y <;
    if len(t)==3 and t[2]=='': #Generar un error
        ERROR_MSG = f"\n\tfalta segundo operando en expresión de comparación: '{t[1]} ?'."
        p_error(t)
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_relop_list(t) 


def p_relop(t): #ok
    '''relop : EQ
    | TRIEQ
    | GT
    | GE
    | LT
    | LE
    | NE
    | NE2
    | IN
    | NOT IN'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_relop(t)

def p_relop_plus(t): #ok
    '''relop_plus : EQ
    | TRIEQ
    | GT
    | GE
    | LT
    | LE
    | NE
    | NE2
    | IN
    | NOT IN
    | MATCH
    | NOT MATCH'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_relop_plus(t)

def p_expr(t): #ok
    '''expr : expr PLUS termino
    | expr MINUS termino
    | expr COLON COLON termino
    | expr INSERTOR termino
    | expr EXTRACTOR termino
    | expr ARROBA termino
    | expr IS termino
    | expr DQUESTION termino
    | expr DESTR termino
    | expr NE3 termino
    | expr NE4 termino
    | expr BINOR termino
    | expr BINAND termino
    | expr BINNOT termino
    | expr USERDEF termino
    | expr COMPLEX_OP termino
    | expr EXTRAOPS termino
    | termino
    | annotation  
    | binor_st
    | cast_st
    | left_arrow_st
    '''
    global active_lang,LANG_TABLE
    #print("en expr: %s" % [el for el in t])
    #Si los dos miembros del operador son '' -> p_error(t) para no permitir cosas como 5- o +-+- en principio posibles
    if len(t)==4:
        if t[1]=='' or t[3]=='':
            p_error(t)
    t[0]= LANG_TABLE[active_lang].process_expr(t)


def p_termino(t): #ok
    '''termino : termino TIMES pot_factor
    | termino DIV pot_factor
    | pot_factor'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_termino(t)
      
#Revisar para usar Math.pow, que tiene mucho mejor rendimiento
def p_pot_factor(t): #ok
    '''pot_factor : factor EXP factor
    | factor'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_pot_factor(t)


def p_factor(t): #ok
    '''factor : LPAREN expr RPAREN
    | STRING
    | MINUS expr 
    | PLUS expr 
    | DESTR expr
    | COMPLEX_OP expr 
    | USERDEF expr 
    | EXTRAOPS expr 
    | NUMBER
    | COMPLEX
    | NULL
    | expr_list_item DOT funcall
    | STRING DOT funcall
    | expr_list_item accesors
    | STRING accesors
    | path_elems_list
    | expr_list_item
    | ifelse_st 
    | format_st
    | serialize_st
    | deserialize_st
    | TRUE
    | FALSE
    | c_address
    | c_pointer_st
    | incr_st
    | cast_st
    | ARROW PIPE LPAREN generic RPAREN LCURLY expr_list RCURLY PIPE
    | LPAREN expr EQUAL expr RPAREN
    | LPAREN expr RPAREN accesors
    | LPAREN expr RPAREN LPAREN funcall_chain RPAREN
    '''
    global active_lang,LANG_TABLE
    #print("en factor: %s" % [el for el in t])
    t[0]=LANG_TABLE[active_lang].process_factor(t)

def p_expr_list(t): #ok
    '''expr_list : condic_expr
    | condic_expr COMMA expr_list'''
    global active_lang,LANG_TABLE
    #print("en expr_list: %s" % [el for el in t])
    t[0] = LANG_TABLE[active_lang].process_expr_list(t)


def p_path_elems_list(t): #ok
    '''path_elems_list : path_elem path_elem_sep path_elems_list
    | path_elem'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_path_elems_list(t)

#def p_binor_st(t):#ok
#    '''binor_st : binor_elem EXCLAMATION binor_elem
#    | binor_elem EXCLAMATION binor_st'''
#    global active_lang,LANG_TABLE
#    t[0] = LANG_TABLE[active_lang].process_binor_st(t)

def p_binor_st(t):#ok
    '''binor_st : binor_elem NE3 binor_elem
    | binor_elem EXCLAMATION binor_st'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_binor_st(t)


def p_binor_elem(t): #ok
    '''binor_elem : factor '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_binor_elem(t)

#---CAMBIO para permitir cadenas con -> (a->b->c) para C--------
def p_path_elem_sep(t):#ok
    '''path_elem_sep : DOT
    | DOTDOT
    | ARROW'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_path_elem_sep(t)
#---Fin cambio----------------------------------------------------

#GRAN CAMBIO: necesitamos esto para prescindir de funcall_generic!!!
#Sin idchain, confunde x * y con genericos, asi como x<y y similares
#Puede tener limitaciones por no usar generic AMPERSAND LT generic_list GT???
#OJO: no se puede poner aqui STRING accesors ni expr_list_item accesors,
#con idea de poder hacer cadenas de llamada con strings y listas, porque falla

def p_path_elem(t): #ok
    '''path_elem : idchain
    | idchain AMPERSAND LT generic_list GT
    | idchain AMPERSAND LT expr GT
    | funcall
    | fs_call
    | this_st
    | idchain accesors
    | funcall accesors
    | LCURLY expr RCURLY'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_path_elem(t)

def p_path_elems_list_list(t): #ok
    '''path_elems_list_list : path_elems_list COMMA path_elems_list_list
    | path_elems_list'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_path_elems_list_list(t)

def p_expr_list_item(t): #ok
    '''expr_list_item : sequence
    | array
    | dict
    | lambda_st
    | functional_st
    | new_st
    | range_st
    | next_expr
    | send_expr
    '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_expr_list_item(t)

def p_range_st(t):#ok
    '''range_st : expr TO expr
    | expr TO expr IN expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_range_st(t)

def p_this_st(t): #ok
    '''this_st : THIS'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_this_st(t)

#Vigilar nueva opcion:     | DESTR LCURLY expr RCURLY LPAREN funcall_chain RPAREN opt_tridot
def p_funcall(t): #ok
    '''funcall : path_elems_list LPAREN funcall_chain RPAREN opt_tridot
    | path_elems_list LCURLY funcall_chain RCURLY opt_tridot
    | path_elems_list LPAREN RPAREN opt_tridot
    | path_elems_list LCURLY RCURLY opt_tridot
    | path_elems_list LPAREN idchain TRIDOT RPAREN opt_tridot
    | path_elems_list LPAREN TRIDOT idchain RPAREN opt_tridot
    | path_elems_list LCURLY idchain TRIDOT RCURLY opt_tridot'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_funcall(t)

def p_opt_tridot(t):#ok
    '''opt_tridot : TRIDOT
    | QUESTION
    | empty'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_opt_tridot(t)

def p_funcall_chain(t): #ok
    '''funcall_chain : expr_list
    | expr_list optional_args
    | optional_args'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_funcall_chain(t)

def p_cast_st(t): #ok
    '''cast_st : PIPE generic PIPE expr'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_cast_st(t)

def p_sequence(t): #ok
    '''sequence : LBRACK RBRACK
    | LBRACK RBRACK AS generic
    | LBRACK expr_list RBRACK
    | LBRACK expr_list COMMA RBRACK
    | LBRACK expr_list RBRACK AS generic'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_sequence(t)

def p_array(t): #ok
    '''array : LCURLY expr_list RCURLY AS generic
    | LCURLY expr_list RCURLY
    | LPAREN expr_list RPAREN'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_array(t)  

#CAMBIO PARA TENER INICIALIZADORES DE ESTRUCTURAS PARA C/C++-----------------
def p_struct_initializer(t):#ok
    '''struct_initializer : LCURLY dotpairlist RCURLY'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_struct_initializer(t)

def p_dotpairlist(t):#ok
    '''dotpairlist : dot_pair COMMA dotpairlist
    | dot_pair
    | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_dotpairlist(t)

def p_dot_pair(t):#ok
    '''dot_pair : DOT expr EQUAL condic_expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_dot_pair(t)

#FIN CAMBIO--------------------------------------------------------------------

def p_dict(t): #ok
    '''dict : LCURLY pair_list RCURLY
    | LCURLY pair_list RCURLY AS generic
    | LCURLY RCURLY
    | LCURLY RCURLY AS generic'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_dict(t)

def p_accesors(t):#ok
    '''
    accesors : accesors_item accesors
    | accesors_item
    '''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_accesors(t)


#Deberiamos separar todo el ajuste de expr en una funcion : hay mucho codigo repetitivo!!!!
def p_accesors_item(t):#ok
    '''accesors_item : LBRACK condic_expr RBRACK
    | LBRACK LBRACK condic_expr RBRACK RBRACK
    | LBRACK  expr_list RBRACK
    | LBRACK expr COLON expr RBRACK
    | LBRACK expr COLON expr COLON expr RBRACK'''
    global active_lang,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_accesors_item(t)

def p_anonym_st(t): #ok
    '''anonym_st : set_an_flags FUNCTION LPAREN funcargs RPAREN COLON order_list END reset_an_flags
    | annotation_list set_an_flags FUNCTION LPAREN funcargs RPAREN COLON order_list END reset_an_flags
    | annotation_list set_an_flags FUNCTION LPAREN funcargs RPAREN AS generic COLON order_list END reset_an_flags'''
    global active_lang,LANG_TABLE,fun_counter
    t[0] = LANG_TABLE[active_lang].process_anonym_st(t,fun_counter=fun_counter)
    #Actualizar fun_counter
    fun_counter+=1

#Esto es un muy buen truco para establecer/restablecer globales
def p_set_an_flags(t): #ok
    '''set_an_flags : empty'''
    global INSIDE_FUNC
    INSIDE_FUNC+=1
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_set_an_flags(t)

def p_reset_an_flags(t): #ok
    '''reset_an_flags : empty'''
    global INSIDE_FUNC
    INSIDE_FUNC-=1
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_reset_an_flags(t)

#Nuevo: soporte para capturas en lambdas
def p_capture_st(t):#ok
    '''capture_st : TAKE idlist
    | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_capture_st(t)

def p_lambda_st(t): #ok
    '''lambda_st : PIPE  LPAREN funcargs2 RPAREN  COLON condic_expr PIPE
    | PIPE  LPAREN funcargs2 RPAREN  COLON DO order_list END capture_st PIPE
    | PIPE  LPAREN funcargs2 RPAREN AS generic COLON DO order_list END capture_st PIPE'''
    global active_lang,fun_counter,LANG_TABLE
    t[0] = LANG_TABLE[active_lang].process_lambda_st(t,fun_counter=fun_counter)
    fun_counter+=1

def p_functional_fun(t): #ok
    '''functional_fun : expr
    | idlist'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_functional_fun(t)

def p_filter_st(t): #ok
    '''filter_st : FILTER functional_fun IN expr_list'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_filter_st(t)

def p_map_st(t): #ok
    '''map_st : MAP functional_fun IN fun_item_list'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_map_st(t)

def p_reduce_st(t): #ok
    '''reduce_st : REDUCE functional_fun IN fun_item_list
    | REDUCE functional_fun IN fun_item_list WITH expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_reduce_st(t)
    
def p_slice_st(t): #ok
    '''slice_st : LBRACK expr COLON expr RBRACK IN fun_item_list'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_slice_st(t)

def p_group_st(t): #ok
    '''group_st : GROUPBY functional_fun IN fun_item_list'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_group_st(t)

def p_fun_list_item(t):#ok
    '''fun_list_item : expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_fun_list_item(t)

def p_fun_item_list(t):#ok
    '''fun_item_list : fun_list_item COMMA fun_item_list
    | fun_list_item'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_fun_item_list(t)

def p_order_st(t): #ok
    '''order_st :  ORDER fun_item_list BY functional_fun opt_reverse'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_order_st(t)

def p_opt_reverse(t):#ok
    '''opt_reverse : REVERSE
       | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_opt_reverse(t)

def p_delete_st(t): #ok
    '''delete_st : DEL path_elems_list'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_delete_st(t)


def p_format_st(t): #ok
    '''format_st : FORMAT expr WITH expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_format_st(t)

def p_empty(t):#ok
    '''
    empty : 
    '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_empty(t)

####----------------------------------------------------------------------------------
####                         MINI LINQ
####----------------------------------------------------------------------------------

##LINQ Query syntax 
##LINQ Query Syntax:
##from <range variable> in <IEnumerable<T> or IQueryable<T> Collection>
##<Standard Query Operators> <lambda expression>
##<select or groupBy operator> <result formation>

#Tendria que ser: linq_st : FROM linq_origin where_linq order_linq lambda_expr select_or_group_linq opt_yield


def p_linq_st(t):#ok
    '''
    linq_st : FROM linq_origin where_linq order_linq select_or_group_linq opt_yield
    '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_linq_st(t)

def p_linq_origin(t):#ok
    '''
    linq_origin : ID IN expr
    '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_linq_origin(t)

def p_where_linq(t):#ok
    '''
    where_linq : WHERE semilambda_st
    | empty
    '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_where_linq(t)

def p_order_linq(t):#ok
    '''
    order_linq : ORDER BY semilambda_st
    | empty
    '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_order_linq(t)

def p_select_or_group_linq(t):#ok
    '''
    select_or_group_linq : SELECT semilambda_st
    | GROUPBY semilambda_st
    '''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_select_or_group_linq(t)

def p_semilambda_st(t):#ok
    '''semilambda_st : condic_expr'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_semilambda_st(t)

def p_opt_yield(t):#ok
    '''opt_yield : YIELD
    | empty'''
    global active_lang,LANG_TABLE
    t[0]=LANG_TABLE[active_lang].process_opt_yield(t)


# Error rule for syntax errors
def p_error(t):#No?????
    #print (dir(t))
    #print(t.__class__)
    #print(dir(t))
    global __program,__program_file,imported_files,ERROR_MSG
    lineno=0
    if t.__class__== ply.yacc.YaccProduction:
        #print('Llamada a p_error con una Produccion!!!')
        #print(t)
        #print(t.lineno(1))
        #print(t.slice)
        #print([(el,type(el)) for el in t.slice])
        lineno = t.lineno(1)
        t = [el for el in t.slice if el.__class__==ply.lex.LexToken]
        #print(dir(t))
    if t not in [None,[]]:
        if type(t) == lex.LexToken:
            buildErrorReport(t)#Coger la excepcion!
        else:
            buildErrorReport(t[0])#Coger la excepcion!
    else:
        buildErrorReportWithNoToken(ERROR_MSG,lineno)
    raise Exception(">>> Bridge language: Program terminated with errors.")

def buildErrorReportWithNoToken(msg,lineno):
    global __program,imported_files,PROG_LINES
    #print(__program)
    plines=__program.split('\n')
    print('='*60)
    print('Bridge Language: Error Report')
    print('='*60)
    print(f"\nError de sintaxis:\n {msg}\n")
    print('Contexto del error:\n' + '-'*60)
    print("... %s => ...,etc.\n" %(plines[lineno-1]))
    print('-'*60)
    #print('Archivo procesado: %s en linea %s.' %(__program_file,(tok.lexer.lineno if tok and tok.lexer!=None else " desconocida")))
    print('Archivo procesado: %s en linea %s.' %(__program_file,lineno))
    print('Importaciones realizadas:\n')
    if imported_files!=[]:
        for item in imported_files:
            print('\t- archivo %s.'%item)
    else:
        print('\t- ninguna.')
    #print('\nArchivo estimado del error: %s.'%guessFile(tok.lexer.lineno))
    print('\nArchivo estimado del error: %s.'%guessFile(lineno))
    print('='*60)
   

def buildErrorReport(tok):
    global __program,imported_files,PROG_LINES
    print('='*60)
    print('Bridge Language: Error Report')
    print('='*60)
    print('Error de sintaxis (token no permitido) evaluando token "%s".'%tok.value if tok else "token es None.")
    #Informar de si es palabra clave----------------------
    if tok.value and tok.value in stlex2.reserved:
        print(f'"{tok.value}" es una palabra reservada de bridge. Para usarla en otro contexto debe comenzar y terminar por "%"')
    #-----------------------------------------------------
    print('Contexto del error:\n' + '-'*60)
    print("... %s   ==>   %s ...,etc.\n" %(__program[tok.lexpos-50:tok.lexpos],__program[tok.lexpos:tok.lexpos + 100]))
    lineno = ''
    if tok and hasattr(tok,'lexer'):
        lineno = tok.lexer.lineno
    elif tok:
        lineno = tok.lineno
    else:
        lineno = ' desconocida'
    #pprint.pprint(list(enumerate(PROG_LINES[tok.lexer.lineno-2 : tok.lexer.lineno + 3])))
    pprint.pprint(list(enumerate(PROG_LINES[lineno-2 : lineno + 3])))
    print('-'*60)
    #print('Archivo procesado: %s en linea %s.' %(__program_file,(tok.lexer.lineno if tok and tok.lexer!=None else " desconocida")))
    print('Archivo procesado: %s en linea %s.' %(__program_file,lineno))
    print('Importaciones realizadas:\n')
    if imported_files!=[]:
        for item in imported_files:
            print('\t- archivo %s.'%item)
    else:
        print('\t- ninguna.')
    #print('\nArchivo estimado del error: %s.'%guessFile(tok.lexer.lineno))
    print('\nArchivo estimado del error: %s.'%guessFile(lineno))
    print('='*60)

def parserFactory():
    #Poner a debug=0 en produccion
    return yacc.yacc(debug=1)#,tabmodule='bridge_parsetab',write_tables=False)#Poner a debug=0 en produccion

parser=parserFactory()



if __name__=='__main__':
    if not 'bridge' in sys.modules:
         bridge=__import__('bridge')
    else:
         bridge=sys.modules['bridge']
    if not 'python_runtime' in sys.modules:
         python_runtime=__import__('python_runtime')
    #imprimir la documentacion del modulo------------------------
    #print(help(bridge))
    #------------------------------------------------------------
    #Establecer opciones de linea de comandos
    setCommandLineOptions(sys.argv)
    #Permitimos arrancar en modo repl minimal, prolog y los lisps
    if repl_mode==1:
        code=''
        if not 'mini_tkbasic' in sys.modules:
            mini_tkbasic=sys.modules['mini_tkbasic']
        while 1:
            code=input('bridge REPL>')
            if code=='quit': break
            bridge.__reflected=1
            code=preprocess(code)
            code=parser.parse(code)
            exec(code)
    #Aqui deberiamos aceptar un encoding por linea de comandos??
    program=open(sys.argv[1],encoding='utf-8',errors='replace').read()
    __program_file=sys.argv[1]

    #Preprocesar imports
    program=preprocess(program)

    #Cambio para usar preprocesador tipo C--------------
    if _use_preproc==True:
        program=preprocessor(program)
        if _show_preproc==True:
            print("-----BRIDGE PREPROCESSOR OUTPUT-----")
            print("------------------------------------")
            print(program)
            print("------------------------------------")
            print("------------------------------------")
    __program=program
    #Fin cambio proprocesador------------------
    code=parser.parse(program,tracking=True)
    if print_script==1:
        print(code)
    #Esto obtiene la gramatica----
    #print help(bridge)
    #-----------------------------
    if exec_script==1:
        exec(code)
    if create_exe==1:
        generateExe()
    if create_exe==0 and extra_files!=[]:
        if outputdir and outputdir!='.':
            copyExtraFiles(outputdir)
        else:
            copyExtraFiles('extras')
    print('>Interprete Bridge finalizado sin errores.')
    #print('DOCUMENTACION: %s' % stlex2.DOC_COMMENTS)
