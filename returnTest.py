from tkinter import *
import tkinter as tk

mainWindow = Tk()

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self.master)
        self.master = master
        self.init_window()#main window and menu bar
        self.main_widgets()#objects that inhabit the main page
    def init_window(self):
        self.master.title('Return Test')

    def main_widgets(self):
        Label(mainWindow, text = 'Enter Value to return: ').grid(row = 0, column = 0)
        self.t_entry = Entry(mainWindow)
        self.t_entry.grid(row=0,column=1)

        t_Activate = Button(mainWindow, text = 'Engage', command = self.printReturn)
        t_Activate.grid(row=0,column=2)

    def printReturn(self):
        rval = self.t_entry.get()
        print(rval)

mainWindow.geometry('600x300')
app=Window(mainWindow)

mainWindow.mainloop()