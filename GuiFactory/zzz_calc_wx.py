
import sys
import wx
import wx.grid
import wx.html
import wx.html2
from wx_support import *


#Soporte para obtener GUIElements por nombre---------------

__WIDGETS__ = dict()
def getGUIElement(name):
    if name in __WIDGETS__:
        return __WIDGETS__[name]
    else:
        return None

def registerGUIElement(name,elem):
    __WIDGETS__[name] = elem

def collectValues():
    pass
#----------------------------------------------------------

app = wx.App()


#User code
def salir(evt):
    frame1.Destroy()

def calcular(evt):
    c = operand.GetValue().strip()
    if c == "+":
        result.SetValue(str(float(oper1.GetValue()) + float(oper2.GetValue())))
    elif c == "-":
        result.SetValue(str(float(oper1.GetValue()) - float(oper2.GetValue())))
    elif c == "*":
        result.SetValue(str(float(oper1.GetValue()) * float(oper2.GetValue())))
    elif c == "/":
        result.SetValue(str(float(oper1.GetValue()) / float(oper2.GetValue())))
    else:
        raise "Error: invalid operand"

frame1 = wx.Frame(parent = None,title = "Simple Calculator")
registerGUIElement('frame1',frame1)


loper1 = wx.StaticText(parent = frame1,label = "Operando 1: ")
registerGUIElement('loper1',loper1)


oper1 = wx.TextCtrl(parent = frame1,value = "0")
registerGUIElement('oper1',oper1)


loperand = wx.StaticText(parent = frame1,label = "Operador: ")
registerGUIElement('loperand',loperand)


operand = wx.ComboBox(frame1,value="+",choices=["+","-","*","/"],style=wx.CB_DROPDOWN)
registerGUIElement('operand',operand)


loper2 = wx.StaticText(parent = frame1,label = "Operando 2: ")
registerGUIElement('loper2',loper2)


oper2 = wx.TextCtrl(parent = frame1,value = "0")
registerGUIElement('oper2',oper2)


lresult = wx.StaticText(parent = frame1,label = "Resultado: ")
registerGUIElement('lresult',lresult)


result = wx.TextCtrl(parent = frame1,value = "0")
registerGUIElement('result',result)


btn1 = wx.Button(parent = frame1,label = "Calcular")
registerGUIElement('btn1',btn1)


btn2 = wx.Button(parent = frame1,label = "Salir")
registerGUIElement('btn2',btn2)


sizer1 = wx.GridSizer(rows=5, cols=2, hgap=5, vgap=5)
registerGUIElement('sizer1',sizer1)
sizer1.Add(loper1, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(oper1, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(loperand, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(operand, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(loper2, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(oper2, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(lresult, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(result, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(btn1, proportion=0, flag=wx.EXPAND, border=3)
sizer1.Add(btn2, proportion=0, flag=wx.EXPAND, border=3)



btn1.Bind(wx.EVT_BUTTON,calcular);
btn2.Bind(wx.EVT_BUTTON,salir);

frame1.SetSizer(sizer1);
frame1.Show();

app.MainLoop()
