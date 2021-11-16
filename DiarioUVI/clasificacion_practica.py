#clasificacion practica de atbs de cara al PROA

from typing import *

clasificacion_atbs : Dict[str,List[str]] = {

    "quinolonas" : ["ciprofloxacino", "levofloxacino","moxifloxacino","norfloxacino"],
    "cefalosporinas" : ["ceftriaxona","cefotaxima","ceftazidima","cefepime",
                "cefuroxima","cefuroxima-axetilo","cefazolina","cefixima"],
    "cefalosporinas+inhibidores" : ["ceftazidima/avibactam", "ceftolozano/tazobactam"],
    "carbapenems" : ["imipenem", "meropenem","ertapenem"],
    "carbapenems+inhibidores" : ["merpenem/vaborbactam"],
    "penicilinas" : ["penicilina","penicilinag","penicilinav","cloxacilina"],
    "penicilinas+inhibidores" : ["amoxicilina/clavulanico","amoxicilina+clavulanico",
                      "piperacilina/tazobactam","piperacilina+tazobactam"],
    "monobactamas" : ["aztreonam"],
    "tetraciclinas" : ["tetraciclina", "doxiciclina","tigeciclina"],
    "macrolidos-lincosamidas" : ["eritromicina","clindamicina","azitromicina",
                    "claritromicina"],
    "glicopeptidos" : ["vancomicina","teicoplanina"],
    "lipopeptidos" : ["daptomicina"],
    "imidazoles" : ["linezolid","tedizolid"],
    "aminoglucosidos" : ["gentamicina","tobramicina","amikacina",
                   "estreptomicina","neomicina","netilmicina","kanamicina"],
    "sulfonamidas" : ["cotrimoxazol","sxt"]
}


def clasificar(atb : str) -> str :
    atb = atb.lower().replace(" ","").strip().strip("\n")
    for familia in clasificacion_atbs:
        if atb in clasificacion_atbs[familia]:
            return familia
    return ""


if __name__ == '__main__':
    print(clasificar("daptomicina"))
    print(clasificar("MEROPENEM "))
    print(clasificar("chocholoco"))