#masterFile for GUI for HVS
#Written by Albert Fabrizi
#Version: July 10, 2020 10:24

from Tkinter import *
import Tkinter as tk
import time
import voltage_ramp
from voltage_ramp import voltageRampCheck, voltageRampUp, voltageRampDown
import random

mainWindow = Tk()

class Window(Frame):
    def __init__(self, master = None):
        Frame.__init__(self,master)

        self.master = master

        self.init_window()#main window and menu bar

        self.main_widgets()#objects that inhabit the main page

        #conversions
        self.voltageConversion = 300 * 1800 / 1709
        self.currentConversion = 3.3/100

    #use this function for menu bar and page title
    def init_window(self):
        self.master.title('HVS')

        #cascade menus
        menu = Menu(mainWindow)
        mainWindow.config(menu = menu)

        #file cascade menu
        file_C = Menu(menu)
        file_C.add_command(label='Exit', command = self.close_window)
        menu.add_cascade(label='File', menu=file_C)

    #this function defines the main page controls
    def main_widgets(self):
        #ramp voltage entry
        Label(mainWindow, text='Enter Desired Voltage: ').grid(row = 0)
        #voltage entry user input
        self.v_Entry = Entry(mainWindow)
        self.v_Entry.grid(row = 0, column = 1)

        #Button to pass entry to ramp voltage function
        v_Activate = Button(mainWindow, text='Enter',command=self.rampEntryCheck)
        v_Activate.grid(row = 0, column = 2)


    #voltage ramp function
    def r_Entry(self, goalVoltage):

        #Get values of voltage and current
        voltage, current = voltageRampCheck()

        if goalVoltage > voltage:
            #print information to the text box
            self.text_box.configure(state = 'normal')
            self.text_box.insert(tk.END, 'Voltage Ramping from ' + str(voltage) + '\n')
            self.text_box.insert(tk.END, 'Voltage Ramping to ' + str(goalVoltage) + '\n')
            self.text_box.insert(tk.END, '----------\n')
            self.text_box.insert(tk.END, 'Max Current Set to ' + str(current) + '\n')
            self.text_box.insert(tk.END, '----------\n')
            self.text_box.configure(state = 'disabled')
            #begin ramping up
            voltageRampUp(goalVoltage)

            #get updated information
            voltage, current = voltageRampCheck()

            #print updated information
            self.text_box.configure(state = 'normal')
            self.text_box.insert(tk.END, 'Voltage Brought to ' + str(voltage) + '\n')
            self.text_box.insert(tk.END, '-----------\n')
            self.text_box.configure(stated = 'disabled')
            
        else:
            #print information to the text box
            self.text_box.configure(state = 'normal')
            self.text_box.insert(tk.END, 'Voltage Ramping from ' + str(voltage) + '\n')
            self.text_box.insert(tk.END, 'Voltage Ramping to ' + str(goalVoltage) + '\n')
            self.text_box.insert(tk.END, '-----------\n')
            self.text_box.insert(tk.END, 'Max Current Set to ' + str(current) + '\n')
            self.text_box.insert(tk.END, '-----------\n')
            self.text_box.configure(state = 'disabled')

            #begin ramping down
            voltageRampDown(goalVoltage)

            #get updated information
            voltage, current = voltageRampCheck()

            #print updated information
            self.text_box.configure(state = 'normal')
            self.text_box.insert(tk.END, 'Voltage Brought to ' + str(voltage) + '\n')
            self.text_box.insert(tk.END, '-----------\n')
            self.text_box.configure(state = 'disabled')
        
    def rampEntryCheck(self):
        rampV = self.v_Entry.get()
        check = None
        try:#check if int
            rampV = int(rampV)
            check = True
        except:
            try:#check if float
                rampV = float(rampV)
                check = True
            except:
                check = False
        if check == True:
            self.r_Entry(rampV)


    #individual menu functions
    def close_window(self):
        exit()

#intial size of window
mainWindow.geometry('600x300')
app = Window(mainWindow)

#mainloop stays at the end
mainWindow.mainloop()
