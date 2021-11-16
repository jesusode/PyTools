#Funciones de utilidad
import urllib
import urllib.request

def cleanupSpace(s: str):
    if s[-1]==',': s = s[:-1]
    s = s.strip().strip('\n')
    if s[-1]==',': s = s[:-1]
    return s

def openURL(url : str):
    return urllib.request.urlopen(url) 



htmltemplate2 = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>{0}</title>
</head>
<body>
<h3>{0}</h3>
{1}
</body>
</html>"""

def multiListToTable (seq):
    tablestr = "<table border='1'>\n"
    for item in seq: 
        tablestr = tablestr + "<tr>"
        if type(item) == list : 
            tablestr = tablestr +  "<td>" + str(item[0]) + "</td>\n"
            if len(item) > 1 and type(item[1]) == list : 
                tablestr = tablestr + "<td>" + multiListToTable(item[1:]) + "</td>\n"
            else:
                tablestr = tablestr + "<td>" + str(item[1]) + "</td>\n"
        else:
            tablestr = tablestr +  "<td>" + item + "</td>\n"
        tablestr = tablestr + "</tr>"
    tablestr = tablestr + "\n</table>"
    return tablestr


def multiListToUL (seq):
    tablestr = "<ul>\n"
    for item in seq: 
        if type(item) == list : 
            tablestr = tablestr + multiListToUL(item) + "\n"
        else:
            tablestr = tablestr +  "<li>" + item + "</li>\n"
    tablestr = tablestr + "\n</ul>"
    return tablestr


if __name__ == '__main__':
    l = ["uno","dos",["tres","cuatro",["cinco",["seis","siete"]]],"ocho"]
    print(multiListToUL(l))



