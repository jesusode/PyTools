
from typing import *
from types import FunctionType,CodeType
import io #Para StringIO en Python 3+


#Compila texto a codigo y devuelve un objeto ejecutable
def pyCompile(code) -> CodeType:
    '''
    Envoltorio simple sobre compile. Compila el texto
    contenido en code a codigo Python ejecutable por
    exec.
    '''
    return compile(code, "<string>" ,"exec")


#Crea funciones a partir de texto en runtime
def dynFunFactory(name,code,context={}) -> FunctionType:
    '''
    Compila code a una funcion que se puede ejecutar directamente
    en el codigo. Se le asignará name a la propiedad __name__ de la misma.
    Si se pasa context, se usará en vez de globals() para buscar los nombres
    de las variables no locales en ella.
    '''
    _code = compile(code, "<string>", "exec")
    return FunctionType(_code.co_consts[0], globals(), name)

def switchBuilder(values : str,options : str,default : str ='') -> CodeType:
    '''
    Crea codigo dinamico para convertir una lista de condiciones, otra de
    opciones y un valor por defecto en un objeto de codigo if-elif-else
    que se compilará, creando un especie de switch para Python.
    '''
    assert(len(values) == len(options))

    switch_str :io.StringIO = io.StringIO()
    for i  in range(len(options)):
        if i==0:
            switch_str.write('if ' + values[i] + ': \n\t' + options[i] + "\n")
        else:
             switch_str.write('elif ' +  values[i] + ' : \n\t' + options[i] + "\n")
    if default!='':
        switch_str.write('else:\n\t' +  default)
    return compile(switch_str.getvalue(),"<string>","exec")


def switchFunBuilder(varname : str,values : str,options : str,default : str ='') -> FunctionType:
    '''
    Crea codigo dinamico para convertir una lista de condiciones, otra de
    opciones y un valor por defecto en una funcion if-elif-else
    que se compilará, creando un especie de switch para Python.
    '''
    assert(len(values) == len(options))

    switch_str :io.StringIO = io.StringIO()
    switch_str.write("def switch_" + varname + '(' + varname + '):\n')
    for i  in range(len(options)):
        if i==0:
            switch_str.write('\tif ' + values[i] + ': \n\t\t' + options[i] + "\n")
        else:
             switch_str.write('\telif ' +  values[i] + ' : \n\t\t' + options[i] + "\n")
    if default!='':
        switch_str.write('\telse:\n\t\t' +  default)
    return dynFunFactory("switch_" + varname,switch_str.getvalue())




#Pruebas
if __name__ == '__main__':
    switch = switchBuilder(["x==1","x==2","x==3","x==4"],
    ["print('value_1')","print('value_2')","print('value_3')", "print('value_4')"],
    "print('default_value')")
    print(switch)
    a = pyCompile("l='abcd'")
    print(a)
    exec(a)
    print(l)
    x=1
    exec(switch)
    f = dynFunFactory("foo","def foo() : return 'bar'")
    print(f())
    switchf = switchFunBuilder("x",["x==1","x==2","x==3","x==4"],
    ["print('value_1')","print('value_2')","print('value_3')", "print('value_4')"],
    "print('default_value')")
    print(switchf)
    switchf(x)
    x=3
    switchf(x)
