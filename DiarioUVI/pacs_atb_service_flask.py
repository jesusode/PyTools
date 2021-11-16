
from flask import Flask

app = Flask(__name__)



import urllib
import time
import datetime
import json
import xmlutils
import utilidades
import pickle
import os

info = '''
Microservicio que carga el archivo de pacientes de la intranet
si no lo tiene en cache de menos de 6 horas. Lo convierte en 
JSON y lo devuelve al peticionario.
'''

#Pacientes ingresados con dx (el ultimo disponible)----------------------------------
urlpacs="http://apache.intranet.net:8080/clinica_dae/adm/adm08-11_xml.php?usr=jodefeb&perfil=20&comboserv=0"
campos = ["NHC","Nombre Paciente","Edad","TIS","Registro","FechaIngreso","Servicio","Cama","Uenf","Serv.Cama","Diagnostico","Tipo Ing.","Motivo Ing.","Area AP"]
lines = []
lines.append(campos)
#------------------------------------------------------------------------------------

def server_init():
    global lines
    #with open("pacientes.xml","r",encoding = "latin1") as f:
    with utilidades.openURL(urlpacs) as f:
        #print(pacientes)
        pacientes = f.read()
        xp = xmlutils.xpath(pacientes,".//row",encoding = "latin1")
        for item in xp:
            parts=[]
            #print(item)
            for elem in item:
                #print(elem.text)
                parts.append(elem.text)
            lines.append(parts)
        #Guardar cache para la proxima vez
        if not os.path.exists("pacs_atbs.ser"):
            with open("pacs_atbs.ser","wb") as hf:
                pickle.dump(lines,hf)




#Metodos REST------------------------------

@app.route('/pacs_atbs',methods=['GET'])
def get_handler():
    '''Handles listing'''
    print("Iniciando respuesta...")
    return json.dumps({'result': 'true'})

#------------------------------------------
