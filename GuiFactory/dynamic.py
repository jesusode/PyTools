from typing import *

#----------------------------------------------------------------
tkinter_table={
  'label' : '{0}=tkinter.Label({1}{2})',
  'button' : '{0}=tkinter.Button({1}{2})',
  'textbox' : '{0}=tkinter.Entry({1}{2})',
  'textarea' : '{0}=tkinter.Text({1}{2})',
  'panel' : '{0}=tkinter.Panel({1}{2})',
  'frame' : '{0}=tkinter.Frame({1}{2})',
  'listbox' : '{0}=tkinter.Listbox({1}{2})',
  'spinbox' : '{0}=tkinter.Spinbox({1}{2})',
  'image' : '{0}=tkinter.PhotoImage({1}{2})',
  'canvas' : '{0}=tkinter.Canvas({1}{2})',
  'stringvar' : '{0}=tkinter.StringVar()',
  'intvar' : '{0}=tkinter.IntVar()',
  'doublevar' : '{0}=tkinter.DoubleVar()',
  'boolvar' : '{0}=tkinter.BooleanVar()',
  'check' : '{0}=tkinter.Checkbutton({1}{2})',
  'option' : '{0}=tkinter.OptionMenu({1}{2})',
  'scale' : '{0}=tkinter.Scale({1}{2})',
  'radio' : '{0}=tkinter.Radiobutton({1}{2})',
  'scroll' : '{0}=tkinter.Scrollbar({1}{2})',
  'menu' :  '{0}=tkinter.Menu({1}{2})',
  'menuitem' : '{0}=tkinter.Menubutton({1}{2})',
  'combobox' : '{0}=ttk.Combobox({1}{2})',
  'notebook' : '{0}=ttk.Notebook({1}{2})',
  'progressbar' : '{0}=ttk.Progressbar({1}{2})',
  'separator' : '{0}=ttk.Separator({1}{2})',
  'sizegrip' : '{0}=ttk.Sizegrip({1}{2})',
  'treeview' : '{0}=ttk.treeview({1}{2})'
}

wx_table={
  'label' : '%s=wx.StaticText(',
  'button' : '%s=wx.Button(',
  'textbox' : '%s=wx.TextCtrl(',
  'textarea' : '%s=wx.TextCtrl(',
  'panel' : '%s=wx.Panel(',
  'listbox' : '%s=wx.ListBox(',
  'checklistbox' : '%s=wx.CheckListBox(',
  'spinbox' : '%s=wx.SpinCtrl(',
  'image' : '%s=wx.Image(',
  'bitmap' : '%s=wx.Bitmap(',
  'icon' : '%s=wx.Icon(',
  'check' : '%s=wx.CheckBox(',
  'scale' : '%s=wx.Scale(',
  'radio' : '%s=wx.RadioButton(',
  'radiobox' : '%s=wx.RadioBox(',
  'slider' : '%s=wx.Slider(',
  'topmenu' : '%s=wx.MenuBar(',
  'menu' :  '%s=wx.Menu(',
  'menuitem' : '%s=wx.MenuItem(',
  'combobox' : '%s=wx.ComboBox(',
  'progressbar' : '%s=wx.Gauge(',
  'separator' : '%s.AppendSeparator(',
  'treeview' : '%s=treeFactory(',
  'tablebox' : '%s=tableFactory(',
  'font' : '%s=wx.Font(',
  'splitter' : '%s=wx.SplitterWindow(',
  'boxsizer' : '%s=wx.BoxSizer(',
  'gridsizer' : '%s=wx.GridSizer(',
  'flexgridsizer' : '%s=wx.FlexGridSizer(',
  'gridbagsizer' : '%s=wx.GridBagSizer(',
  'staticboxsizer' : '%s=wx.StaticBoxSizer(',
  'splitter' : '%s=wx.SplitterWindow(',
  'grid' : '%s=gridFactory(',
  'htmlbox' : '%s=htmlWinFactory(',
  'taskbar' : '%s=MinimalTaskBarIcon(',
  'datepicker' : '%s=wx.DatePickerCtrl(',
  'notebook' : '%s=wx.Notebook(',
  'sashwin' : '%s=wx.SashLayoutWindow(',
  'platebutton' : '%s=wx.lib.platebtn.PlateButton(',
  'linkbutton' : '%s=wx.CommandLinkButton(',
  'aquabutton' : '%s=wx.lib.agw.aquabutton.AquaButton(',
  'colourbutton' : '%s=wx.lib.colourselect.ColourSelect(',
  'hyperlink' : '%s=wx.lib.agw.hyperlink.HyperLinkCtrl(',
  'webbrowser' : '%s=wx.html2.WebView.New(',
  'captionbox' : '%s=captionBoxFactory(', #??
  'dialog' : '%s=wx.Dialog(',
  'collapsiblepanel' : '%s=wx.CollapsiblePane(',
  'floatwindow' : '%s=FloatWin(',
  'filebrowsebutton' : '%s=wx.lib.filebrowsebutton.FileBrowseButton(',
  'dirbrowsebutton' : '%s=wx.lib.filebrowsebutton.DirBrowseButton(',
  'line' : '%s=wx.StaticLine(',
  'space' : '',
  'listbook' : '%s=wx.Listbook(',
  'imagelist' : '%s=wx.ImageList(',
  'fontenumerator' : '%s=wx.FontEnumerator(',
  'searchcontrol' : '%s=wx.SearchCtrl('
}

xhtml_table={
    'label' : '<span id="%s" %s>%s</span>',
    'button' : '<input type="button" name="%s" id="%s" %s/>',
    'textbox' : '<input type="text" name="%s" id="%s" %s/>',
    'textarea' : '<textarea name="%s" id="%s" %s>%s</textarea>',
    'frame' : '<iframe id="%s" %s></iframe>',
    'form' : '<form id="%s" %s></form>',
    'listbox' : '<select multiple id="%s" name="%s" %s>%s</select>',
    'image' : '<img id="%s" %s/>',
    'check' : '<input type="checkbox" name="%s" id="%s" %s/>',
    'option' : '<option value="%s">%s</option>',
    'radio' : '<input type="radio" name="%s" id="%s" %s/><span id="radiovalue">%s</span>',
    'combobox' : '<select id="%s" name="%s" %s>%s</select>',
    'tablebox' : '<table id="%s" %s>%s</table>',
    'submit' : '<input type="submit" name="%s" id="%s" %s/>',
    'hidden' : '<input type="hidden" name="%s" id="%s" %s/>',
    'password' : '<input type="password" name="%s" id="%s" %s/>',
    'link' : '<a id="%s" %s>%s</a>',
    'raw' : '<div id="%s" %s>%s<div>',
    'file' : '<input type="file" name="%s" id="%s" %s/>',
    'color' : '<input type="color" name="%s" id="%s" %s/>',
    'date' : '<input type="date" name="%s" id="%s" %s/>',
    'datetime' : '<input type="datetime" name="%s" id="%s" %s/>',
    'datetime-local': '<input type="datetime-local" name="%s" id="%s" %s/>',
    'email' : '<input type="email" name="%s" id="%s" %s/>',
    'month' : '<input type="month" name="%s" id="%s" %s/>',
    'number' : '<input type="number" name="%s" id="%s" %s/>',
    'range' : '<input type="range" name="%s" id="%s" %s/>',
    'search' : '<input type="search" name="%s" id="%s" %s/>',
    'tel' : '<input type="tel" name="%s" id="%s" %s/>',
    'time' : '<input type="time" name="%s" id="%s" %s/>',
    'url' : '<input type="url" name="%s" id="%s" %s/>',
    'pattern' : '<input type="pattern" name="%s" id="%s" %s/>',
    'week' : '<input type="week" name="%s" id="%s" %s/>'
}

pyQt_table = {}
#---------------------------------------------------

TABLES = {
    "wxPython" : wx_table,
    "PyQt" : pyQt_table,
    "tkinter" : tkinter_table,
    "xhtml" : xhtml_table
}


def addTable(name : str, table : Dict[str,str]) -> NoReturn:
    '''
    addTable
    --------
    Añade una tabla a TABLES.
    '''
    TABLES[name] = table


def tkinterWidgetFromTable(widget : str,name : str, parent: str, props : Dict[str,str] = {}):
    assert widget in tkinter_table
    fstr=tkinter_table[widget]
    if '{1}{2}' in fstr:
        if props!={}:
            prps = ",".join([f"{x}='{y}'" for x,y in props.items()])
            return fstr.format(name,parent,"," + prps)
        else:
            return fstr.format(name,parent,"")
    else:
        return fstr.format(name)



FACTORIES = {
    "tkinter" : tkinterWidgetFromTable
}

def addFactory(name : str, factory : Callable) -> NoReturn:
    '''
    addFactory
    --------
    Añade una factoría a FACTORIES.
    '''
    FACTORIES[name] = factory
  