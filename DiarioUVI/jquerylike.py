import bs4
import sys

def _flat(lst):
    flatted=[]
    for el in lst:
        if type(el)==list or isinstance(el,list):
            for item in _flat(el):
                flatted.append(item)
        else:
            flatted.append(el)
    return flatted

def HTML(selector,source):
    parser= "lxml" if "lxml" in sys.modules else "html.parser"
    #print("html parser: %s" %parser)
    def _parseSelector(sel):
        parts= sel.split(' ')
        #print("parts: %s"%parts)
        return parts
    parts= _parseSelector(selector)
    html=bs4.BeautifulSoup(source,parser)
    if parts==[]:
        return []
    resul=[]
    resul= list(filter(lambda x: x!=[] ,_flat(html.findAll(parts[0]))))
    for part in parts[1:]:
        resul= list(filter(lambda x: x!=[],_flat([x.findAll(part) for x in resul])))
    return resul


html_doc = """
 <html><head><title>The Dormouse's story</title></head>
 <p class="title"><b>The Dormouse's story</b></p>
 <p class="story">Once upon a time there were three little sisters; and their names were
 <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
 <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
 <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
 and they lived at the bottom of a well.</p>
 <p class="story">...</p>
 """

print(HTML("p a", html_doc))