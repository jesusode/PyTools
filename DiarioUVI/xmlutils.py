#Utilidades xml-html
import sys
import bs4
from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup
import lxml
import html

def getxmldoc(string,encoding='utf-8'):
    return lxml.etree.fromstring(bytes(string,encoding))

def xpath(element_source,xpath_expression,encoding='utf-8'):
    '''
    xpath
    -----
    
    Obtiene el resultado de aplicar una expresion XPATH
    a un elemento DOM o un string.
    '''
    root=None
    print(type(element_source))
    if type(element_source) in [str,bytes]:
        #element_source puede ser bytes!!
        if type(element_source) == bytes:
            element_source = str(element_source,encoding)
        root = lxml.etree.fromstring(bytes(element_source,encoding))
    else:
        root= element_source
    #print(root)
    return root.xpath(xpath_expression)

def insertInXpath(doc,xpath,elem):
    root=None
    if type(doc)==str:
        root = lxml.etree.fromstring(doc)
    else:
        root= doc
    root=lxml.etree.ElementTree(root)
    for item in root.xpath(xpath):
        if type(elem)==str:
            el = lxml.etree.fromstring(elem)
        else:
            el= elem
        item.append(el)
    return root

def toxml(lxmlelem,encoding="utf-8",errors="replace"):
    return html.unescape(lxml.etree.tostring(lxmlelem,pretty_print=True).decode(encoding,errors))


def applyXSLT(_xml,xsl):
    dom = lxml.etree.XML(_xml)
    xslt = lxml.etree.XML(xsl)
    transform = lxml.etree.XSLT(xslt)
    newdom = transform(dom)
    return lxml.etree.tostring(newdom, pretty_print=True)


def flat(lst):
    flatted=[]
    #print("lst in _flat: %s"%repr(lst))
    for el in lst:
        #print ("type(el) in flat: %s"%type(el))
        if type(el)==list or isinstance(el,list):
            for item in flat(el):
                flatted.append(item)
        else:
            flatted.append(el)
    return flatted


def html(selector,source):
    #Buscar el mejor parser disponible
    parser= "lxml" if "lxml" in sys.modules else "html.parser"
    #print("html parser: %s" %parser)
    parts= selector.strip().split(',')
    #print("parts: %s"%parts)
    html=bs4.BeautifulSoup(source,parser)
    #print('html: %s'%html)
    if parts==[]:
        return []
    resul=[]
    #Cada parte puede ser un solo elemento(la mayoria) o varios(p div a)
    for part in parts:
        #print("procesando part: %s"%part)
        #print("resul aqui: %s"%resul)
        #print(' ' in part)
        if not ' ' in part: #Procesar un item no jerarquico
            #print("por el if")
            resul.append(list(filter(lambda x: x!=[] ,flat(html.findAll(part)))))
            #print("resul aqui: %s"%resul)
        else:
            #print("por el else")
            childs=part.split(' ')
            #print("childs: %s"%childs)
            resul=list(filter(lambda x:x!=[],flat(html.findAll(childs[0]))))
            #print("resul aqui: %s"%resul)
            for item in childs[1:]:
                #print("procesando item: %s"%item)
                resul= list(filter(lambda x: x!=[],flat([x.findAll(item) for x in resul])))
                #print("resul en el for: %s"%resul)
            #pprint.pprint(resul)
            #pprint.pprint(_flat(resul))
    return flat(resul)
    #return resul
