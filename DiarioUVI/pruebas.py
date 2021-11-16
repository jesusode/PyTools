#Pruebas de CSVTransformer


import streams
import streams.CSVFileIterator
from streams.CSVFileIterator import CSVFileIterator
from CSVTransformer import *
import pprint
import time
import bs4
import requests
import urllib
import pypyodbc
import xmlutils
import pprint
import time
import datetime

import consultas_ol
import json

import utilidades

nhc = '1641911'


import datetime
def csv_guess_types(csv : List[str],types_to_try : List[Type] = [int,float,datetime.date]) -> List[Type]:
    '''
    Intenta adivinar el tipo que puede tener un string
    probando una lista de tipos conocidos.
    Si acierta alguno, pone el tipo, si no, str.
    '''
    types_guessed = []
    #Probar los tipos 



raise Exception("Parada temporal")

connstr="DRIVER={sql server};server=openlabdb.intranet.net;Database=OpenData;UID=openlab;PWD=Pat1t0degoma"
connstr_conf="DRIVER={sql server};server=openlabdb.intranet.net;Database=OpenConf;UID=openlab;PWD=Pat1t0degoma"
#Pruebas de conexion a opneconf

anas_defined = """select abr,nombre from openconf.dbo.ana"""

conn = pypyodbc.connect(connstr)
print("Conexion correcta")
cur = conn.cursor()
cur.execute(anas_defined)
anasd = []
for row in cur.fetchall():
    anasd.append(row)
conn.close()
pprint.pprint(anasd)




#HTML con datos de paciente y medicacion de la intranet
urlmedicacion= "http://apache.intranet.net:8080/clinica_DAE/farmacia/ordenmedica/ordenmedica.php?nhc=%s"



#pruebas de conversion a datetime
#print(lines[3][5])
#dt = datetime.date.fromtimestamp(time.mktime(time.strptime(lines[3][5],"%d/%m/%Y %H:%M:%S")))
#print(f"DATETIME: {dt},{datetime.date.today()-dt}")

#Pruebas de coger medicacion de la intranet de farmacia
#Usar tuplas para mejorar rendimiento, solas o named_tuples

'''
Hay 3 tablas en el archivo: 

La primera contiene los datos demograficos del paciente.
La segunda contiene las lineas de medicacion.
La tercera contiene los comentarios de enfermeria y otros.
'''

nhc = '709350'

with utilidades.openURL(urlmedicacion % nhc) as source:
    file_anas = bs4.BeautifulSoup(source,features="lxml")
    #pac_info = [[y for y in list(x.strings) if y!='\n'] for x in ]
    tables = file_anas.find_all("table")
    medicacion = []
    pac_table,med_table,com_table = tables

    info_pac = [x for x in pac_table.find("div").strings]
    pac_medicacion = {}
    #pprint.pprint(info_pac)
    #for item in tables[1]:
        #pprint.pprint([x.find("p") for x in item.find_all("td")])
    for elem in med_table.find_all("tr"):
        med_line = []
        tds = elem.find_all("td")
        for td in tds:
            p = td.find("p")
            if p:
                try:
                    med_line.append(next(p.children))
                except:
                    pass
        if med_line!=[]:
            medicacion.append(med_line)
    #print("-------------------------------------")
    #pprint.pprint(info_pac)
    pac_medicacion['info'] = info_pac
    #print("-------------------------------------")
    #pprint.pprint(medicacion)
    pac_medicacion["farmacos"] = medicacion
    #print("-------------------------------------")
    farmacos = [[x[0],int(x[-1])] for x in medicacion]
    #print(farmacos)
    pac_medicacion['resumen'] = farmacos
    #print("-------------------------------------")
    coments = [x for x in com_table.find("div").strings]
    #print(coments)
    pac_medicacion["comentarios"] = coments
    print(json.dumps(pac_medicacion))



#raise "Parada temporal"


#Pruebas de coger analiticas ptes de 24h
#Usar tuplas para mejorar rendimiento, solas o named_tuples
analiticas24=[]
with open("example_intranet_anas.html") as anasfile:
    anas = bs4.BeautifulSoup(anasfile,features="lxml")
    table_anas = anas.find("table")
    #Las 3 primeras entradas son basura
    #Hay que obtener una tabla {nhc:[analiticas]}
    anas_pac = {}
    nhc = None
    for item in table_anas.find_all("tr")[3:]:
        td = item.find("td")
        key = td.string
        tds = item.find_all("td")
        if key:
            nhc = utilidades.cleanupSpace(list(tds[1].find("span").strings)[-1])
            print(nhc)
            #Crear entrada en el diccionario
            if not key in anas_pac:
                anas_pac[nhc]=[]
                anas_pac[nhc].append((utilidades.cleanupSpace(tds[2].string),utilidades.cleanupSpace(tds[-1].string)))
                #anas_pac[nhc] = [x.string if x!=None else None for x in tds[2:]]
        else:
                anas_pac[nhc].append((utilidades.cleanupSpace(tds[1].string),utilidades.cleanupSpace(tds[-1].string)))
        #print(anas_pac)
        #continue
    
        #analiticas24.append(line_ana)
#analiticas24 = [(x[2] if len(x)==8 else x[1],x[7] if len(x)==8 else x[6]) for x in analiticas24]
#pprint.pprint(analiticas24)
pprint.pprint(anas_pac)
#print(anas_pac)


#Esto solo funciona dentro del explorer en intranet
pag_ana = requests.get("http://estigiaw2k8.intranet.net/GIPI/Results/PatientStudyHistory.aspx?user=jodefeb&ResultNid=336269116&StudyNid=96")
print(pag_ana.text)

print('Ok')
    