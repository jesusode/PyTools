
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
def navigate(evt):
    browser.LoadURL(url.GetValue());


frame1 = wx.Frame(parent = None,title = "Simple Web Browser")
registerGUIElement('frame1',frame1)


panel1 = wx.Panel(parent = frame1)
registerGUIElement('panel1',panel1)


navigate_btn = wx.Button(parent = panel1,label = "Ir")
registerGUIElement('navigate_btn',navigate_btn)


url = wx.TextCtrl(parent = panel1,value = "http://www.google.com")
registerGUIElement('url',url)


spacer = wx.StaticText(parent = frame1,label = "")
registerGUIElement('spacer',spacer)
spacer.SetBackgroundColour(wx.WHITE)

browser = wx.html2.WebView.New(parent = frame1)
registerGUIElement('browser',browser)


sizer1 = wx.BoxSizer(wx.HORIZONTAL)
registerGUIElement('sizer1',sizer1)
sizer1.Add(navigate_btn, proportion=1, flag=wx.EXPAND, border=30)
sizer1.Add(url, proportion=6, flag=wx.EXPAND, border=30)


main_sizer = wx.BoxSizer(wx.VERTICAL)
registerGUIElement('main_sizer',main_sizer)
main_sizer.Add(panel1, proportion=0, flag=wx.EXPAND, border=30)
main_sizer.Add(spacer, proportion=0, flag=wx.EXPAND, border=30)
main_sizer.Add(browser, proportion=10, flag=wx.EXPAND, border=30)




navigate_btn.Bind(wx.EVT_BUTTON,navigate)
#sizer1.AddGrowableCol(1)
panel1.SetSizer(sizer1)
frame1.SetSizer(main_sizer)
browser.SetSize(800,600)
frame1.Show()
frame1.SetSize(800,600)


app.MainLoop()
