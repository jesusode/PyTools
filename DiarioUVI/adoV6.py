#!Python

__version__='6.0'
__date__='28/06/2009'

import win32com.client
import sys
import os
import types
import pickle
import io

#Diccionario de tipos de columnas
adoColTypes={
    1:'adColFixed',
    2:'adColNullable'
    }


#Diccionario de constantes para el tipo de los campos
adoDelOptions={
    'adAffectAll':3,
    'adAffectAllChapters':4,
    'adAffectCurrent':1,#Por defecto
    'adAffectGroup':2
    }

adoTypes={
    20:'adBigInt',
    128:'adBinary',
    11: 'adBoolean',
    8:'adBSTR',
    6:'adCurrency',
    136:'adChapter',
    129:'adChar',
    7:'adDate',
    133:'adDBDate',
    134:'adDBTime',
    135:'adDBTimeStamp',
    14:'adDecimal',
    5:'adDouble',
    0:'adEmpty',
    10:'adError',
    64:'adFileTime',
    72:'adGUID',
    9:'adIDispatch',
    3:'adInteger',
    13:'adIUnknown',
    205:'adLongVarBinary',
    201:'adLongVarChar',
    203:'adLongVarWChar',
    131:'adNumeric',
    138:'adPropVariant',
    4:'adSingle',
    2:'adSmallInt',
    16:'adTinyInt',
    21:'adUnsignedBigInt',
    19:'adUnsignedInt',
    18:'adUnsignedSmallInt',
    17:'adUnsignedTinyInt',
    132:'adUserDefined',
    204:'adVarBinary',
    200:'adVarChar',
    12:'adVariant',
    139:'adVarNumeric',
    202:'adVarWChar',
    130:'adWChar'
    }
adoCursors={
    'adOpenDynamic':2,
    'adOpenForwardOnly':0,
    'adOpenKeyset':1,
    'adOpenStatic':3,
    'adOpenUnspecified':-1
    }

adoLockType={
    'adLockBatchOptimistic':4,
    'adLockOptimistic':3,
    'adLockPessimistic':2,
    'adLockReadOnly':1,
    'adLockUnspecified':-1
    }

adoCursorLocation={
    'adUseServer':3,
    'adUseClient':2
    }

#Constantes para Recordset::GetRows()
GetRowsOptionEnum={'adGetRowsRest':-1}

BookmarkEnum={
    'adBookmarkCurrent': 0,
    'adBookmarkFirst': 1,
    'adBookmarkLast': 2
    }

class Connection:

    def __init__(self,constring,dontSplitConnString=0):
      partes={}
      self.__driver=''
      self.__server=''
      self.__db=''     
      self.__user=''    
      self.__pwd=''     
      self.__adoConn=None
      self.__conStr=''      
      if dontSplitConnString:
          self.__conStr=constring
          #print self.__conStr + '\n\n'
      else:
          for item in constring.split(';'):
              if item!='' and item.split('=')!=[]:
                  partes[item.split('=')[0].lower()]=item.split('=')[1]
          
          self.__driver=partes['driver']
          self.__server=partes['server']
          self.__db=partes['database']     
          self.__user=partes['user']     
          self.__pwd=partes['pwd']     
          self.__adoConn=None
          self.__conStr=''
          self.__makeConString()
      self.__adoConn=self.getConnection()
      #print str(self.__adoConn)

 

    #Metodos de accesoo
    def getDriver(self):
      return self.__driver

    def setDriver(self,nuevo):
      self.__driver=nuevo
      self.__makeConString()      

    def getServer(self):
      return self.__server

    def setServer(self,nuevo):
      self.__server=nuevo
      self.__makeConString()      

    def getDb(self):
      return self.__db

    def setDb(self,nuevo):
      self.__db=nuevo
      self.__makeConString()      

    def getUser(self):
      return self.__user

    def setUser(self,nuevo):
      self.__user=nuevo
      self.__makeConString()      

    def getPwd(self):
      return self.__pwd

    def setPwd(self,nuevo):
      self.__pwd=nuevo
      self.__makeConString()      

    def getConString(self):
        return self.__conStr

  
    def getConnection(self):
      #Obtiene la conexion ado
      #try:
     adoConn = win32com.client.Dispatch('ADODB.Connection')
     adoConn.Open(self.__conStr)
     return adoConn

##      except:
##         print 'Atrapada una excepcion intentando conectar con la base de datos'
##         return None

    def __makeConString(self):
      self.__conStr='driver=' + self.__driver + ';server=' + self.__server + ';database=' +self.__db + ';UID=' + self.__user + ';pwd=' + self.__pwd + ';'      


    def execute(self,query):
      #try:
        #print query
        (self.__adoRS, success) = self.__adoConn.Execute(query) 
        return self.__adoRS       

##      except:
##        print 'Atrapada una excepcion ejecutando la consulta'
##        return None


    def closeConnection(self):
      if self.__adoConn:
        self.__adoConn.Close()

    def cargaLista(self,query,campo,encoding='ascii'):
        self.__results=[]    
      #try:
        (self.__adoRS, success) = self.__adoConn.Execute(query)
        #print (self.__adoRS,success)
        if not self.__adoRS.EOF:
          self.__adoRS.MoveFirst()
          while not self.__adoRS.EOF:
            if type(self.__adoRS.Fields(campo).Value)==str:              
             self.val=(self.__adoRS.Fields[campo].Value).encode(encoding,"replace")
            self.__results.append(self.val)
            self.__adoRS.MoveNext()
          #self.__adoRS=None
          return self.__results
        else:
          return None

      #except:
        #print 'Atrapada una excepcion ejecutando la consulta'
        #return None


    def cargaDiccionario(self,query,claves,valores,encoding='ascii'):
        self.__results={}    
      #try:
        (self.__adoRS, success) = self.__adoConn.Execute(query)
        self.__adoRS.MoveFirst()
        while not self.__adoRS.EOF:
          if type(valores)==type(''): #Valores es un string
              if type(self.__adoRS.Fields(claves).Value)==str:
                self.__clave=((self.__adoRS.Fields(claves).Value).encode(encoding,"replace")).strip()
              else:
                  self.__clave=self.__adoRS.Fields(claves).Value
              if type(self.__adoRS.Fields(valores).Value)==str:            
                self.__valor=((self.__adoRS.Fields(valores).Value).encode(encoding,"replace")).strip()
              else:
                  self.__valor=self.__adoRS.Fields(valores).Value
              self.__results[self.__clave]=self.__valor
              
          elif type(valores)==type([]): #Valores es una lista
              if type(self.__adoRS.Fields(claves).Value)==str:
                self.__clave=((self.__adoRS.Fields(claves).Value).encode(encoding,"replace")).strip()
              else:
                self.__clave=self.__adoRS.Fields(claves).Value
              #Crear una entrada de lista para cada clave
              self.__results[self.__clave]=[]
              for campo in values:
                  if type(self.__adoRS.Fields(campo).Value)==str:            
                    self.__valor=((self.__adoRS.Fields(campo).Value).encode(encoding,"replace")).strip()
                  else:
                    self.__valor=self.__adoRS.Fields(campo).Value
                  self.__results[self.__clave].append(self.__valor)
                  
          self.__adoRS.MoveNext()
        #print str(self.__results)
        return self.__results       

      #except:
        #print 'Atrapada una excepcion ejecutando la consulta'
        #return None




class Recordset:
  def __init__(self):
      self.__rst=win32com.client.Dispatch('ADODB.Recordset')

  def setConnection(self,con):
      if self.__rst and con:
        self.rst.ActiveConnection=con
        

  def open(self,query,con,cursor=adoCursors['adOpenKeyset'],locktype=adoLockType['adLockOptimistic'],opt=8):
    if self.__rst:
        args=[query,con] #,cursor,locktype]
        self.__rst.Open(query,con)
        #self.__rst.Open(args) 


  def setCursor(self,cursor):
      self.__rst.Cursor=adoCursors[cursor]

  def close(self):
    if self.__rst:
      self.__rst.Close()

  def update(self):
    self.__rst.Update()

  def getRecordset(self):
    return self.__rst


  def addNew(self,record=[]):
      self.__rst.AddNew()


  def moveNext(self):
      try:
          self.__rst.MoveNext()
      except:
          return -1

  def movePrevious(self):
      try:
          self.__rst.MovePrevious()
      except:
          return -1

          
  def moveFirst(self):
      try:
          self.__rst.MoveFirst()
      except:
          return -1


  def moveLast(self):
      try:
          self.__rst.MoveLast()
      except:
          return -1

  def save(self,destino,formato=0):
    
    if formato==1:
        #Formato XML
        self.__rst.Save(destino,1)
    else:
        #Formato ADTG (por defecto)
        self.__rst.Save(destino,0)

  def delete(self,options):
      self.__rst.Delete(adoDelOptions[options])

  def find(self,criterio):
      self.__rst.Find(criterio)

  def filter(self,criterio):
      self.__rst.Filter=criterio

  def requery(self):
      self.__rst.Requery()

  def getRecordCount(self):
      '''
        Obtiene el numero de registros
        independientemente del tipo de cursor
        que se haya establecido
      '''
      try:
          contador=0
          while not self.__rst.EOF:
              self.__rst.MoveFirst()
              contador+=1
              self.__rst.MoveNext()
          self.__rst.MoveFirst()
          return contador
      except:
          print('Atrapada una excepcion en getRecordCount')

  def isEOF(self):
      if self.__rst.EOF:
          return 1
      else:
          return 0
        
  def isBOF(self):
      if self.__rst.BOF:
          return 1
      else:
          return 0

  def setCursorLocation(self,loc):
      if loc in adoCursorLocation:
          self.__rst.CursorLocation=adoCursorLocation[loc]
      else:
          #Cursor de cliente por defecto
          self.__rst.CursorLocation=2 

  def getField(self,nombre):
      try:
          return self.__rst.Fields(nombre).Value
      except:
          print('Atrapada una excepcion en getField')
          return None


  def setField(self,nombre,valor):
      try:
          self.__rst.Fields(nombre).Value=valor
      except:
          print('Atrapada excepcion dando valor a campo')


  def getFieldsNames(self):
      nombres=[]
      for it in range(self.__rst.Fields.Count):
          nombres.append(self.__rst.Fields(it).Name)
      return nombres


  def disconnect(self):
      self.__rst.ActiveConnection=None

  def reconnect(self,con):
      self.__rst.ActiveConnection=con

  def addField(self,nombre):
      try:
          self.__rst.Fields.Add(nombre)
      except:
          print('Atrapada una excepcion en addField')


  def rst2Dict(self,clave):
      '''
         Transforma un recordset en un diccionario
         del tipo {campo_clave:[resto del registro]}
      '''
      dict={}
      fila=[]
      self.__rst.MoveFirst()
      while not self.__rst.EOF:
        for it in range(self.__rst.Fields.Count):
          if self.__rst.Fields(it).Name!=clave:
            fila.append(self.__rst.Fields(it).Value)
            #print str(self.__rst.Fields(it).Value)
          else:
            c=self.__rst.Fields(clave).Value
        dict[c]=fila
        fila=[]
        c=''
        self.__rst.MoveNext()
      return dict


  def getRows(self,start=GetRowsOptionEnum['adGetRowsRest'],fields=None):
      '''
      Devuelve el resultado de la query en forma de array pero invertido.
      Cada fila equivale a una columna (los resultados para un campo)
      de la query. En general devuelve unicode.
      '''
      if fields:
          return self.__rst.GetRows(start,fields)
          return list([list(i) for i in self.__rst.GetRows(start,fields)])
      else:
          return list([list(i) for i in self.__rst.GetRows(start)])
        

    

class AdoStream:
  def __init__(self):
      pass


class DbInfo:
  def __init__(self):
      self.__conn=None
      self.__cat=win32com.client.Dispatch('ADOX.Catalog')

  def setConnection(self,con):
      self.__cat.ActiveConnection=con

  def getDbTables(self):
      """
         Devuelve una lista con los nombres de todas
         las tablas de la base de datos que se le pasa
         como parametro
      """
      self.tables=[]
      #print self.__cat.Tables.Count

      for self.i in range (self.__cat.Tables.Count):
        #print str(self.__cat.Tables.Item(self.i).Name)
        self.tables.append(str(self.__cat.Tables.Item(self.i).Name))
      return self.tables


  def getTableColumns(self,table):
      """
         Devuelve una lista con los nombres de todas
         las columnas de la tabla que se le pasa
         como parametro
      """      
      self.columns=[]
      #print self.__cat.Tables.Item(table).Columns.Count

      for self.i in range (self.__cat.Tables.Item(table).Columns.Count):
        #print str(self.__cat.Tables.Item(table).Columns.Item(self.i).Name.encode("ascii","replace"))
        self.columns.append(str(self.__cat.Tables.Item(table).Columns.Item(self.i).Name.encode("ascii","replace")))
      return self.columns     

  def getColumnProps(self,table,col):
      """
         Hay que coger:Tipo de campo,atributos(coleccion) y DefinedSize
      """

      self.colProps=[]
      print(adoTypes[self.__cat.Tables.Item(table).Columns.Item(col).Type])
      print(self.__cat.Tables.Item(table).Columns.Item(col).DefinedSize)      

      #for self.i in range (self.__cat.Tables.Item(table).Columns.Item(col).Properties.Count):
      print(str(adoColTypes[self.__cat.Tables.Item(table).Columns.Item(col).Attributes]))
        #self.columns.append(str(self.__cat.Tables.Item(self.i).Name))
      #return self.columns       




if __name__=='__main__':
  print('Codigo de prueba')
  con=Connection("DRIVER={sql server};server=agave;Database=OpenConf;UID=sa;PWD=ci5000",1).getConnection()
  rst=Recordset()
  #rst.setCursor('adOpenUnspecified')
  #rst.setCursorLocation(adoCursorLocation['adUseClient'])
  rst.open('select top 10 * from ana',con)#abr,nombre,naso,uniconv from ana',con)
  print(rst.getRows())
  rst.close()
  








      