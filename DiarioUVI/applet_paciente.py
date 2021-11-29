import PySimpleGUI as sg

import pickle
import json
import requests
#import streams
#import streams.dictutils
#from streams.dictutils import groupby,mapDictTree
#from bridge_odswriter import *
from CSVTransformer import *
from utilidades import *
from clasificacion_practica import *
import grupoJ
import webbrowser

#print(help(sg.Table))


#1.- Conseguir atbs--------------------------------------------------------
lista_antibioticos = [x.upper() for x in grupoJ.antibioticos_grupoJ.values() if not ' ' in x]
#Estancias 2020
estancias_2020 = 252594
#Poblacion atendida
poblacion_atendida = 479925
nhc = "328983"
info_pac={}

def getPacInfo(nhc):
    global window
    #Pedir datos de paciente
    info_pac = json.loads(requests.get(f"http://localhost:11111/medicacion/{nhc}").text)["result"]
    if info_pac != None:
        pac_info = "\n".join(info_pac["info"])
        #Y actualizar los campos
        window["PAC_INFO"].update(value=pac_info)
        window["TABLE"].update(values=info_pac["farmacos"])
        window["OBSERV"].update(value=info_pac["comentarios"][0])

#-------------------------------------------------------------------------

#-------------------------------------------------------------------------

def export_to_ods(path):
    print("exportando a ods...")

rows = [ ["N/D","N/D","N/D","N/D","N/D","N/D"]]
titles = ["FÁRMACO","VÍA","DOSIS","SECUENCIA","PAUTA","DÍAS"]

rows2 = [ ["N/D","N/D","N/D","N/D"]]
titles2 = ["FECHA","PETICIÓN","DETERMINACIÓN","RESULTADO"]

rows3 = [ ["N/D","N/D","N/D","N/D","N/D","N/D"]]
titles3 = ["FECHA","ID","MUESTRA","ESTADO","RESULTADO","OBSERVACIONES"]

#sg.theme('Light Blue 2')
#sg.theme('Dark Blue 3')
sg.theme('Default 1')


#Definicion de menu
menu_def = [
    ["&Archivo",["&Salir"]],
    ["E&xportar",["Exportar a &ods"]]
]

tab1_layout = [
    [sg.Text('PACIENTE:',size=(60,1),font="Arial 12 bold underline")],
    [sg.Multiline(default_text="Sin datos de paciente.",font="Arial 10",size=(80,12),key="PAC_INFO")]
]

tab2_layout = [

    [sg.Text('MEDICACIÓN:',size=(50,1),font="Arial 12 bold underline",key="MEDICACION")],
    [sg.Table(rows,headings = titles,key = "TABLE",
                col_widths = [25,8,11,11,8,4],
                header_text_color = "black",
                auto_size_columns = False,
                font = "Arial 10 bold",
                background_color="#EAEAEA",
                row_height = 25,
                max_col_width = 200,
                justification="left",
                text_color = "black",
                alternating_row_color = "lightgray",
                num_rows= 8,
                pad=(0,10),
                #display_row_numbers = True,
                enable_events=True)]
]

tab3_layout = [

    [sg.Text('OBSERVACIONES:',size=(60,1),font="Arial 12 bold underline")],
    [sg.Multiline(default_text="Datos no disponibles.",font="Arial 10",size=(80,7),key="OBSERV")] 
]

col_izq = [ [sg.TabGroup([[sg.Tab("PACIENTE",tab1_layout),
                           sg.Tab("MEDICACIÓN",tab2_layout),
                           sg.Tab("OBSERVACIONES",tab3_layout)]])]
]

tab4_layout = [
    [sg.Text('ANALÍTICAS:',size=(60,1),font="Arial 12 bold underline")],
    [sg.Table(rows2,headings = titles2,key="ANAL",
                col_widths = [25,8,11,11,8,4],
                header_text_color = "black",
                auto_size_columns = False,
                font = "Arial 10 bold",
                background_color="#EAEAEA",
                row_height = 25,
                max_col_width = 200,
                justification="left",
                text_color = "black",
                alternating_row_color = "lightgray",
                num_rows= 8,
                pad=(0,10),
                #display_row_numbers = True,
                enable_events=True)]    
]


tab5_layout = [
    [sg.Text('PETICIONES MICROBIOLOGÍA',size=(50,1),font="Arial 12 bold underline")],
    [sg.Table(rows3,headings = titles3,key="PET_MICRO",
                col_widths = [25,8,11,11,8,4],
                header_text_color = "black",
                auto_size_columns = False,
                font = "Arial 10 bold",
                background_color="#EAEAEA",
                row_height = 25,
                max_col_width = 200,
                justification="left",
                text_color = "black",
                alternating_row_color = "lightgray",
                num_rows= 8,
                pad=(0,10),
                #display_row_numbers = True,
                enable_events=True)]
]

tab6_layout = [
    [sg.Text('HISTÓRICO MICROBIOLOGÍA:',size=(60,1),font="Arial 12 bold underline")],
    [sg.Table(rows,headings = titles,key="HISTO_MICRO",
                col_widths = [25,8,11,11,8,4],
                header_text_color = "black",
                auto_size_columns = False,
                font = "Arial 10 bold",
                background_color="#EAEAEA",
                row_height = 25,
                max_col_width = 200,
                justification="left",
                text_color = "black",
                alternating_row_color = "lightgray",
                num_rows= 8,
                pad=(0,10),
                #display_row_numbers = True,
                enable_events=True)]
]


col_der = [ [sg.TabGroup([[sg.Tab("ANALÍTICAS",tab4_layout),
                           sg.Tab("PETICIONES MICROBIOLOGÍA",tab5_layout),
                           sg.Tab("HISTÓRICO MICROBIOLOGÍA",tab6_layout)]])]

]


frame_sup_layout = [

    [sg.Text("Buscar NHC: ",font="Arial 12 bold",pad=(5,20),size=(18,1)),sg.Input(justification="center",size=(40,1),font="Arial 16 bold",key="NHC",pad=(0,10)),sg.Button('Buscar',key="BUSCAR",font="Arial 16 bold",pad=(10,10),size=(40,1))]
]

layout = [     
            [sg.Menu(menu_def)],
            [sg.Frame("Buscar paciente por NHC",frame_sup_layout,font="Arial 11")],
            [sg.Frame("Resultados paciente",[ [sg.Pane([sg.Column(col_izq),sg.Column(col_der)],orientation="h")]],font="Arial 11")],
            [sg.StatusBar("PROA HUNSC")]  
 ]

window = sg.Window('PROA HUNSC. Información de paciente.', layout, finalize=True)


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
    elif event == "Salir":
        print("Ha elegido Salir!!")
        break
    elif event == "BUSCAR":
        print(f"Buscando nhc:{values['NHC']}")
        getPacInfo(values['NHC'])
    elif event == "PAC":
        window["PAC_INFO"]
    elif event == "Exportar a ods":
        path = ""
        export_to_ods(path)
window.close()