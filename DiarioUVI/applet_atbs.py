import PySimpleGUI as sg

import pickle
import json
import requests
import streams
import streams.dictutils
from streams.dictutils import groupby,mapDictTree
from bridge_odswriter import *
from CSVTransformer import *
from utilidades import *
from clasificacion_practica import *
import grupoJ
from bridge_odswriter import *
import webbrowser

#print(help(sg.Table))


#1.- Conseguir atbs--------------------------------------------------------
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

#pprint.pprint(total_familias)
#------------------------------------------------------------------


#Tasa de atbs_pautados
total_atbs = len(atbs_pautados)
tasa_atbs = total_atbs/numpacs
print(f"Tasa de atbs pautados : {tasa_atbs}")


#Recuento de antibioticos
recuento_atbs = streams.dictutils.pivot(atbs_pautados,[lambda x:x[4]])
recuento_atbs = sorted(recuento_atbs,key =lambda x: x[1],reverse=True)


recuento_familias = sorted(total_familias.items(),key =lambda x: x[1],reverse=True)
#print(recuento_familias)

#-------------------------------------------------------------------------

def export_to_ods(path):
    print("exportando a ods...")

rows = [ ["imipenem","45"],["cirpofloxacino","60"],["ceftazidima","25"]]
titles = ["Antibiótico","Total"]
titles2 = ["Familia","Total"]

#sg.theme('Light Blue 2')

sg.theme('Dark Blue 3')


#Definicion de menu
menu_def = [
    ["&Archivo",["&Salir"]],
    ["E&xportar",["Exportar a &ods"]]
]

layout = [  [sg.Menu(menu_def)],
            [sg.Text('Antibióticos pautados HUNSC 10/07/2021',size=(50,1),font="Arial 16 bold"),sg.Text("Total: 120, Tasa: 0.56",font="Arial 16 bold",text_color="navy")],
            [sg.Table(recuento_atbs,headings = titles,key = "TABLE",
                      col_widths = [50,8],
                      header_text_color = "black",
                      auto_size_columns = False,
                      font = "Arial 16 bold",
                      background_color="#EAEAEA",
                      row_height = 25,
                      max_col_width = 200,
                      justification="left",
                      text_color = "navy",
                      alternating_row_color = "lightblue",
                      num_rows= 8,
                      #display_row_numbers = True,
                      enable_events=True)],
            [sg.Text('Por Familias:',size=(60,1),font="Arial 16 bold",enable_events=True,key="XX")],
            [sg.Table(recuento_familias,headings = titles2,key = "TABLE_FAM",
                      col_widths = [50,8],
                      header_text_color = "black",
                      auto_size_columns = False,
                      font = "Arial 16 bold",
                      background_color="#EAEAEA",
                      row_height = 25,
                      max_col_width = 200,
                      justification="left",
                      text_color = "navy",
                      alternating_row_color = "lightblue",
                      num_rows= 8,
                      #display_row_numbers = True,
                      enable_events=True)],
            [sg.Button('Exit')] ]

window = sg.Window('Antibioticos pautados HUNSC', layout, finalize=True)


while True:             # Event Loop
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        sg.popup_ok("Adiós!")
        break
    elif event == 'TABLE':
        # if the text was clicked, open a browser using the text as the address
        print("Gestor de event TABLE")
        #print(window["TABLE"].get())
    elif event =="XX":
        print("Pulsada etiqueta!!!!")
    elif event == "Salir":
        print("Ha elegido Salir!!")
        break
    elif event == "Exportar a ods":
        path = ""
        export_to_ods(path)
window.close()