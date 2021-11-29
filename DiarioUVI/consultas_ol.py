#Configuracion
anas_defined = """select abr,nombre from openconf.dbo.ana"""
organismos_defined = """select abr,nombre from openconf.dbo.microorganismos"""


pac_pendientes="""
SELECT pet.fecha,
pet.id,
pet.estado,
resul.vdic as resultado,
pet.diag as observaciones,
pet.dataanal as danal
 from Pet,pac,resul
 where pet.TIPO=25  
and pet.pac=(select nid from pac where nhisto='{0}') 
and pet.pac=pac.nid 
and resul.pet=pet.nid
order by pet.fecha desc;
"""

#Para coger los resultados de peticiones de micro por nhisto

resmicro="""
select resul.pet,resul.vmemo from resul where resul.pet in
 (select nid from pet 
 where pet.tipo=25 
 and pet.pac=(select nid from pac where nhisto='{0}'));
"""

#Obtiene todos los aislamientos de uno o mas pacientes
aislam_str="""
select Pet.fecha,
Pet.id,
Pet.estado,
openconf.dbo.muestras.nombre as muestra,
openconf.dbo.microorganismos.nombre as aislamiento,
resorganismos.ufcs,
resorganismos.obs as observaciones,
Resorganismos.nid from ResOrganismos, openconf.dbo.microorganismos,
openconf.dbo.muestras,
Pet where
 ResOrganismos.pac=(select nid from Pac where Pac.nhisto='{0}')
 and Pet.nid=ResOrganismos.pet
 and ResOrganismos.organismo=openconf.dbo.microorganismos.nid
 and ResOrganismos.muestra=openconf.dbo.muestras.nid
order by ResOrganismos.fcrea desc;"""

connstr="DRIVER={sql server};server=openlabdb.intranet.net;Database=OpenData;UID=openlab;PWD=Pat1t0degoma"

posmicro_colnames=["fcrea","ana","idee","nhisto","servicio","nombre","apell1","apell2","muestra","organismo","ufcs","observ"]

posmicro_string="""
    select opendata.dbo.resorganismos.fcrea,openconf.dbo.ana.abr as ana,
    opendata.dbo.pet.idee,
    opendata.dbo.pac.nhisto,
    openconf.dbo.ser.nombre as servicio,
    opendata.dbo.pac.nombre,
    opendata.dbo.pac.apell1,
    opendata.dbo.pac.apell2,
    openconf.dbo.muestras.abr as muestra,
    openconf.dbo.microorganismos.nombre as organismo,
    opendata.dbo.resorganismos.ufcs,
    opendata.dbo.resorganismos.obs
     from opendata.dbo.resorganismos,opendata.dbo.pac,
    openconf.dbo.ana,openconf.dbo.microorganismos,
    opendata.dbo.pet,openconf.dbo.muestras,
    openconf.dbo.ser
    where opendata.dbo.resorganismos.fcrea  between '{0}' and '{1}'  
    and opendata.dbo.resorganismos.pac=opendata.dbo.pac.nid
    and opendata.dbo.resorganismos.pet=opendata.dbo.pet.nid
    and opendata.dbo.resorganismos.muestra=openconf.dbo.muestras.nid
    and opendata.dbo.resorganismos.estudio=openconf.dbo.ana.nid
    and opendata.dbo.resorganismos.organismo=openconf.dbo.microorganismos.nid
    and opendata.dbo.pet.serv1=openconf.dbo.ser.nid
    order by opendata.dbo.resorganismos.fcrea;
"""

#Consultas para historico de un paciente

#Obtiene el antibiograma de un aislamiento
atb_string="""
select
resorganismo, 
openconf.dbo.antibioticos.nombre,
sensibilidad, 
cmi from ResAntibioticos,
openconf.dbo.antibioticos
 where resorganismo in ({0})
and openconf.dbo.antibioticos.nid=resantibioticos.antibiotico;"""

#Obtiene todos los analisis no de micro asociados a un paciente
anas_from_interest=["CREA","HB","HEM","LEU","PLQ"]

anas_from_pac="""
select fechapet,pet.id,openconf.dbo.ana.abr,vnum,vdic,vmemo,resul.estado 
 from resul,pet,openconf.dbo.ana
 where pet.pac=(select nid from pac where pac.nhisto='{0}')
and resul.ana=openconf.dbo.ana.nid
and resul.pet=pet.nid
and openconf.dbo.ana.abr in ('CREA','PCR','PROCALC','HB','LEU','PLQ') 
order by fechapet desc,abr asc"""

#Simplificada y restringida a 20 analiticas
anas_from_pac20="""
select top 20 fechapet as fecha,pet.id as peticion,openconf.dbo.ana.abr as determinacion,vnum as resultado 
 from resul,pet,openconf.dbo.ana
 where pet.pac=(select nid from pac where pac.nhisto='{0}')
and resul.ana=openconf.dbo.ana.nid
and resul.pet=pet.nid
and openconf.dbo.ana.abr in ('CREA','PCR','PROCALC','HB','LEU','PLQ') 
order by fechapet desc,abr asc"""
