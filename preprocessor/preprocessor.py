#!Python

import re
from typing import *
from io import StringIO
import simpleeval


class PreProcMacro:
    '''
    Clase que representa una macro de Preprocesador tipo C
    '''

    def __init__(self, name, value, args, va_args, foreach):
        self.name = name
        self.value = value
        self.args = args
        self.va_args = va_args
        self.foreach = foreach

    def __str_(self):
        return '<<PreProcMacro:\n name: %s\n value: %s\n args: %s\n va_args: %s\n foreach: %s >>\n' % (self.name, self.value, self.args, self.va_args, self.foreach)


# Pruebas para el if en el preprocessor------
def eval_if_expr(e, names):
    #print('names: %s'%names)
    # print('e:%s'%e)
    # print(simpleeval.simple_eval(e,names=names))
    return simpleeval.simple_eval(e, names=names)


# ESTO ESTARIA MEJOR EN EUNA CLASE!!!
# Globales para macros definidas
defines = {}
defines_list = []


# Esta funcion esta escrita en bridge y luego adaptada:).
def preprocessor(txt):
    '''
    Preprocesador tipo C para archivos de texto en general
    '''
    global defines, defines_list
    resul = []
    ignore_lin = False
    ifdef_counter = 0
    endif_counter = 0
    ifndef_counter = 0
    endifn_counter = 0
    ifexp_counter = 0
    endifexp_counter = 0
    lin = ""
    com_st = 0
    com_rest = ""
    str_pre = ""
    multiline_c = False
    multipos = -1
    multiend = -1
    multstring = False
    multspos = -1
    multsend = -1
    passmode = 0
    # Para #include--------
    recursive_mode = 0
    # -----------------------
    variadic_separator = ','
    line_separator = ''
    # for tmp in _split(txt,"\n"):
    for tmp in txt.split("\n"):
    #print("LINEA: " + repr(_strip(tmp)))
    # Cambio para soportar directiva #include: los #includes no seran preprocesados tal y como esta------------------
    # El preprocesador solo pasa una vez. Activar modo recursivo para que se vuelva a preprocesar??????
    # o mejor dar dos pases, uno para includes y otro para preprocesar????
    # if _find(_strip(tmp),"#include")==0:
        if tmp.strip().find("#include") == 0:
            if ignore_lin == 0:  # Esto es para que funcione con los #ifdef
                resul.append(findFileToInclude(tmp.replace("#include", '')))
                recursive_mode = 1
                continue
        # Fin cambio para include----------------------------------------------------------------------------------------
        #print("passmode: %s"%passmode)
        # if _find(_strip(tmp),"#pass")==0:
        if tmp.strip().find("#pass") == 0:
            passmode = 1
            #print('Entrando en passmode...')
            resul.append(tmp)
            continue
        # if _find(_strip(tmp),"#endpass")==0:
        if tmp.strip().find("#endpass") == 0:
            passmode = 0
            #print('saliendo de passmode...')
            resul.append(tmp)
            continue
        # Pasar las lineas al resultado mientras passmode sea 1
        if passmode == 1:
            resul.append(tmp)
            continue
        else:
            # if _strip(tmp) != "" and _strip(tmp)[-1] == "\\" :
            if tmp.strip() != "" and tmp.strip()[-1] == "\\":
                lin = lin + tmp[:-1] + "\n"
                #print("lin por ahora: " + lin)
                continue
            else:
                lin += tmp
            #print("lin: " + lin)
            # if _find(_strip(lin),"#vsep") == 0 :
            if lin.strip().find("#vsep") == 0:
                #print("cambiando vsep!!!")
                sep = lin[len("#vsep"):]
                if sep.strip() == 'nl':
                    sep = '\n'
                elif sep == 'tab':
                    sep = '\t'
                elif sep == 'none':
                    sep = ''
                variadic_separator = sep
                #print("VSEP: "  + variadic_separator)
                lin = ""
                continue
            # if _find(_strip(lin),"#lsep") == 0 :
            if lin.strip().find("#lsep") == 0:
                #print("cambiando lsep!!!")
                sep = lin[len("#lsep"):]
                if sep.strip() == 'nl':
                    sep = '\n'
                elif sep == 'tab':
                    sep = '\t'
                elif sep == 'none':
                    sep = ''
                line_separator = sep
                #print("LSEP: "  + line_separator)
                lin = ""
                # continue
            # if _find(_strip(lin),"#ifdef") == 0 :
            if lin.strip().find("#ifdef") == 0:
                #parts = _split(_strip(lin)," ")
                parts = lin.strip().split(" ")
                if not len(parts) >= 2:
                    raise Exception(
                        """assertion error: 'len(parts) >= 2' is false""")
                if ignore_lin == False:
                    # if _strip(parts[1]) in defines_list :
                    if parts[1].strip() in define_list:
                        ignore_lin = False
                    else:
                        ignore_lin = True
                ifdef_counter += 1
                lin = ""
                #print("puesto ignore lin a %s"%ignore_lin)
                continue
            # if _find(_strip(lin),"#ifexp") == 0 :
            if lin.strip().find("#ifexp") == 0:
                #parts = _split(_strip(lin)," ")
                parts = lim.strip().split(" ")
                # print(defines)
                # print(defines.items())
                print([x for x in defines.values()])
                _names = {x[0]: x[1].value for x in defines.items()}
                # if not len(parts) >= 2:
                #   raise Exception("""assertion error: 'len(parts) >= 2' is false""")
                assert(len(parts) >= 2)
                if ignore_lin == False:
                    if bool( eval_if_expr(' '.join(parts[1:]).strip(), _names)) == True:
                        ignore_lin = False
                    else:
                        ignore_lin = True
                ifexp_counter += 1
                lin = ""
                #print("puesto ignore lin a %s"%ignore_lin)
                continue
            # if _find(_strip(lin),"#ifndef") == 0 :
            if lin.strip().find("#ifndef") == 0:
                #parts = _split(_strip(lin)," ")
                parts = lin.strip().split(" ")
                # if not len(parts) >= 2:
                #   raise Exception("""assertion error: 'len(parts) >= 2' is false""")
                assert(len(parts) >= 2)
                if ignore_lin == False:
                    # if not _strip(parts[1]) in defines_list :
                    if not parts[1].strip() in defines_list:
                        ignore_lin = False
                    else:
                        ignore_lin = True
                ifndef_counter += 1
                lin = ""
                continue
            # if _find(_strip(lin),"#endifn") == 0 : #Primero tiene que ir este o si no, siempre encuentra #endif
            # Primero tiene que ir este o si no, siempre encuentra #endif
            if lin.strip().find("#endifn") == 0:
                #print("ifndef_counter: " + str(ifndef_counter))
                #print("endifn_counter: " + str(endifn_counter))
                if ifndef_counter == 0 or endifn_counter > ifndef_counter:
                    raise Exception(
                        "Bridge Preprocessor Error: #endifn without #ifndef")
                endifn_counter -= 1
                ifndef_counter -= 1
                ignore_lin = False if ignore_lin == True else ignore_lin
                lin = ""
                continue
            # if _find(_strip(lin),"#endifexp") == 0 :
            if lin.strip().find("#endifexp") == 0:
                #print("ifdef_counter: " + str(ifdef_counter))
                #print("endif_counter: " + str(endif_counter))
                if ifexp_counter == 0 or endifexp_counter > ifexp_counter:
                    raise Exception(
                        "Bridge Preprocessor Error: #endifexp without #ifexp")
                endifexp_counter -= 1
                ifexp_counter -= 1
                ignore_lin = False if ignore_lin == True else ignore_lin
                lin = ""
                #print("puesto ignore lin a %s"%ignore_lin)
                continue
            # if _find(_strip(lin),"#endif") == 0 :
            if lin.strip().find("#endif") == 0:
                #print("ifdef_counter: " + str(ifdef_counter))
                #print("endif_counter: " + str(endif_counter))
                if ifdef_counter == 0 or endif_counter > ifdef_counter:
                    raise Exception(
                        "Bridge Preprocessor Error: #endif without #ifdef")
                endif_counter -= 1
                ifdef_counter -= 1
                ignore_lin = False if ignore_lin == True else ignore_lin
                lin = ""
                #print("puesto ignore lin a %s"%ignore_lin)
                continue

            # if _find(_strip(lin),"#define") == 0 :
            if lin.strip().find("#define") == 0:
                #print("lin en defines: " + lin)
                #parts = _split(_strip(lin)," ")
                parts = lin.strip().split(" ")
                #print('parts[2:]: %s'%parts[2:])
                if not len(parts) >= 2:  # ????
                    raise Exception(
                        """assertion error: 'len(parts) >= 2' is false""")
                name = None
                value = None
                args = None
                m = None
                #name = _strip(parts[1])
                name = parts[1].strip()
                if "(" in name:
                    #rest = _sublist(name,_index("(",name)+1,-1)
                    rest = name[name.index("("):-1]
                    #name = _sublist(name,0,_index("(",name))
                    name = name[0:name.index("(")]
                    #args = _split(rest,",") if "," in rest else [rest]
                    args = rest.split(',') if ',' in rest else [rest]
                    # Si el ultimo argumento es ... , entonces es una macro variadica
                    variadic = False
                    if "..." in args:
                        if args[-1] != "...":
                            raise Exception(
                                "Bridge Preprocessor error: macro %s is variadic but %s is not last argument" % (name, "..."))
                        else:
                            variadic = True
                    # Si el tercer argumento es foreach, entonces es una macro foreach
                    foreach = False
                    if len(parts) > 2 and parts[2] =="#foreach":
                        #print('encontrado foreach en parts[2]')
                        if variadic == False:
                            raise Exception(
                                "Bridge Preprocessor error: macro %s is #foreach macro but is not  variadic" % name)
                        else:
                            foreach = True
                            # parts=parts[1:]
                    #print("parts aqui: " + str(parts))
                    #print("FOREACH: " + str(foreach))
                    if foreach == False:
                        #value = _join(" ",list(itertools.chain(parts))[ 2: None])
                        value = " ".join(parts[2:])
                    else:
                        # foreach solo acepta ... como argumento
                        if args != ["..."]:
                            raise Exception(
                                "Bridge Preprocessor error: #foreach macro only accepts variadic arguments (...), given (%s)" % ','.join(args))
                        #value = _join(" ",list(itertools.chain(parts))[ 3: None])
                        value = parts[3:].join(" ")
                    m = PreProcMacro(name, value, args, variadic,foreach)
                    # m.toString()
                else:
                    #m = PreProcMacro(name,value=_join(" ",parts[2:]),args=[],va_args=False,foreach=False)
                    m = PreProcMacro(name, value=" ".join(parts[2:]), args=[], va_args=False, foreach=False)
                    # print(m.toString())
                defines_list.append(name)
                defines[name] = m
                lin = ""
                continue
            # if _find(_strip(lin),"#undef") == 0 :
            if lin.strip().find("#undef") == 0:
                if ignore_lin == False:
                    # parts = _split(_strip(lin)," "
                    parts = lin.strip().split(" ")
                    if not len(parts) >= 2:
                        raise Exception(
                            """assertion error: 'len(parts) >= 2' is false""")
                    # if _strip(parts[1]) in defines.keys() :
                    if parts[1].strip() in defines.keys():
                        #del defines[_strip(parts[1])]
                        del defines[parts[1].strip()]
                        #del defines_list[_index(_strip(parts[1]),defines_list)]
                        del defines_list[defines_list.index(parts[1].strip())]
                lin = ""
                continue
            # print(defines)
            if ignore_lin == False:
                # ---------------------------------------------------------------------------------
                # Buscar los strings uni y multilinea en la linea--------------------------------------------
                _stringpos = [[x.start(), x.end()] for x in re.finditer(r"[r|f]?\"\"\"[\s\S]*?\"\"\"|[r|f]?\"[^\"\\]*(?:\\.[^\"\\]*)*\"", lin)]
                # -------------------------------------------------------------------------------------------
                # Comentarios de una linea----------------------------------------------------
                # com_st=_find(_strip(lin),"#")
                com_st = lin.strip().find("#")
                #print("com_st: " + str(com_st));
                com_rest = ""
                if com_st == 0:
                    resul.append(lin)
                    lin = ""
                    continue
                elif com_st > 0:
                    com_rest = lin[com_st:]
                    lin = lin[:com_st]
                # ----------------------------------------------------------------------------
                # Comentarios multilinea------------------------------------------------------
                # multipos=_find(lin,"/*")
                multipos = lin.find("/*")
                # Si es principio de comentario multiple
                #print("multipos para comment: " + str(multipos))
                # Si el principio del comentario esta en un string, ignoramos la linea---------------
                # print(_stringpos)
                for elem in _stringpos:
                    if elem[0] <= multipos and elem[1] >= multipos:
                        multipos = -1
                        #print("puesto multipos a -1")
                        break
                # ------------------------------------------------------------------------------------
                #print("multipos: %s"%multipos)
                #print("multiline_c: %s"%multiline_c)
                if multipos != -1:
                    multiline_c = True
                    # Si es principio de linea, cogerla y poner multi_c a true
                    if multipos == 0:
                        resul.append(lin)
                        # Si es una sola linea, terminamos
                        # if _strip(lin)[-2:]=="*/":
                        if lin.strip()[-2:] == "*/":
                            multiline_c = False
                        lin = ""
                        continue
                    # Si no empieza al principio, trocear la linea y coger la parte de comentario
                    else:
                        # Comentario multiple de una linea que comienza a la mitad y termina
                        # if _strip(lin)[-2:]=="*/":
                        if lin.strip()[-2:] == "*/":
                            com_rest = lin[multipos:]
                            lin = lin[:multipos]
                            multiline_c = False
                        else:  # ??esto altera el texto
                            # multiend=_find(lin,"*/")
                            multiend = lin.find("*/")
                            #print("multiend: " + str(multiend))
                            precom = lin[:multipos]
                            com = lin[multipos:multiend+2]
                            postcom = lin[multiend+2:]
                            com_rest = com
                            # lin=lin[:multipos]
                            lin = precom + postcom
                            #print("com_rest: " + com_rest)
                            #print("lin: " + lin)
                            multiline_c = False
                # Si no, ver si es final de comentario y terminar,o coger la linea y seguir
                else:
                    if multiline_c:
                        # multiend=_find(_strip(lin),"*/")
                        multiend = lin.strip().find("*/")
                        #print("multiend para comment: " + str(multiend))
                        if multiend != -1:
                            if multiend == 0:
                                resul.append(lin)
                                lin = ""
                                multiline_c = False
                                continue
                            else:
                                #print("por el else de comment")
                                str_pre = lin[:multiend]
                                lin = lin[multiend:]
                                multiline_c = False
                        else:
                            resul.append(lin)
                            lin = ""
                            continue
                # Strings multilinea---------------------------------------------------------------
                indices = [match.start()
                           for match in re.finditer("\"\"\"", lin)]
                multspos = indices[-1] if indices != [] else -1
                #print("indices: " + str(indices))
                #print("indices%2 " + str(len(indices)%2))
                # Si es principio de string multiple (comprobar que no sea una linea sola)
                if multspos != -1 and len(indices)%2 !=0 and multstring==False:
                    multstring = True
                    # Si es principio de linea, cogerla y poner multistring a true
                    if multspos == 0:
                        #print("entrando por Principio de linea")
                        resul.append(lin)
                        lin = ""
                        continue
                    # Si no empieza al principio, trocear la linea y coger la parte de comentario
                    else:
                        #print("entrando por el ELSE")
                        com_rest = lin[multspos:]
                        lin = lin[:multspos]
                        #print("str_pre1: " + com_rest)
                        #print("lin1: " + lin)
                # Si no, ver si es final de string multiple y terminar,o coger la linea y seguir
                else:
                    if multstring:
                        #print("entrando por multstring TRUE")
                        # multsend=_find(_strip(lin),"\"\"\"")
                        multsend = lin.strip().find("\"\"\"")
                        if multsend != -1:
                            if multsend == 0:
                                resul.append(lin)
                                lin = ""
                                multstring = False
                                #print("==>puesto multstring a false1!!!")
                                continue
                            else:
                                str_pre = lin[:multsend]
                                lin = lin[multsend:]
                                multstring = False
                                #print("==>puesto multstring a false2!!!")
                                #print("str_pre2: " + str_pre)
                                #print("lin2: " + lin)
                        else:
                            resul.append(lin)
                            lin = ""
                            continue
            # print(_stringpos)
            #print("lin aqui: " + lin)
            #print ("DEFINES LIST: %s"%defines_list)
            # print(defines)
            for item in defines_list:
                is_variadic_macro = defines[item].va_args
                is_foreach_macro = defines[item].foreach
                if defines[item].args == []:
                    m = re.search(item, lin)
                    if m:
                        if m and (m.end()-m.start()) == len(item):
                            # Cambio para proteger los strings de una linea
                            substitute = True
                            for elem in _stringpos:
                                if m.start() >= elem[0] and m.start() <= elem[1]:
                                    substitute = False
                            if substitute:
                                tmp = defines[item].value
                                print('TMP: %s' % repr(tmp))
                                if tmp not in ['', None]:
                                    if "##" in tmp:
                                        # tmp = _join("",list(map(_strip,list(itertools.chain(_split(tmp,"##"))))))
                                        tmp = "".join([x.strip()
                                                       for x in tmp.split("##")])
                                    if tmp[0:len("#foreach")] == "#foreach":
                                        raise Exception(
                                            "Bridge Preprocessor error: cannot use #foreach in not variadic macro")
                                    if tmp[0] == "#":
                                        #tmp = "\"" + _sublist(tmp,1) + "\""
                                        tmp = "\"" + tmp[1:] + "\""
                                    lin = re.sub(item, tmp, lin)
                else:
                    # if _strip(lin) == "" :
                    if lin.strip() == "":
                        continue
                    pos = -2
                    # El while es necesario para que sustituya todas las ocurrencias de la macro
                    while pos != -1:
                        #print("lin al entrar al while: " + lin)
                        #pos = _find(lin,item+"(")
                        pos = lin.find(item + "(")
                        initval = pos
                        args = []
                        buff = ""
                        if pos != -1:
                            while lin[pos] != "(":
                                pos += 1
                            pos += 1
                            openpars = 1
                            closedpars = 0
                            openbracks = 0
                            closedbracks = 0
                            opensquares = 0
                            closedsquares = 0
                            quotes = 0
                            while pos < len(lin):
                                if openpars == 0:
                                    break
                                if lin[pos] == "(":
                                    openpars += 1
                                if lin[pos] == ")":
                                    closedpars += 1
                                    openpars -= 1
                                if lin[pos] == "[":
                                    openbracks += 1
                                if lin[pos] == "]":
                                    closedbracks += 1
                                    openbracks -= 1
                                if lin[pos] == "{":
                                    opensquares += 1
                                if lin[pos] == "}":
                                    closedsquares += 1
                                    opensquares -= 1
                                if lin[pos] == "\"":
                                    if quotes == 0:
                                        quotes = 1
                                    else:
                                        quotes = 0
                                if lin[pos] == "," and openpars == 1 and openbracks == 0 and opensquares == 0 and quotes == 0:
                                    args.append(buff)
                                    buff = ""
                                else:
                                    buff = buff+lin[pos]
                                pos += 1
                            if buff != "":
                                # args.append(_sublist(buff,0,-1))
                                args.append(buff[0:-1])
                            #print("Argumentos encontrados: " + str(args))
                            if len(defines[item].args) != len(args) and not is_variadic_macro:
                                raise Exception("Bridge Preprocessor error: macro %s has %s arguments. Found %s" % (item, len(defines[item].args), len(args)))
                            newval = defines[item].value
                            last_val = 0 if is_variadic_macro == False else 1
                            if is_foreach_macro:
                                #print("procesando macro foreach: " + item)
                                #print("args en foreach: " + str(args))
                                newval = ""
                                for _it in args:
                                    #tmp = _replace(defines[item].value,"...",_it)
                                    tmp = defines[item].value.replace(
                                        "...", _it)
                                    if "##" in tmp:
                                        # tmp = _join("",list(map(_strip,list(itertools.chain(_split(tmp,"##"))))))
                                        tmp = "".join([x.strip()
                                                       for x in tmp.split("##")])
                                    if tmp[0] == "#":
                                        #tmp = "\"" + _sublist(tmp,1) + "\""
                                        tmp = "\"" + tmp[1:] + "\""
                                    # newval+=_replace(defines[item].value,"...",_it)
                                    newval += tmp + line_separator
                                #print("NEWVAL en foreach: " + newval)
                            else:
                                i = 0
                                #print('lin aqui: %s'%lin)
                                #print('defines: %s'% defines)
                                #print('newval: %s'%newval)
                                if "##" in newval:
                                    newval = _join("", list(map(_strip, list(itertools.chain(_split(newval, "##"))))))
                                if newval[0] == "#":
                                    newval = "\"" + _sublist(newval, 1) + "\""

                                while i < len(defines[item].args)-last_val:
                                    #newval = _replace(newval,defines[item].args[i],args[i])
                                    newval = newval.replace(
                                        defines[item].args[i], args[i])
                                    i += 1
                                newval += line_separator
                            # Si es variadica y no foreach, reemplazar ... por todos los argumentos despues del ultimo unidos por comas
                            if is_variadic_macro and not is_foreach_macro:
                                #print("VSEP aqui: " + variadic_separator)
                                #newval= _replace(newval,"...",_join(variadic_separator,args[i:]))
                                newval = newval.replace(
                                    "...", args[i:].join(variadic_separator))
                                #print("NEWVAL: " + newval)
                            #lin = _replace(lin,item + "(" + _join(",",args) + ")",newval)
                            lin = lin.replace(
                                #item + "(" + _join(",", args) + ")", newval)
                                item + "(" + ",".join(args) + ")", newval)
                            #print("lin al final del while: " + lin)
            if ignore_lin == False:
                resul.append(str_pre + lin + com_rest)
                str_pre = ""
                com_rest = ""
            lin = ""
    if ifdef_counter != 0:
        raise Exception(
            "Preprocessor Error: not all #ifdef are closed by an #endif")
    if ifndef_counter != 0:
        raise Exception(
            "Preprocessor Error: not all #ifndef are closed by an #endifn")
    if ifexp_counter != 0:
        raise Exception(
            "Preprocessor Error: not all #ifexp are closed by an #endifexp")
    # return _join("\n",resul)
    # Cambio para reprocesar si ha habido #includes
    if recursive_mode == 0:
        # return _join("\n",resul)
        return "\n".join(resul)
    else:
        # return preprocessor(_join("\n",resul))
        return preprocessor("\n".join(resul))


if __name__ == '__main__':
    print(preprocessor(open("preprocessor_test.bridge", "r").read()))
