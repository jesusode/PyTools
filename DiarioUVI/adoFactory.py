#Constantes para versiones de Access*******
Jet10 = 1
Jet11 = 2
Jet20 = 3
Jet3x = 4
Jet4x = 5
#******************************************

import win32com.client

def createAccessFile(name,format):
    catalog=win32com.client.Dispatch('ADOX.Catalog')
    query_str="Provider=Microsoft.Jet.OLEDB.4.0;Jet OLEDB:Engine Type=%s;Data Source= %s" %(format,name)
    catalog.Create(query_str)

if __name__=='__main__':
    #Create Access2000 database
    createAccessFile("myaccess.mdb", Jet4x)
    print('Terminado!')

