#Pruebas de CSVTransformer


import streams
import streams.CSVFileIterator
from streams.CSVFileIterator import CSVFileIterator
from CSVTransformer import *
import pprint
import time


db = "ANTIBIOGRAMAS.sqlite"
create_table = """create table if not exists antibiogramas (
    nid integer primary key autoincrement,
    Microorganismo text,
    Muestra text,
    atb text,
    sensibilidad text,
    CMI text,
    Proceso text,
    fecha datetime,
    Servicio text,
    id text,
    NHC text,
    anyo integer,
    edad integer,
    Sexo text
    );
    """


    
iter = CSVFileIterator("../atbsEspecializada2020.csv","latin1",";")
print("---------------------------------------")
print(f"starting at: {time.time()}")

keys = iter.next()
print(f"CAMPOS: {keys}")

conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute(create_table)



#Creamos un transformer
transformer = CSVTransformer([CSVToDict,CSVToDictWithConversions,CSVToJSON,CSVToSQL])


#for i in range(30000):
while iter.hasNext():
    n = iter.next()
    #pprint.pprint(transformer.transform(n,keys,clean=True,tname = "antibiogramas"))
    #print(transformer.transform(n,keys,clean=True,tname = "antibiogramas",convert = True))
    if n != None:
        tt = transformer.transform(n,keys,clean=True,tname = "antibiogramas",convert = True)
        cur.execute(tt[-1])

iter.close()
print(f"finishing at: {time.time()}")


conn.commit()
#Prueba de vida
for row in cur.execute("select * from antibiogramas limit 300;"):
    print(row)
conn.close()

print('Ok')
    