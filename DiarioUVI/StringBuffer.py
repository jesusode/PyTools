import io

#------------------------------------------------------------------------------
#Clase que envuelve un StringBuffer
#El contenido del buffer se obtiene con una llamada al mismo sin argumentos
#Para poner strings en el buffer se pude usar el operador +
# que admite un string o bien otro StringBuffer,
#o un llamada con tantos argumentos como se quieran meter en el buffer
#------------------------------------------------------------------------------ 

class StringBuffer:
    def __init__(self,*vals):
        self._sb= io.StringIO()
        self._encoding='utf-8'
        if vals!=(): 
            for item in vals:
                if type(item)==str:
                    self._sb.write(item)
                elif isinstance(item,StringBuffer):
                    self._sb.write(item._collect())
                else:
                    self._sb.write(str(item))
        self.__canCollect=True

    def getEncoding(self):
        return self._encoding

    def setEncoding(self,enc):
        self._encoding=enc

    def _canCollect(self):
        return self.__canCollect

    def __add__(self,astr):
        if self._canCollect():
            if type(astr) in [str,str]:
                self._sb.write(str(astr))
            elif isinstance(astr,StringBuffer):
                self._sb.write(str(astr._collect()))
            else:
                self._sb.write(str(astr))

    def __call__(self,*args):
        if args!=():
            for item in args:
                if type(item) in [str,str]:
                    self._sb.write(str(item))
                elif isinstance(item,StringBuffer):
                    self._sb.write(str(item._collect()))
                else:
                    self._sb.write(str(item))
            return ""
        else:
            return self._collect()

    def _collect(self):
        if self._canCollect():
            self.__canCollect=False
            return self._sb.getvalue()
        else:
            raise Exception("Error: This StringBuffer has been collected yet!")

#---------------------------------------------------------------------------------------------------
