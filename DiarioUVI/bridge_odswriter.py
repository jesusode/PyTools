import odswriter
import os

def listToOds(fname,headers,_list,sheet=""):
    #escribir headers si se ha pasado
    ods=odswriter.writer(open(fname,"wb"))
    active=ods
    #Crear sheet si esta definido
    if sheet!="" :
        sht=ods.new_sheet(sheet)
        active=sht
    if headers!=[] :
        active.writerow(headers)
    for item in _list:
        active.writerow(item)
    ods.close()


def createOds(name):
    return odswriter.writer(open(name,"wb"))


def createSheet(ods,sname):
    return ods.new_sheet(sname)


def odsWrite(ods_or_sheet,row,multiple=False):
    if multiple== True :
        ods_or_sheet.writerows(row)
    else:
        ods_or_sheet.writerow(row)
    return 1


def odsWriteFormula(ods,formula):
    ods.writerow([odswriter.Formula(formula)])
    return 1


def odsClose(ods):
    ods.close()
    return 1
    


# #Pruebas:(no se puede reabrir un archivo, lo sobreescribe, tanto con wb como con ab
# setvar f,h,l,s,x,s1,s2,s3
# h=["header 1","header 2","header 3"]
# l=[[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15]]
# listToOds("zzzzz.ods",h,l,"minimal rules!")
# listToOds("zzzzz2.ods",h,l)
# s=createOds("zzzz3.ods")
# s1=createSheet(s,"hoja 1")
# s2=createSheet(s,"hojilla 2")
# s3=createSheet(s,"hojula 3")
# odsWrite(s1,h)
# odsWrite(s2,h)
# odsWrite(s2,l,true)
# odsWrite(s3,l,true)
# odsWrite(s3,["Total:"])
# odsWriteFormula(s3,"=(A1+A2+A3+A4+A5)")
# s.close()
# print("Terminado")