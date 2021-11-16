#OOUtils


from enum import Enum,unique
import odswriter
from ODSReader import ODSReader
import odf


def listToOds ( fname, headers, _list, sheet=""):
    ods = None
    sht = None
    active = None
    ods = odswriter.writer(open(fname,"wb"))
    active = ods
    if sheet != "" : 
        sht = ods.new_sheet(sheet)
        active = sht
    if headers != [] : 
        active.writerow(headers)
    for item in _list: 
        active.writerow(item)
    ods.close()

def createOds ( name):
    return odswriter.writer(open(name,"wb"))

def createSheet ( ods, sname):
    return ods.new_sheet(sname)

def odsWrite ( ods_or_sheet, row, multiple=False):

    if multiple == True : 
        ods_or_sheet.writerows(row)
    else:
        ods_or_sheet.writerow(row)
    return 1

def odsWriteFormula ( ods, formula):
    ods.writerow([odswriter.Formula(formula)])
    return 1

def odsClose ( ods):
    ods.close()
    return 1

elements = {"span":odf.text.Span,
            "P":odf.text.P,
            "H":odf.text.H,
            "A":odf.text.A,
            "tab":odf.text.Tab,
            "frame":odf.draw.Frame,
            "image":odf.draw.Image,
            "list":odf.text.List,
            "li":odf.text.ListItem,
            "textprops":odf.style.TextProperties,
            "paraprops":odf.style.ParagraphProperties,
            "pageprops":odf.style.PageLayoutProperties,
            "pagelayout":odf.style.PageLayout,
            "textbox":odf.draw.TextBox}


class ODSReader():
    def __init__ ( self, odsfilepath):
        self.loadODS(odsfilepath)

    def loadODS ( self, path):
        self.__ods = ODSReader(path,clonespannedcolumns=True)

    def getSheet ( self, name):
        return self.__ods.getSheet(name)

    def getSheetNames ( self):
        return self.__ods.SHEETS.keys()

    def hasSheet ( self, name):
        return name in self.__ods.SHEETS.keys()

    def getCell ( self, sheet, row, col):
        return self.__ods.getSheet(sheet)[row][col]

    def getRow ( self, sheet, row):
        return self.__ods.getSheet(sheet)[row]

    def getCol ( self, sheet, col):
        cl = []
        for row in self.__ods.getSheet(sheet): 
            cl.append(row[int(col)])
        return cl

class ODTReader():

    def __init__ ( self, odsfilepath):
        self.loadODT(odsfilepath)

    def loadODT ( self, path):
        self.__odt = odf.opendocument.load(path)

    def getDocument ( self):
        return self.__odt

    def getText ( self):
        text = StringBuffer()
        text.setEncoding("latin-1")
        for item in doc.text.childNodes: 
            text(teletype.extractText(item),"\n")
        return text()

    def getHeaders ( self):
        headers = []
        for item in doc.text.getElementsByType(odf.text.H): 
            headers.append(teletype.extractText(item))
        return headers

    def getParagrapahs ( self):
        pars = []
        for item in doc.text.getElementsByType(odf.text.P): 
            pars.append(teletype.extractText(item))
        return pars

    def getLinks ( self):
        resul = []
        for item in doc.text.getElementsByType(odf.text.A): 
            resul.append([teletype.extractText(item),item.getAttribute("href")])
        return resul

    def getTables ( self):
        tables = []
        for item in doc.text.getElementsByType(odf.table.Table): 
            trows = []
            for elem in item.getElementsByType(odf.table.TableRow): 
                row = []
                for cell in elem.getElementsByType(odf.table.TableCell): 
                    row.append(teletype.extractText(cell))
                trows.append(row)
            tables.append(trows)
        return tables

class ODT():

    def __init__ ( self):
        self.__odt = odf.opendocument.OpenDocumentText()

    def getODT ( self):
        return self.__odt

    def registerStyle ( self, style):
        self.__odt.styles.addElement(style)

    def addParagraph ( self, text, style=None):
        p = None
        if style != None : 
            p = odf.text.P(stylename=style)
        else:
            p = odf.text.P()
        teletype.addTextToElement(p,text)
        self.__odt.text.addElement(p)
        return p

    def addSpan ( self, element, text, style=None):
        s = None
        if style != None : 
            s = odf.text.Span(stylename=style)
        else:
            s = odf.text.Span()
        teletype.addTextToElement(s,text)
        element.addElement(s)
        return s

    def addTab ( self, element):
        element.addElement(odf.text.Tab())
        return None

    def addHeader ( self, text, style=None, level=1):
        h = None
        if style != None : 
            h = odf.text.H(stylename=style,outlinelevel=level)
        else:
            h = odf.text.H(outlinelevel=level)
        teletype.addTextToElement(h,text)
        self.__odt.text.addElement(h)
        return h

    def addLink ( self, element, text, href, style=None):
        a = None
        if style != None : 
            a = odf.text.A(stylename=style,href=href)
        else:
            a = odf.text.A(href=href)
        teletype.addTextToElement(a,text)
        element.addElement(a)
        return a

    def addBR ( self):
        self.addParagraph("\n",None)

    def addTable ( self, coldescriptions, cellscontents, units="cm"):
        if not len(cellscontents[0]) == len(coldescriptions):
            raise Exception("""assertion error: 'len(cellscontents[0]) == len(coldescriptions)' is false""")
        counter = 0
        table = odf.table.Table()
        for item in coldescriptions: 
            colst = odf.style.Style(name=python_runtime.doAddition("colwidth",_tostring(counter)),family="table-column")
            colst.addElement(odf.style.TableColumnProperties(columnwidth=python_runtime.doAddition(_tostring(item[1]),units)))
            self.__odt.automaticstyles.addElement(colst)
            table.addElement(odf.table.TableColumn(stylename=colst))
        for row in cellscontents: 
            tr = odf.table.TableRow()
            table.addElement(tr)
            for cell in row: 
                c = odf.table.TableCell()
                tr.addElement(c)
                if type(cell[0]) == str : 
                    if cell[1] != None : 
                        c.addElement(odf.text.P(stylename=cell[1],text=cell[0]))
                    else:
                        c.addElement(odf.text.P(text=cell[0]))
                else:
                    c.addElement(cell[0])
        self.__odt.text.addElement(table)
        return table

    def addList ( self, items, parent=None, style=None):
        lst = odf.text.List()
        for elem in items: 
            li = odf.text.ListItem()
            li.addElement(odf.text.P(text=elem))
            lst.addElement(li)
        if parent == None : 
            self.__odt.text.addElement(lst)
        else:
            parent.addElement(lst)
        return lst

    def addImage ( self, imgpath, width, height, anchor, style=None, x=None, y=None):
        p = odf.text.P()
        self.__odt.text.addElement(p)
        if x == None and y == None : 
            df = odf.draw.Frame(width=width,height=height,anchortype=anchor)
        else:
            df = odf.draw.Frame(width=width,height=height,x=x,y=y,anchortype=anchor)
        href = self.__odt.addPicture(imgpath)
        df.addElement(odf.draw.Image(href=href))
        p.addElement(df)
        return df

    def addTextFrame ( self, width, height, anchor, text, style=None, x=None, y=None):
        p = odf.text.P()
        self.__odt.text.addElement(p)
        if x == None and y == None : 
            df = odf.draw.Frame(width=width,height=height,anchortype=anchor)
        else:
            df = odf.draw.Frame(width=width,height=height,x=x,y=y,anchortype=anchor)
        tb = odf.draw.TextBox()
        tb.addElement(odf.text.P(text=text))
        df.addElement(tb)
        p.addElement(df)
        return df

    def save ( self, path):
        if not self.__odt != None:
            raise Exception("""assertion error: 'self.__odt != None' is false""")
        self.__odt.save(path,True)




def odsSplit ( srcods, sheetlist, newods):
    odsr = ODSReader(srcods)
    newods = createOds(newods)
    for item in sheetlist: 
        s = createSheet(newods,item)
        rows = odsr.getSheet(item)
        for elem in rows: 
            odsWrite(s,elem)
    odsClose(newods)

def multiOdsSplit ( srclist, sheetlist, newods):
    newods = createOds(newods)
    for arch in srclist: 
        odsr = ODSReader(arch)
        for item in sheetlist: 
            if odsr.hasSheet(item) : 
                s = createSheet(newods,item)
                rows = odsr.getSheet(item)
                for elem in rows: 
                    odsWrite(s,elem)
    odsClose(newods)

@unique
class stylekind (Enum):
    parstyle=0
    pagestyle=1
    textstyle=2
    liststyle=3

def styleFactory ( name, family, styleitems=[]):
    st = odf.style.Style(name=name,family=family)
    for item in styleitems: 
        st.addElement(item)
    return st

def styleItemFactory ( kind, attributes, parent=None):
    item = None
    if kind ==  stylekind.parstyle:
        item = odf.style.ParagraphProperties(attributes=attributes)
    elif kind ==  stylekind.textstyle:
        item = odf.style.TextProperties(attributes=attributes)
    elif kind ==  stylekind.pagestyle:
        item = odf.style.TextProperties(attributes=attributes)
    else:
        item = odf.style.TextProperties(attributes=attributes)
    if parent != None : 
        parent.addElement(item)
    return item

def addElementByName ( name, parent, **attrs):
    global elements
    el = elements[name](**attrs)
    parent.addElement(el)
    return el
