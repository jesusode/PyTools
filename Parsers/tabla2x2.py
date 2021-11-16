# Calculo de parametros de pruebas diagnosticas
#
#La funcion espera los datos como una lista de listas con dos columnas:
#       ref+    ref-
#test+   a       b
#test-   c       d
#
#[[a,b][c,d]]
#
#Valor de kappa     Fuerza de la concordancia
#  < 0.20                Pobre
#  0.21 – 0.40           Debil
#  0.41 – 0.60           Moderada
#  0.61 – 0.80           Buena
#  0.81 – 1.00           Muy buena
#
#
#Claves:
#a:Verdaderos positivos (VP): enfermos con la prueba positiva
#b: Falsos positivos (FP): no enfermos con la prueba positiva
#c: Falsos negativos (FN): enfermos con la prueba negativa
#d:Verdaderos negativos (VN): no enfermos con la prueba negativa
#a + c: Casos con patron de referencia positivo (enfermos)
#b + d: Casos con patron de referencia negativo (no enfermos)
#a + b: Casos con la prueba diagnostica positiva
#c + d: Casos con la prueba diagnostica negativa
#Sensibilidad (Se) = a / (a + c)
#Especificidad (Es) = d / (b + d)
#Valor predictivo positivo (VPP) = a / (a + b)
#Valor predictivo negativo (VPN) = d / (c + d)
#Cociente de probabilidad (CP) positivo = Se / (1 – Es)
#Cociente de probabilidad negativo = (1 – Se) / Es
#Probabilidad preprueba(prevalencia) (Ppre) = (a + c) / (a + b + c + d)
#Odds preprueba (odds pre) = Ppre / (1 – Ppre)
#Odds posprueba (odds post) = CP positivo x odds pre
#Probabilidad postprueba (Ppost) = odds post / (1 + odds post)
#
#
#
#
import math 
def  calcConting2x2 (data):
  assert type(data) == type([])
  assert len(data) == 2

    #Calcular variables
  a = data[0][0]
  b = data[0][1]
  c = data[1][0]
  d = data[1][1]
  TotTestP = a + b
  TotTestN = c + d
  TotRefP = a + c
  TotRefN = b + d
  Total = a + b + c + d
  VP = a
  FP = b
  FN = c
  VN = d

    #Validez o proporcion de aciertos
  Val = (VP + VN) / Total

    #Sensibilidad
  Sens = VP / TotRefP

    #Especificidad
  Spec = VN / TotRefN

    #Valor Predictivo Positivo
  VPP = VP / (VP + FP)

    #Valor Predictivo Negativo
  VPN = VN / (VN + FN)

    #Cociente de Probabilidad Positivo(razon de verosimilitud)
  CPP = Sens / (1 - Spec)

    #Cociente de Probabilidad Negativo
  CPN = (1 - Sens) / Spec

    #Probabilidad preprueba(prevalencia estimada)
  Ppre = (a + c) / (a + b + c + d)

    #Odds preprueba
  odds_pre = Ppre / (1 - Ppre)

    #Odds Postprueba
  odds_post = CPP * odds_pre

    #Probabilidad Postprueba
  Ppost = odds_post / (1 + odds_post)

    #Indice Kappa-----------------------------------------------------------------------------

    #Probabilidad de que ambos esten de acuerdo en los mismos resultados al azar(la diagonal)
  concord_observ = (a + d) / Total

    #Valores esperados para cada casilla
  a_esp = (TotTestP * TotRefP) / Total
  b_esp = (TotTestP * TotRefN) / Total
  c_esp = (TotTestN * TotRefP) / Total
  d_esp = (TotTestN * TotRefN) / Total
  concord_esper = (a_esp + d_esp) / Total

    #print("Concordancia observada: " + concord_observ);

    #print("Concordancia esperada: " + concord_esper);
  kappa = (concord_observ - concord_esper) / (1 - concord_esper)

    #print("IC95Kappa: " + str(IC95prop(kappa,Total)));
  ksens = (Sens - a_esp / TotRefP) / (1 - a_esp / TotRefP)

    #print("KSens: " + ksens);
  kesp = (Spec - d_esp / TotRefN) / (1 - d_esp / TotRefN)

    #print("KEsp: " + kesp);

    #Indice de Youden(indica la diferencia entre la tasa de VP y FP)
  IJ = Sens - (1 - Spec)

    #-----------------------------------------------------------------------------------------
  results = {} 
  results["VP"] = VP
  results["FP"] = FP
  results["VN"] = VN
  results["FN"] = FN
  results["TotTestP"] = TotTestP
  results["TotTestN"] = TotTestN
  results["TotRefP"] = TotRefP
  results["TotRefN"] = TotRefN
  results["Total"] = Total
  results["Val"] = Val
  results["ValIC95"] = IC95prop(Val, Total)
  results["Sens"] = Sens
  results["SensIC95"] = IC95prop(Sens, TotRefP)
  results["Spec"] = Spec
  results["SpecIC95"] = IC95prop(Spec, TotRefN)
  results["VPP"] = VPP
  results["VPPIC95"] = IC95prop(VPP, VP + FP)
  results["VPN"] = VPN
  results["VPNIC95"] = IC95prop(VPN, VN + FN)
  results["kappa"] = kappa
  results["KEsp"] = kesp
  results["KSens"] = ksens
  results["CPP"] = CPP
  results["CPN"] = CPN
  results["Ppre"] = Ppre
  results["PpreIC95"] = IC95prop(Ppre, Total)
  results["odds_pre"] = odds_pre
  results["odds_post"] = odds_post
  results["Ppost"] = Ppost
  results["PpostIC95"] = IC95prop(Ppost, Total)
  results["IJ"] = IJ
  return results

def  describeResults (dic):
  report = ""
  report += "Total: " + str(dic["Total"]) + "\n"
  report += "Verdaderos positivos: " + str(dic["VP"]) + "\n"
  report += "Falsos Positivos: " + str(dic["FP"]) + "\n"
  report += "Veraderos Negativos: " + str(dic["VN"]) + "\n"
  report += "Falsos Negativos: " + str(dic["FN"]) + "\n"
  report += "Total Test Positivo: " + str(dic["TotTestP"]) + "\n"
  report += "Total Test Negativo: " + str(dic["TotTestN"]) + "\n"
  report += "Total Referencia Positivo: " + str(dic["TotRefP"]) + "\n"
  report += "Total Referencia Negativo: " + str(dic["TotRefN"]) + "\n"
  report += "Validez: " + str(dic["Val"]) + "\n"
  report += "IC95 Validez: " + str(dic["ValIC95"]) + "\n"
  report += "Sensibilidad: " + str(dic["Sens"]) + "\n"
  report += "IC95 Sensibilidad: " + str(dic["SensIC95"]) + "\n"
  report += "Especificidad: " + str(dic["Spec"]) + "\n"
  report += "IC95 Especificidad: " + str(dic["SpecIC95"]) + "\n"
  report += "Valor Predictivo Positivo: " + str(dic["VPP"]) + "\n"
  report += "IC95 VPP: " + str(dic["VPPIC95"]) + "\n"
  report += "Valor Predictivo Negativo: " + str(dic["VPN"]) + "\n"
  report += "IC95 VPN: " + str(dic["VPNIC95"]) + "\n"
  report += "Indice Kappa: " + str(dic["kappa"]) + "\n"
  report += "Indice Kappa Sensibilidad: " + str(dic["KSens"]) + "\n"
  report += "Indice Kappa Especificidad: " + str(dic["KEsp"]) + "\n"
  report += "Cociente de Probabilidad Positivo: " + str(dic["CPP"]) + "\n"
  report += "Cociente de Probabilidad Negativo: " + str(dic["CPN"]) + "\n"
  report += "Probabilidad Preprueba: " + str(dic["Ppre"]) + "\n"
  report += "IC95 Ppre(prevalencia): " + str(dic["PpreIC95"]) + "\n"
  report += "Odds Preprueba: " + str(dic["odds_pre"]) + "\n"
  report += "Odds Postprueba: " + str(dic["odds_post"]) + "\n"
  report += "Probabilidad Postprueba: " + str(dic["Ppost"]) + "\n"
  report += "IC95 Ppost: " + str(dic["PpostIC95"]) + "\n"
  report += "Indice de Youden: " + str(dic["IJ"]) + "\n"
  return report

def  IC95prop (p, tot):
  aux = 1.96 * math.sqrt((p * (1 - p)) / tot)
  return [p - aux, p + aux]

def  ajustarVP (sens, esp, prev):
  VPP = (sens * prev) / (sens * prev + (1 - esp) * (1 - prev))
  VPN = (esp * (1 - prev)) / ((1 - sens) * prev + esp * (1 - prev))
  return [VPP, VPN]

print(describeResults(calcConting2x2([[81, 160], [21, 427]])))
print("------------------------------------------")
print(ajustarVP(0.79, 0.71, 0.01))
