
from flask import Flask

import time
import datetime
import json

import flask
from flask.helpers import make_response
import xmlutils
import utilidades
import pickle
import os
import bs4
import streams
import streams.dictutils
from streams.dictutils import groupby, mapDictTree
import pypyodbc
import consultas_ol

info = '''
<h2>HUNSC PROA SERVICE</h2>
<br/>
<h3><p>Microservicio que carga el archivo de pacientes de la intranet
si no lo tiene en cache de menos de 6 horas.</p><p> Lo convierte en 
JSON y lo devuelve al peticionario.</p></h3>
<br/>
<h3><p> Todos los servicios responden con un objeto JSON que contiene</p>
<p>el resultado en una entrada "result". (Ej: {"result" : ...})</p>
'''

#Pacientes ingresados con dx (el ultimo disponible)----------------------------------
urlpacs="http://apache.intranet.net:8080/clinica_dae/adm/adm08-11_xml.php?usr=jodefeb&perfil=20&comboserv=0"
campos_pacs = ["NHC","Nombre Paciente","Edad","TIS","Registro","FechaIngreso","Servicio","Cama","Uenf","Serv.Cama","Diagnostico","Tipo Ing.","Motivo Ing.","Area AP"]
lines_pacs = []
lines_pacs.append(campos_pacs)

lines_atbs = []
campos_atbs = ["NHC","Nombre","U.Enf.","Cama","Antibiotico","Fecha Inicio","Dosis","Via","Frecuencia"]
urlatbs = "http://apache.intranet.net:8080/clinica_DAE/hos/hos12-11_xml.php?comboantib=TODOS"
lines_atbs.append(campos_atbs)


#HTML con datos de paciente y medicacion de la intranet
urlmedicacion= "http://apache.intranet.net:8080/clinica_DAE/farmacia/ordenmedica/ordenmedica.php?nhc=%s"

#------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
#Configuracion Openlab
connstr = consultas_ol.connstr
anas_from_pac= consultas_ol.anas_from_pac
anas_defined = consultas_ol.anas_defined
organismos_defined = consultas_ol.organismos_defined
res_micro = consultas_ol.resmicro
aislamientos = consultas_ol.aislam_str
atb_s = consultas_ol.atb_string
#-----------------------------------------------------------------------------------


def makeFlaskResponse(resp):
    response = flask.Response(resp)
    response.access_control_allow_origin = "*"
    response.access_control_allow_methods = ' GET, DELETE, HEAD, OPTIONS'
    return response


app = Flask(__name__)

@app.before_first_request
def server_init():
    global lines_pacs
    #with open("pacientes.xml","r",encoding = "latin1") as f:
    print("Cargando pacientes...")
    with utilidades.openURL(urlpacs) as f:
        pacientes = f.read()
        xp = xmlutils.xpath(pacientes,".//row",encoding = "latin1")
        for item in xp:
            parts=[]
            for elem in item:
                parts.append(elem.text)
            lines_pacs.append(parts)
        #Guardar cache para la proxima vez
        if not os.path.exists("pacs_dx.ser"):
            with open("pacs_dx.ser","wb") as hf:
                pickle.dump(lines_pacs,hf)

    print("Cargando antibioticos...")
    with utilidades.openURL(urlatbs) as f:
        pacientes = f.read()
        xp = xmlutils.xpath(pacientes,".//row",encoding = "latin1")
        for item in xp:
            parts=[]
            for elem in item:
                parts.append(elem.text)
            lines_atbs.append(parts)
        #Guardar cache para la proxima vez
        if not os.path.exists("pacs_atbs.ser"):
            with open("pacs_atbs.ser","wb") as hf:
                pickle.dump(lines_atbs,hf)

#Metodos REST------------------------------
@app.route('/info',methods=['GET'])
def info_handler():
    '''Handles info'''
    #return info
    return makeFlaskResponse(json.dumps([info]))

@app.route('/pacs',methods=['GET'])
def pacs_handler():
    '''Handles listing'''
    print("Iniciando respuesta pacs...")
    #return json.dumps({'result': lines_pacs})
    return makeFlaskResponse(json.dumps({"result": lines_pacs}))

@app.route('/atbs',methods=['GET'])
def atbs_handler():
    '''Handles listing'''
    print("Iniciando respuesta atbs...")
    #return json.dumps({'result': lines_atbs})
    return makeFlaskResponse(json.dumps({"result": lines_atbs}))

@app.route('/medicacion/<nhc>',methods=['GET'])
def medicacion_handler(nhc):
    '''
    Hay 3 tablas en el archivo: 

    La primera contiene los datos demograficos del paciente.
    La segunda contiene las lineas de medicacion.
    La tercera contiene los comentarios de enfermeria y otros.
    '''
    pac_medicacion = {}
    with  utilidades.openURL(urlmedicacion % nhc) as source:
        file_anas = bs4.BeautifulSoup(source,features="lxml")
        #pac_info = [[y for y in list(x.strings) if y!='\n'] for x in ]
        tables = file_anas.find_all("table")
        medicacion = []
        pac_table,med_table,com_table = (None,None,None)
        if len(tables) == 3:
            pac_table,med_table,com_table = tables
        else: #No hay medicacion
            #Ver resto de casos
            #Fallo: Devolvemos esqueleto de diccionario
            return json.dumps({"result" : None})

        info_pac = [x for x in pac_table.find("div").strings]
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
    #return json.dumps({"result":pac_medicacion})
    return makeFlaskResponse(json.dumps({"result": pac_medicacion}))

@app.route('/total_pacs',methods=['GET'])
def total_pacs_handler():
    '''Handles listing'''
    print("Iniciando respuesta total_pacs...")
    #return json.dumps({'result': len(lines_pacs)})
    return makeFlaskResponse(json.dumps({"result": lines_pacs}))

@app.route('/pacs_serv',methods=['GET'])
def pacs_serv_handler():
    '''Handles listing'''
    print("Iniciando respuesta pacs_serv...")

    npacs = len(lines_pacs)
    #Tabla servicio->nhcs
    byserv = groupby(lambda x : x[6],lines_pacs[1:])
    mapDictTree(byserv,[lambda x: [y[0] for y in x]])
    #return json.dumps({'result': byserv})
    return makeFlaskResponse(json.dumps({"result": byserv}))

@app.route('/pacs_nhc',methods=['GET'])
def pacs_nhc_handler():
    '''Handles listing'''
    print("Iniciando respuesta pacs_nhc...")
    #Tabla servicio->nhcs
    bynhc = groupby(lambda x : x[0],lines_pacs[1:])
    #return json.dumps({'result': bynhc})
    return makeFlaskResponse(json.dumps({"result": bynhc}))

@app.route('/analiticas/<nhc>',methods=['GET'])
def analiticas_handler(nhc):
    global connstr,anas_from_pac
    analiticas = anas_from_pac.format(nhc)
    conn = pypyodbc.connect(connstr)
    cur = conn.cursor()
    cur.execute(analiticas)
    #cur.fetchall()
    anas = []
    for row in cur.fetchall():
        lst = list(row)
        lst[0]=str(lst[0])
        anas.append(lst)
    print("Conexion correcta")
    conn.close()
    #response = flask.Response(json.dumps({"result": anas}))
    #response.access_control_allow_origin = "*"
    #response.access_control_allow_methods = ' GET, DELETE, HEAD, OPTIONS'
    return makeFlaskResponse(json.dumps({"result": anas}))

@app.route('/res_micro/<nhc>',methods=['GET'])
def res_micro_handler(nhc):
    global connstr,resmicro
    micro = res_micro.format(nhc)
    conn = pypyodbc.connect(connstr)
    cur = conn.cursor()
    cur.execute(micro)
    #cur.fetchall()
    micros = []
    for row in cur.fetchall():
        micros.append(row)
    print("Conexion correcta")
    conn.close()
    #response = flask.Response(json.dumps({"result": micros}))
    #response.access_control_allow_origin = "*"
    #response.access_control_allow_methods = ' GET, DELETE, HEAD, OPTIONS'
    return makeFlaskResponse(json.dumps({"result": micros}))


@app.route('/anas_defined',methods=['GET'])
def anas_defined_handler():
    global connstr_conf,anas_defined
    conn = pypyodbc.connect(connstr)
    print("Conexion correcta")
    cur = conn.cursor()
    cur.execute(anas_defined)
    anasd = []
    for row in cur.fetchall():
        anasd.append(row)
    conn.close()
    #print(anasd)
    #response = flask.Response(json.dumps({"result": anasd}))
    #response.access_control_allow_origin = "*"
    #response.access_control_allow_methods = ' GET, DELETE, HEAD, OPTIONS'
    #return response
    return makeFlaskResponse(json.dumps({"result": anasd}))


@app.route('/microorganismos',methods=['GET'])
def amicroorganismos_handler():
    global connstr_conf,organismos_defined
    conn = pypyodbc.connect(connstr)
    print("Conexion correcta")
    cur = conn.cursor()
    cur.execute(organismos_defined)
    orgs = []
    for row in cur.fetchall():
        orgs.append(row)
    conn.close()
    return json.dumps({"result": orgs})


@app.route('/aislamientos/<nhc>',methods=['GET'])
def aislamientos_handler(nhc):
    global connstr,aislamientos,atb_s
    micro = aislamientos.format(nhc)
    conn = pypyodbc.connect(connstr)
    cur = conn.cursor()
    cur.execute(micro)
    #cur.fetchall()
    micros = []
    atbs = {}
    org_nids = []
    for row in cur.fetchall():
        #Usar str para que serialize las fechas a JSON. Si no, da una excepcion
        micros.append([str(x) for x in row])
        org_nids.append(row[-1])
        atbs[row[-1]] = []
    print("Conexion correcta")
    a_tb = atb_s.format(','.join(["'" + str(x) + "'" for x in org_nids]))

    cur.execute(a_tb)
    print(cur.description)

    for row in cur.fetchall():
        atbs[row[0]].append([str(x) for x in row[1:]])
        #cont+=1
    conn.close()
    return json.dumps({"result": {"organismos": micros,"antibiogramas" : atbs}})


#------------------------------------------

if __name__ == '__main__':
    #app.run(port=5000,debug=True,host="0.0.0.0")
    app.run(port=11111,debug=True)