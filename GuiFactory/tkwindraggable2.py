# Version: 0.7
# Author: Miguel Martinez Lopez
# Uncomment the next line to see my email
# print "Author's email: ", "61706c69636163696f6e616d656469646140676d61696c2e636f6d".decode("hex")


import tkinter as Tk
import tkinter.font

class DraggableWindow(object):

    def __init__(self, disable_draggingd =False, release_command = None):
        if disable_draggingd == False:
            self.bind('<Button-1>', self.initiate_motion)
            self.bind('<ButtonRelease-1>', self.release_dragging)

        self.release_command = release_command


    def initiate_motion(self, event) :
        mouse_x, mouse_y = self.winfo_pointerxy()

        self.deltaX = mouse_x - self.winfo_x()
        self.deltaY = mouse_y - self.winfo_y()

        self.bind('<Motion>', self.drag_window)


    def drag_window (self, event) :
        mouse_x, mouse_y = self.winfo_pointerxy()

        new_x = mouse_x - self.deltaX
        new_y = mouse_y - self.deltaY

        if new_x < 0 :
            new_x = 0

        if new_y < 0 :
            new_y = 0

        self.wm_geometry("+%s+%s" % (new_x, new_y))

    def release_dragging(self, event):
        self.unbind('<Motion>')

        if self.release_command != None :
            self.release_command()

    def disable_dragging(self) :
        self.unbind('<Button-1>')
        self.unbind('<ButtonRelease-1>')
        self.unbind('<Motion>')

    def enable_dragging(self):
        self.bind('<Button-1>', self.initiate_motion)
        self.bind('<ButtonRelease-1>', self.release_dragging)


class AutoResizedText(Tk.Frame):
    def __init__(self, master, width=0, height=0, family=None, size=None,*args, **kwargs):

        Tk.Frame.__init__(self, master, width = width, height= height)
        self.pack_propagate(False)

        self.min_width = width
        self.min_height = height

        self.Text_widget = Tk.Text(self, *args, **kwargs)
        self.Text_widget.pack(expand=True, fill='both')

        if family != None and size != None:
            self.font = tkinter.font.Font(family=family,size=size)
        else:
            self.font = tkinter.font.Font(family=self.Text_widget.cget("font"))

        self.Text_widget.config(font=self.font)

        # I want to insert a tag just in front of the class tag
        # It's not necesseary to guive to this tag extra priority including it at the beginning
        # For this reason I am making this search
        list_of_bind_tags = list(self.Text_widget.bindtags())
        list_of_bind_tags.insert(list_of_bind_tags.index('Text'), 'autoresizetext')

        self.Text_widget.bindtags( tuple(list_of_bind_tags) )
        self.Text_widget.bind_class("autoresizetext", "<KeyPress>",self.update_textbox)

    def update_textbox(self, event):

        if event.keysym == 'BackSpace':
            self.Text_widget.delete("%s-1c" % Tk.INSERT)
            new_text = self.Text_widget.get("1.0", Tk.END)
        elif event.keysym == 'Delete':
            self.Text_widget.delete("%s" % Tk.INSERT)
            new_text = self.Text_widget.get("1.0", Tk.END)
        # We check whether it is a punctuation or normal key
        elif len(event.char) == 1:
            if event.keysym == 'Return':
                # In this situation ord(event.char)=13, which is the CARRIAGE RETURN character
                # We want instead the new line character with ASCII code 10
                new_char = '\n'
            else:
                new_char = event.char


            old_text = self.Text_widget.get("1.0", Tk.END)
            new_text = self.insert_character_into_message(old_text, self.Text_widget.index(Tk.INSERT), new_char)

        else:
            # If it is a special key, we continue the binding chain
            return

        # Tk Text widget always adds a newline at the end of a line
        # This last character is also important for the Text coordinate system
        new_text = new_text[:-1]

        number_of_lines = 0
        widget_width = 0

        for line in new_text.split("\n"):
            widget_width = max(widget_width,self.font.measure(line))
            number_of_lines += 1

        # We need to add this extra space to calculate the correct width
        widget_width += 2*self.Text_widget['bd'] + 2*self.Text_widget['padx'] + self.Text_widget['insertwidth']

        if widget_width < self.min_width:
            widget_width = self.min_width

        self.Text_widget.configure(height=number_of_lines)
        widget_height = max(self.Text_widget.winfo_reqheight(), self.min_height)

        self.config(width=widget_width, height=widget_height)

        # If we don't update_idletasks(), the window won't be resized before the insertion
        self.update_idletasks()

        # Finally we insert the new character
        if event.keysym != 'BackSpace' and event.keysym != 'Delete':
            self.Text_widget.insert(Tk.INSERT, new_char)

        return "break"

    def insert_character_into_message(self,message, coordinate, char):
        target_row, target_column = list(map( int, coordinate.split('.')))

        this_row = 1
        this_column = 0
        index = 0

        for ch in message:
            if this_row == target_row and this_column == target_column:
                message = message[:index] + char + message[index:]
                return message

            index += 1

            if ch == '\n':
                this_row += 1
                this_column = 0
            else:
                this_column += 1

    def focus(self):
        self.Text_widget.focus()
    

class DesktopNote(Tk.Toplevel, DraggableWindow):
    #BG_NOTE = '#ffff7d'

    def __init__(self, parent, title='Without title', min_width =110, min_height = 40,bg_note='#ffff7d'):
        Tk.Toplevel.__init__(self, parent)
        DraggableWindow.__init__(self)
        self.BG_NOTE

        self.overrideredirect(True)

        self.close_IMG = Tk.PhotoImage(data="R0lGODlhEAAQAPAAAAQEBAAAACH5BAEAAAEALAAAAAAQABAAAAImDI6ZFu3/DpxO0mlvBLFX7oEfJo5QZlZNaZTupp2shsY13So6VwAAOw==")
        self.minimize_IMG = Tk.PhotoImage(data="R0lGODlhEAAQAPAAAAQEBAAAACH5BAEAAAEALAAAAAAQABAAAAIiDI6ZFu3/DpxO0mlvBBrmbnBg83Wldl6ZgoljSsFYqNRcAQA7")
        self.restore_IMG = Tk.PhotoImage(data="R0lGODlhEAAQAPcAAAAAAAQEBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAP8ALAAAAAAQABAAAAhFAP8FGEiwYEGB/xIqXLhwIMOHCh02NBgxAEODFhNKjNiwYsWDGQWGxIhQ48iJI09ynLhS48WUB1lCfLhxpkebHTHqtBgQADs=")
        self.minimizeAtRightSide_IMG = Tk.PhotoImage(data="R0lGODlhEAAQAPcAAAAAAAQEBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAP8ALAAAAAAQABAAAAg+AP8FGEiwYEGB/xIqXLhwIMOHCh1CfChxosSKEC8GmJhQI0eBG0F+9MiRpMWQGCmiDPmxI8uWKUuCNEhzY0AAOw==")


        frameNote = Tk.Frame(self, bg=self.BG_NOTE, bd=1, highlightbackground='black',highlightcolor='black',highlightthickness=1)
        frameNote.pack()

        self.mimizedNote = Tk.Label(frameNote, text=title, bg=self.BG_NOTE, wraplength=1)
        self.mimizedNote.bind('<Button-1>', lambda event: self.maximize_from_right_side())

        self.maximizedNote = Tk.Frame(frameNote)
        self.maximizedNote.pack()

        Header = Tk.Frame(self.maximizedNote, bg=self.BG_NOTE)
        Header.pack(fill=Tk.X)

        HR = Tk.Frame(self.maximizedNote,bg='black', height=1)
        HR.pack(padx=1, fill=Tk.X)

        titleLabel = Tk.Label(Header, text = title, bg=self.BG_NOTE)
        titleLabel.pack(side=Tk.LEFT)

        Tk.Button(Header, compound=Tk.TOP, image=self.close_IMG, bg=self.BG_NOTE,activebackground=self.BG_NOTE, command= self.destroy).pack(side=Tk.RIGHT)

        self.iconifyButton = Tk.Button(Header, image=self.minimize_IMG, command=self.minimize,  bg=self.BG_NOTE, activebackground=self.BG_NOTE)
        self.iconifyButton.pack(side=Tk.RIGHT)

        Tk.Button(Header, compound=Tk.TOP, image=self.minimizeAtRightSide_IMG, bg=self.BG_NOTE,activebackground=self.BG_NOTE, command= self.minimize_at_right_side).pack(side=Tk.RIGHT)

        self.text_box = AutoResizedText(self.maximizedNote, bd=0, bg=self.BG_NOTE, width=min_width, height=min_height)
        self.text_box.pack(expand=Tk.YES, fill=Tk.BOTH)


    def minimize_at_right_side(self):
        self.disable_dragging()
        self.maximizedNote.pack_forget()
        self.mimizedNote.pack()

        self.x = self.winfo_x()
        self.y = self.winfo_y()

        self.wm_geometry('-0+%d'%self.y)


    def maximize_from_right_side(self):
        self.maximizedNote.pack()
        self.mimizedNote.pack_forget()
        self.wm_geometry('+%d+%d'% (self.x,self.y))
        self.enable_dragging()

    def minimize(self):
        self.text_box.pack_forget()
        self.iconifyButton['command'] = self.maximize
        self.iconifyButton['image'] = self.restore_IMG

    def maximize(self):
        self.text_box.pack(expand=Tk.YES, fill=Tk.BOTH)
        self.iconifyButton['command'] = self.minimize
        self.iconifyButton['image'] = self.minimize_IMG


class Test(Tk.Tk):
    def __init__(self):
        self.root = Tk.Tk()
        Tk.Label(self.root,text="Title:").pack(side=Tk.LEFT)

        self.title = Tk.StringVar()
        self.title.set('TITLE')

        entry_title = Tk.Entry(self.root, textvariable=self.title)
        entry_title.pack(side=Tk.LEFT)
        entry_title.bind('<Return>', lambda event: self.create_note() )

        Tk.Button(self.root, text="Create another note", command=self.create_note).pack(side=Tk.LEFT)

        self.create_note()

    def create_note(self):
        New_note = DesktopNote(self.root, self.title.get())
        New_note.text_box.focus()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    Test().run()
