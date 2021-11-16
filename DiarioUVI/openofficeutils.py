"""
Clase de utilidad para leer archivos .ods de OpenOffice.
Permite obtener el contenido de una hoja de calculo por nombre
en forme de lista de listas, o bien obtener una celda del mismo.
Es un envoltorio ligero sobre ODSReader.

NOTA: Aparentemente hay un fallo en odfpy: En opocument.py, load
asume que al cargar, firstChild es el nodo correcto de tipo Element para 
un spreadsheet. Es posible que haya nodos vacios tipo texto, con lo cual
si coge el primero, cargaria un Text en vez de un Table, que es lo que 
deberia hacer. Se ha corregido para que busque el primer nodo que sea de
tipo Element.
Conviene recordar que Element hereda de xml.dom.Node
"""

from enum import Enum

from bridge_odswriter import *

from ODSReader import ODSReader 
from StringBuffer import StringBuffer

import odf
import teletype
#import odf.opocument

import pprint

elements={
        "span": odf.text.Span,
        "P": odf.text.P,
        "H": odf.text.H,
        "A": odf.text.A,
        "tab": odf.text.Tab,
        "frame" : odf.draw.Frame,
        "image" : odf.draw.Image,
        "list" : odf.text.List,
        "li" : odf.text.ListItem,
        "textprops" : odf.style.TextProperties,
        "paraprops" : odf.style.ParagraphProperties,
        "pageprops" : odf.style.PageLayoutProperties,
        "pagelayout" : odf.style.PageLayout,
        "textbox" : odf.draw.TextBox
}



class BridgeODSReader:
    def __init__(self,odsfilepath):
        self.loadODS(odsfilepath)
    
    def loadODS(self,path):
        self.__ods= ODSReader(path,clonespannedcolumns=True)
    
    def getSheet(self,name):
        return self.__ods.getSheet(name)
    
    def getSheetNames(self):
        return  self.__ods.SHEETS.keys()
    
    def hasSheet(self,name):
        return name in self.__ods.SHEETS.keys()
    
    def getCell(self,sheet,row,col):
        return self.__ods.getSheet(sheet)[row][col]
    
    def getRow(self,sheet,row):
        return self.__ods.getSheet(sheet)[row]
    
    def getCol(self,sheet,col):
        cl = []
        for row in self.__ods.getSheet(sheet):
            cl.append(row[int(col)])
        return cl
    

class BridgeODTReader:

    def __init__(self,odsfilepath):
        self.loadODT(odsfilepath)
    
    def loadODT(self,path):
        self.__odt= odf.opocument.load(path)
    
    def getDocument(self):
        return self.__odt
    
    def getText(self):
        #text=""
        text= StringBuffer()
        text.setEncoding("latin-1")
        for item in self.__odt.text.childNodes:
            #text= text + teletype.extractText(item) + "\n"
            text(teletype.extractText(item),"\n")
        #return text
        return text()
    
    def getHeaders(self):
        headers=[]
        for item in self.__odt.text.getElementsByType(odf.text.H):
            headers.append(teletype.extractText(item))
        return headers
    
    def getParagrapahs(self):
        pars=[]
        for item in self.__odt.text.getElementsByType(odf.text.P):
            pars.append(teletype.extractText(item))
        return pars
    
    def getLinks(self):
        resul=[]
        for item in self.__odt.text.getElementsByType(odf.text.A):
            resul.append([teletype.extractText(item),item.getAttribute("href")])
        return resul
    
    def getTables(self):
        tables=[]
        print(self.__odt.text.getElementsByType(odf.table.Table))
        for item in self.__odt.text.getElementsByType(odf.table.Table):
            trows=[]
            for elem in item.getElementsByType(odf.table.TableRow):
                row=[]
                for cell in elem.getElementsByType(odf.table.TableCell):
                    row.append(teletype.extractText(cell))
                trows.append(row)
            
            tables.append(trows)
        return tables
    

class BridgeODT:

    def __init__(self):
        self.__odt= odf.opocument.OpenDocumentText()
        print(self.__odt)
    

    def getODT(self):
        return self.__odt
    

    def registerStyle(self,style):
        #assert isinstance(style,odf.style.Style)
        self.__odt.styles.addElement(style)
    

    def addParagraph(self,text,style=None):
        if style!=None :
            p=  odf.text.P(stylename=style)
        else:
            p=  odf.text.P
        
        teletype.addTextToElement(p,text)
        self.__odt.text.addElement(p)
        return p
    

    def addSpan(self,element,text,style=None):
        if style!=None :
            s=  odf.text.Span(stylename=style)
        else:
            s=  odf.text.Span
        teletype.addTextToElement(s,text)
        element.addElement(s)
        return s
    

    def addTab(self,element):
        element.addElement( odf.text.Tab)
        return None
    

    def addHeader(self,text,style=None,level=1):
        if style!=None :
            h=  odf.text.H(stylename=style,outlinelevel=level)
        else:
            h=  odf.text.H(outlinelevel=level)
        
        teletype.addTextToElement(h,text)
        self.__odt.text.addElement(h)
        return h
    

    def addLink(self,element,text,href,style=None):
        if style!=None :
            a=  odf.text.A(stylename=style,href=href)
        else:
            a=  odf.text.A(href=href)
        
        teletype.addTextToElement(a,text)
        element.addElement(a)
        return a
    

    def addBR(self):
        self.addParagraph("\n",None)
    

    #Estructura de celda: [texto o elemento,estilo]
    def addTable(self,coldescriptions,cellscontents,units="cm"):
        assert len(cellscontents[0])==len(coldescriptions)
        counter=0
        table =  odf.table.Table
        #1.-Crear un estilo para cada columna
        for item in coldescriptions:
            colst =  odf.style.Style(name="colwidth"+str(counter), family="table-column")
            colst.addElement( odf.style.TableColumnProperties(columnwidth= str(item[1]) + units))
            self.__odt.automaticstyles.addElement(colst) 
            table.addElement( odf.table.TableColumn(stylename=colst))
        
        for row in cellscontents:
            tr=  odf.table.TableRow
            table.addElement(tr)
            for cell in row:
                #print("procesando cell: " + _tostring(cell))
                c=  odf.table.TableCell
                tr.addElement(c)
                if type(cell[0])==str :
                    if cell[1]!=None :
                        c.addElement( odf.text.P(stylename=cell[1],text=cell[0]))
                    else:
                        c.addElement( odf.text.P(text=cell[0]))
                else:
                    c.addElement(cell[0])
        self.__odt.text.addElement(table)
        return table
    
    #Gestionar estilos y bullets
    def addList(self,items,parent=None,style=None):
        lst=  odf.text.List
        for elem in items:
            li= odf.text.ListItem
            li.addElement( odf.text.P(text=elem))
            lst.addElement(li)
        if parent==None :
            self.__odt.text.addElement(lst)
        else:
            parent.addElement(lst)
        return lst
    

    #Pensarse usar x e y para situar la imagen en las coordenadas especificadas
    def addImage(self,imgpath,width,height,anchor,style=None,x=None,y=None):
        p =  odf.text.P
        self.__odt.text.addElement(p)
        # Create the frame.
        #df = odf.draw.Frame(width="476pt", height="404pt", anchortype="paragraph")
        #df =  odf.draw.Frame(width=width, height=height, anchortype="paragraph")
        if x==None and y==None :
            df =  odf.draw.Frame(width=width, height=height, anchortype=anchor)
        else:
            df =  odf.draw.Frame(width=width, height=height,x=x,y=y, anchortype=anchor)
        
        href = self.__odt.addPicture(imgpath)
        df.addElement( odf.draw.Image(href=href))
        p.addElement(df)
        return df
    

    def addTextFrame(self,width,height,anchor,text,style=None,x=None,y=None):
        p =  odf.text.P
        self.__odt.text.addElement(p)
        if x==None and y==None :
            df =  odf.draw.Frame(width=width, height=height, anchortype=anchor)
        else:
            df =  odf.draw.Frame(width=width, height=height,x=x,y=y, anchortype=anchor)
        tb=  odf.draw.TextBox
        tb.addElement( odf.text.P(text=text))
        df.addElement(tb)
        p.addElement(df)
        return df
    
    def save(self,path):
        assert self.__odt!=None
        self.__odt.save(path, True)
    

def odsSplit(srcods,sheetlist,newods):
    odsr= BridgeODSReader(srcods)
    newods= createOds(newods)
    for item in sheetlist:
        s= createSheet(newods,item)
        rows=odsr.getSheet(item)
        for elem in rows:
            odsWrite(s,elem)
    odsClose(newods)


def multiOdsSplit(srclist,sheetlist,newods):
    newods= createOds(newods)
    for arch in srclist:
        odsr= BridgeODSReader(arch)
        for item in sheetlist:
            if odsr.hasSheet(item) :
                s= createSheet(newods,item)
                rows=odsr.getSheet(item)
                for elem in rows:
                    odsWrite(s,elem)
    odsClose(newods)


class stylekind(Enum): 
    parstyle = 1
    pagestyle = 2
    textstyle = 3
    liststyle = 4

def styleFactory(name,family,styleitems=[]):
    st= odf.style.Style(name=name,family=family)
    for item in styleitems:
        st.addElement(item)
    return st


def styleItemFactory(kind,attributes,parent=None):
    item=None
    if kind == stylekind.parstyle:
        item =  odf.style.ParagraphProperties(attributes=attributes)
    elif kind == stylekind.textstyle:
        item =  odf.style.TextProperties(attributes=attributes)
    elif kind == stylekind.pagestyle:
        item =  odf.style.TextProperties(attributes=attributes)
    else: 
        item =  odf.style.TextProperties(attributes=attributes)
    if parent!= None :
        parent.addElement(item)
    return item


def addElementByName(name,parent,**attrs):
    global elements
    el= elements[name](**attrs)
    parent.addElement(el)
    return el

