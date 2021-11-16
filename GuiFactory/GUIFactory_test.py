'''
Clases y funciones para crear GUIs
segun descriptor XML.
'''
import GuiFactory
from GuiFactory.dynamic import *
from GuiFactory.factory import renderAppDescriptor,compileCode,readf
#from GuiFactory.templates import getTemplate


import tkinter

guielems2="""<?xml version="1.0" ?>
<appDescriptor>
    <application name="zzz_pruebas_wx" lang="wx">
        <initCode href="init_code.txt" />
        <widgets>
            <widget class="wx.Frame" name="frame1">
                <elements>
                </elements>
                <properties>
                    <property parent="None" />
                    <property title='"My Cool Frame"' />
                    <property BackgroundColour="wx.RED" />
                    <property ForegroundColour="wx.BLUE" />
                </properties>
            </widget>
            <widget class="wx.TextCtrl" name="txt1">
                <elements>
                </elements>
                <properties>
                    <property parent="frame1" />
                    <property value='"Valor Inicial"' />
                </properties>
            </widget>
            <widget class="wx.Button" name="btn1">
                <elements>
                </elements>
                <properties>
                    <property parent="frame1" />
                    <property label='"Push Me!"' />
                </properties>
            </widget>
            <widget class="wx.BoxSizer" name="sizer1">
                <elements>
                    <element name="txt1" proportion="0" flag="wx.EXPAND" border="3" />
                    <element name="btn1" proportion="3" flag="wx.EXPAND" border="3" />
                </elements>
                <properties>
                    <property constructor="wx.VERTICAL" />
                </properties>
            </widget>
        </widgets>
        <events>
            <event name="wx.EVT_CLOSE" for="frame1" code="onExitFrame"/>
        </events>
        <postWidgetsCode href="postwidgets_code.txt" />
    </application>
</appDescriptor>"""



tkinterd="""<?xml version="1.0" ?>
<appDescriptor>
    <application name="zzz_pruebas_tkinter" lang="tkinter">
        <initCode href="init_code_tk.txt" />
        <menus>
            <menubar parent="" name="main_menu" text="" tearoff = "0"/>
            <menubar parent="main_menu" name="filemenu" text="Archivo" tearoff = "0"/>
            <menubar parent="main_menu" name="editmenu" text="Editar" tearoff = "0"/>
            <menubar parent="main_menu" name="helpmenu" text="Ayuda" tearoff = "0"/>
            <menuitem parent="filemenu" kind="text" text="Abrir" code="onOpenFile" image="" accelerator="Ctrl+O" />
            <menuitem parent="filemenu" kind="separator" text="" code="" image="" accelerator=""/>
            <menuitem parent="filemenu" kind="text" text="Salir" code="onExit" image="" accelerator="Ctrl+S"/>
            
        </menus>
        <widgets>
            <widget class="Frame" name="frame1">
                <elements>
                </elements>
                <properties>
                    <property parent="root" />
                    <property bg="blue"/>
                </properties>
            </widget>
            <widget class="ttk.Entry" name="txt1">
                <elements>
                </elements>
                <properties>
                    <property parent="frame1" />
                    <property text="Valor Inicial" />
                </properties>
            </widget>
            <widget class="ttk.Button" name="btn1">
                <elements>
                </elements>
                <properties>
                    <property parent="frame1" />
                    <property text="Push Me!" />
                </properties>
            </widget>
            <widget class="Button" name="btn2">
                <elements>
                </elements>
                <properties>
                    <property parent="frame1" />
                    <property text="Another one!" />
                    <property bg="red"/>
                    <property fg="white"/>
                    <!--<property font="Arial 44 bold"/>-->
                    <property font="JohnDoe 24 bold"/>
                </properties>
            </widget>
            <widget class="Sheet" name="sheet1">
                <elements>
                </elements>
                <properties>
                    <property constructor="frame1,data=[[1,2,3],[4,5,6]]" />
                </properties>
            </widget>
        </widgets>
        <events>
            <!--<event name="WM_DELETE_WINDOW" for="root" code="onExitFrame"/>-->
            <event name="Button-1" for="btn1" code="onBtnClicked"/>
            <!-- <event name="Enter" for="frame1" code="onBtnClicked"/> -->
        </events>
        <postWidgetsCode href="postwidgets_code_tk.txt"/>
    </application>
</appDescriptor>"""



#print("-------------------------------------------------------")

'''
n,l,code = renderAppDescriptor(guielems2,PyWxRenderer())
print(code)
with open(n + ".py","w") as f:
    f.write(wxPyAppTemplate.format(code))
    f.close()
'''

#n,l,m,t,i,code = renderAppDescriptor(readf("wxapps/webbrowser_wx_descriptor.xml"),"wx",True)
#n,l,m,t,i,code = renderAppDescriptor(readf("wxapps/calc_wx_descriptor.xml"),"wx",True)
#n,l,m,t,i,code = renderAppDescriptor(tkinterd,"tkinter",True)
n,l,m,t,i,code= renderAppDescriptor(readf('csv_visor_descriptor.xml','utf-8'),"tkinter",True)
print(code)



print(tkinterWidgetFromTable("button","btn1","frame1",{"font":"Arial 12 bold"}))
print(tkinterWidgetFromTable("textarea","text1","frame1",{"font":"Arial 12 bold"}))
exec(compileCode(tkinterWidgetFromTable("textarea","text2","None",{"font":"Arial 12 bold"})))
#print(help(text2))
print(text2)

print("Ok")


