#Pruebas

import CSVJSONIterator
import pprint
import time

from  pymongo import MongoClient
import json

    
jsiter = CSVJSONIterator.CSVJSONIterator("../atbsEspecializada2020.csv","latin1",";",findNumsBoolNull = True,
cleanWhitespace=True,compact = True)
print("---------------------------------------")
print(f"starting at: {time.time()}")
f = open("jsonified.txt","w",encoding = "utf-8")


#PyMongo-------------------------------
mongo_client = MongoClient()
#Crear Base de Datos si no existe
db = mongo_client["micro_hunsc"]
print(mongo_client.list_database_names())
#La "tabla" en Mongo es la Collection
collection = db["antibiogramas"]
print(collection)
#-------------------------------------



'''
#for i in range(300):
while jsiter.hasNext():
    #pprint.pprint(jsiter.next())
    n = jsiter.next()
    #print(n)
    #f.write(n + ',')
    #Mongo------------------------------
    collection.insert_one(json.loads(n))
    #-----------------------------------
jsiter.close()

f.close()
'''


#querys con Mongo
#for i in range(3):
#    print(collection.find_one({"Muestra" :  "Hemocultivo","Sexo" : "Hombre","edad":{"$gt":90}}))
    #print(collection.find_one())

cont = 0
for doc in collection.find({"Muestra" :  "Hemocultivo","Sexo" : "Hombre","edad":{"$gt":80}}):
    print(doc)
    cont+=1

print(f"Encontrados {cont} documentos")

print(f"finishing at: {time.time()}")

print('Ok')
    