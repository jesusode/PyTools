import tkinter
import tkinter.font
import tkinter.ttk
import re
import copy
import webbrowser
import os

#from interprete import runMiniCode

class TtkMultiListbox(tkinter.ttk.Frame):
    def __init__(self, master,columns,lists,editable,callback,*opts,**kwopts ):
        tkinter.ttk.Frame.__init__(self, master,*opts,**kwopts)
        self.pack(fill='both', expand='yes')
        self.columns=columns
        #Copias de seguridad por si se necesitan------
        self.backup=copy.deepcopy(lists)
        self.filterbackup=[]
        self.tagsbackup=[]
        #---------------------------------------------
        self.lists=lists
        self.selected=[]
        self.selection=[]
        self.colopts=None
        self.editable=1
        if editable==0:
            self.editable=0
        
        self.tree = tkinter.ttk.Treeview(self,columns=self.columns, show="headings")
        vsb = tkinter.ttk.Scrollbar(self,orient="vertical", command=self.tree.yview)
        hsb = tkinter.ttk.Scrollbar(self,orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self)
        vsb.grid(column=1, row=0, sticky='ns', in_=self)
        hsb.grid(column=0, row=1, sticky='ew', in_=self)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_tree()
        self.tree.bind('<<TreeviewSelect>>',self.__getSelection)
        if self.editable!=0:
            self.tree.bind('<Double-Button-1>',self.__editCell)
        self.tree.bind('<Button-3>',self.__filterCell)
        self.tree.bind('<Key-Escape>',self.cancelFilter)        
        self._rw=-1
        self._cl=-1
        #Funcion del parent para notificarle cambios en la ordenacion-------
        self.callback=callback
        #-------------------------------------------------------------------
        #indice por el que se quiere filtrar
        self.filterindex=-1



    def setColOptions(self,opts_list):
        #Debe ser un lista de listas. La lista vacia hace que se muestre
        #un cuadro de texto al editar una celda
        #una lista con opciones hace que se muestren esas opciones en un combo
        for item in opts_list:
            if type(item)!=type([]):
                if item not in ['link','system','code']:
                    raise Exception('Error: todos los elementos de la lista deben ser listas, o bien uno de "link","system","code"')
        self.colopts=opts_list



    def restore(self):
        self.lists=copy.deepcopy(self.backup)#[:]
        self.tree.delete(*self.tree.get_children())
        for item in self.lists:
            self.tree.insert('', 'end', values=item)

    def sortby(self,tree, col, descending):
        """Sort tree contents when a column is clicked on."""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # reorder data
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        # switch the heading so that it will sort in the opposite direction
        tree.heading(col,
            command=lambda col=col: self.sortby(tree, col, int(not descending)))
        #Notificar el ordenamiento al parent
        if self.callback:
            self.callback()

    def _build_tree(self):
        
        for col in self.columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: self.sortby(self.tree, c, 0))
            # XXX tkFont.Font().measure expected args are incorrect according
            #     to the Tk docs
            self.tree.column(col, width=tkinter.font.Font().measure(col.title()))

        for item in self.lists:
            self.tree.insert('', 'end', values=item)

            # adjust columns lenghts if necessary
            for indx, val in enumerate(item):
                ilen = tkinter.font.Font().measure(val)
                if self.tree.column(self.columns[indx], width=None) < ilen:
                    self.tree.column(self.columns[indx], width=ilen)
            

    def createTag(self,name,options):
        self.tree.tag_configure(name,**options)

    def applyTags(self,item,tags,update=0):
        if update:
            oldtags=self.tree.item(item)['tags']
            if type(oldtags) in [type(''),type('')]:
                oldtags=oldtags.split(',')
            for tag in tags:
                if tag not in oldtags:
                    oldtags.append(tag)
            self.tree.item(item,tags=oldtags)
        else:
            self.tree.item(item,tags=tags)

    def getTags(self,item):
        return self.tree.item(item)['tags']

    def __getSelection(self,event=None):
        self.selection=self.tree.selection()
        self.selected=[self.tree.item(it)['values'] for it in self.selection]        
        #print self.selected


    def __editCell(self,event):
        self._rw=self.tree.identify_row(event.y)
        self._cl=self.tree.identify_column(event.x)
        if self._rw:
            #Desactivar el table
            x,y,w,h=self.tree.bbox(self._rw,self._cl)
            if self.colopts==None:
                tb=tkinter.ttk.Entry(self,foreground='red')
                tb.insert('end',self.tree.set(self._rw,self._cl))
            elif self.colopts[int(self._cl[1:])-1]in ['link','system','code']:
                if self.colopts[int(self._cl[1:])-1]=='link':
                    webbrowser.open(self.tree.set(self._rw,self._cl))
                elif self.colopts[int(self._cl[1:])-1]=='code':
                    exec(self.tree.set(self._rw,self._cl))                   
                else:
                    os.system(self.tree.set(self._rw,self._cl))
                return 'break'
            elif self.colopts[int(self._cl[1:])-1]==[]:
                tb=tkinter.ttk.Entry(self,foreground='red')
                tb.insert('end',self.tree.set(self._rw,self._cl))
            else:
                tb=tkinter.ttk.Combobox(self,values=self.colopts[int(self._cl[1:])-1])
            
            tb.bind('<Key-Return>',self.__doEdit)
            tb.bind('<Key-Escape>',self.__cancelEdit)
            tb.place(x=x,y=y,width=w,height=h)
            tb.focus_set()
            tb.grab_set()
           
    def __doEdit(self,event):
        val=event.widget.get()
        self.tree.set(self._rw,self._cl,val)
        event.widget.grab_release()
        event.widget.destroy()
        #Obligar a un refresco---------
        sel=self.getSelectedItems()
        self.deselect()
        self.tree.selection_set(sel)
        #------------------------------
        #Hay que actualizar tambien las listas!!!!
        self.lists[self.tree.index(self._rw)][int(self._cl[1:])-1]=val
        

    def dobackup(self):
        #hacer una copia de seguridad de los valores actuales-------------------------
        self.filterbackup=copy.deepcopy(self.lists)
        self.tagsbackup=copy.deepcopy([self.tree.item(it)['tags'] for it in self.tree.get_children()])
        #------------------------------------------------------------------------------        

    def __cancelEdit(self,event):
        event.widget.grab_release()
        event.widget.destroy()

    def __filterCell(self,event):
        #Si hay menos de una fila, no hacer nada
        if len(self.tree.get_children())>1:
            self.dobackup()
            self._rw=self.tree.identify_row(event.y)
            self._cl=self.tree.identify_column(event.x)
            if self._rw:
                #Desactivar el table
                x,y,w,h=self.tree.bbox(self._rw,self._cl)            
                #obtener para la columna los valores unicos
                uniques=[]
                self.filterindex=int(self._cl[1:])-1
                for el in self.tree.get_children():
                    item=self.tree.set(el,self.filterindex)
                    if not item in uniques:
                        uniques.append(item)
                uniques.sort()#Ordenarlos
                tb=tkinter.ttk.Combobox(self,values=uniques,state='readonly')
            
                tb.bind('<<ComboboxSelected>>',self.__doFilter)
                tb.place(x=x,y=y,width=w,height=h)
                tb.focus_set()
                tb.grab_set()

       
    def __doFilter(self,event):
        unwanted=[]
        for item in self.tree.get_children():
            texts=self.tree.item(item)['values']
            if type(texts[self.filterindex]) in [type(0),type(0),type(0.0)]:
                if str(texts[self.filterindex])!=event.widget.get():
                    unwanted.append(item)
            else:                             
                if texts[self.filterindex]!=event.widget.get():
                    unwanted.append(item)     
        self.tree.delete(*unwanted)
        #Meter los nuevos valores en el modelo
        self.lists=[self.tree.item(item)['values'] for item in self.tree.get_children()]
        event.widget.grab_release()
        event.widget.destroy()
        if self.callback:
            self.callback()
    

    def cancelFilter(self,event=None):
        if self.filterbackup!=[]:
            self.lists=copy.deepcopy(self.filterbackup)
            self.filterbackup=[]
            self.tree.delete(*self.tree.get_children())
            cont=0
            for item in self.lists:
                self.tree.insert('', 'end', values=item,tags=self.tagsbackup[cont])
                cont+=1

        

    def getTable(self):
        return self.tree

    def getItems(self):
        return self.lists    

    def getSelected(self):
        self.__getSelection()
        return self.selected

    def getSelectedItems(self):
        self.__getSelection()
        return self.selection
        

    def getNumItems(self):
        return len(self.tree.get_children())

    def getItemValues(self,index):
        return self.tree.item(self.tree.get_children()[index])['values']

    def getItemValueAt(self,index,col):
        return self.tree.set(self.tree.get_children()[index],col)

    def setItemValueAt(self,index,col,value):
        return self.tree.set(self.tree.get_children()[index],col,value)     

    def getItem(self,index):
        return self.tree.set(self.tree.get_children()[index])

    def insertItem(self,index,values):
       #Actualizar listas
        if index=='end':
            self.lists.append(values)
        else:
            self.lists.insert(index,values)
        return self.tree.insert('',index,values=values)
     

    def deselect(self,event=None):
        self.selection=self.tree.selection()
        for item in self.selection:
            self.tree.selection_remove(item)
        self.selected=[]
        self.selection=[]

    def selectAll(self):
        for it in self.tree.get_children():
            self.tree.selection_add(it)

    def delAll(self):
        self.tree.delete(*self.tree.get_children())
              

    def delSelection(self):
        self.__getSelection()
        if self.selection:
            self.tree.delete(self.selection)
            self.selected=[]
            self.selection=[]


    def find(self,text,regex=0):
        self.deselect(None)
        for it in self.tree.get_children():
            texts=self.tree.item(it)['values']
            for txt in texts:
                #Convertir numeros a cadenas para buscar!!
                if type(txt) in [type(0),type(0),type(0.0)]:
                    txt=str(txt)
                if regex==0:
                    if text in txt:
                        self.tree.selection_add(it)
                        break
                else:
                    if re.search(text,txt)!=None:
                        self.tree.selection_add(it)
                        break
