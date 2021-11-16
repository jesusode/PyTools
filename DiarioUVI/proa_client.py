#Cliente de pruebas para el servidor proa

import requests
import json
import pprint
import grupoJ
import pickle
import streams
import streams.dictutils
from streams.dictutils import groupby,mapDictTree
from bridge_odswriter import *
from CSVTransformer import *
from utilidades import *
from clasificacion_practica import *


htmltemplate_atbs = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>{0}</title>
</head>
<body>
<h1>{0}</h1>
<h2>Pacientes ingresados: {1}</h2>
<h2>Total antibioticos: {2}</h2>
<h2>Tasa prescripcion: {3}</h2>
{4}
</body>
</html>"""


#Estancias 2020
estancias_2020 = 252594
#Poblacion atendida
poblacion_atendida = 479925

#conseguir los pacientes ingresados por servicio
pacsserv = json.loads(requests.get("http://localhost:11111/pacs_serv").text)["result"]

#Tabla de datos de paciente por nhc
pacsnhc = json.loads(requests.get("http://localhost:11111/pacs_nhc").text)["result"]
#pprint.pprint(pacsnhc)
numpacs = len(pacsnhc)
print(f"Numero de pacientes ingresados: {numpacs}")


lista_antibioticos = [x.upper() for x in grupoJ.antibioticos_grupoJ.values() if not ' ' in x]
#pprint.pprint(lista_antibioticos)

#Esto es lento e ineficiente!
def isAtbLine(line : str) ->bool : 
    '''
    docstr
    '''
    global lista_antibioticos
    for item in lista_antibioticos:
        if item in line: return True
    return False


def buscaMedPac(nhc: str):
    '''
    docstr
    '''
    jspac = requests.get(f"http://localhost:11111/medicacion/{nhc}").text
    pac_dic = json.loads(jspac)["result"]
    return pac_dic

'''
nhcs = ['1471248','1050429','1016439','2263943',
       '839910','220448','1537976','2168520','382648',
       '24766','709350']
#for nhc in nhcs[:3]:
for nhc in nhcs:
    pac_dic=buscaMedPac(nhc)
    print(pac_dic['info'][0])
    print("-----------------------------------------------------")
    #print('\n'.join(['\t' + ' '.join(x) for x in pac_dic['farmacos']]))
    print('\n'.join(['\t' + x[0] + (" >>ATB!!!!<<" if isAtbLine(x[0].upper()) else '') for x in pac_dic['farmacos']]))
    print('=====================================================')
'''

#Pruebas en estatico--------------------------------------------------------
atbs_pautados = None
pacs_ingresados = None
with open("pacs_atbs.ser","rb") as f:
    atbs_pautados = pickle.load(f)
    f.close()


#Tabla de familias:n_atbs------------------------------------------
total_familias = {}
for item in clasificacion_atbs:
    total_familias[item] = 0

#Recorrer los atbs pautados e ir sumando por familia
for lin in atbs_pautados:
    fam = clasificar(lin[4]) 
    if fam in total_familias:
        total_familias[fam] += 1

pprint.pprint(total_familias)
#------------------------------------------------------------------


#Tasa de atbs_pautados
total_atbs = len(atbs_pautados)
tasa_atbs = total_atbs/numpacs
print(f"Tasa de atbs pautados : {tasa_atbs}")


#Recuento de antibioticos
recuento_atbs = streams.dictutils.pivot(atbs_pautados,[lambda x:x[4]])
recuento_atbs = sorted(recuento_atbs,key =lambda x: x[1],reverse=True)
#pprint.pprint(recuento_atbs)
print("-----------------------------------------------------")
to_table=multiListToTable(recuento_atbs)
#print(to_table)
with open("recuento_atbs.html","w",encoding="latin-1") as ff:
    ff.write(htmltemplate_atbs.format("Recuento de antibioticos",numpacs,total_atbs,tasa_atbs,to_table))

recuento_atbs_por_serv = streams.dictutils.pivot(atbs_pautados,[lambda x : x[2],lambda x:x[4]])
#pprint.pprint(recuento_atbs_por_serv)
to_table=multiListToTable(recuento_atbs_por_serv)
#print(to_table)
with open("recuento_atbs_por_serv.html","w",encoding="latin-1") as ff:
    ff.write(htmltemplate2.format("Recuento de antibioticos por servicio",to_table))
print("-----------------------------------------------------")
recuento_atbs_por_nhc = streams.dictutils.pivot(atbs_pautados,[lambda x : x[0],lambda x:x[4]])
to_table=multiListToTable(recuento_atbs_por_nhc)
#pprint.pprint(to_table)
with open("recuento_atbs_por_nhc.html","w",encoding="latin-1") as ff:
    ff.write(htmltemplate2.format("Recuento de antibioticos por NHC",to_table))
print("-----------------------------------------------------")
#---------------------------------------------------------------------------



'''
table_servs = dict(enumerate(pacsserv.keys()))
pprint.pprint(table_servs)
#pprint.pprint(pacsserv)
random_serv = table_servs[13]
random_pacs = pacsserv[random_serv] + ['123456']
print(f"Pacientes ingresados en {random_serv} : {random_pacs}")
print("Medicaciones:")
print("===============\n")
for pac in random_pacs:
    p_med = buscaMedPac(pac)
    if p_med != None:
        print(f"p_med: {p_med['resumen']}")
    else:
        print("No hay medicacion pautada para este paciente.")
    print("-------------------------------------------------------")
    #print(p_med["resumen"])
'''

