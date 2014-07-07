from Tkinter import *
import tkFileDialog

class WindowDemo:
    def run(self):
        win = self.prepareGui()
        win.mainloop()

    def closewindow(self):
        exit()

    def askForFile(self):
        self.labelText.set(tkFileDialog.askopenfilename(filetypes = ( ("pyhons", "*.py"), ("any", "*.*") )))
    
    def prepareGui(self):
        """prepares window and stuff"""
        
        app = Tk()
        app.title("Pierwsze okienko w pytonie")

        self.labelText = StringVar()
        label = Label(app, textvariable = self.labelText)
        label.pack()

        button = Button(app, text="Otworz plik", command = self.askForFile)
        button.pack()

        
        menubar = Menu(app)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Otworz plik", command = self.askForFile)
        filemenu.add_command(label="Zamknij", command= self.closewindow)
        
        menubar.add_cascade(label="Plik", menu=filemenu)

        

        app.config(menu=menubar)
        
      
        return app



WindowDemo().run()


    
