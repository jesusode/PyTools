from tkinterweb import HtmlFrame #import the HTML browser
try:
  import tkinter as tk #python3
except ImportError:
  import Tkinter as tk #python2

root = tk.Tk() #create the tkinter window
frame = HtmlFrame(root) #create the HTML browser
frame.load_website("http://tkhtml.tcl.tk/tkhtml.html") #load a website
frame.load_website("http://elmundo.es") #load a website#
frame.pack(fill="both", expand=True) #attach the HtmlFrame widget to the parent window
root.mainloop()