A#Main File for High Voltage System
#Written by Albert Fabrizi
#To Run: python HighVoltageSystem.py

#Version 1.4
#Last Edited: August 6, 2020
#Version log:
#0.1: Implemented all GUI features
#0.2: Implemented Voltage Control
#0.3: Textbox changes to give updated information
#0.4: Added Multi-Meter Function
#0.5: Linked Classes and disabled system check
#0.6: Added Expert Mode Window
#0.7: Added temp variables and repaired class instances
#0.8: Added time delay
#1.0: Overhauled structure of program and wrote in comments for easier use and editing
#1.1: Text boxes now update properly
#1.2: Made operational changes to ramping functions
#1.3: Added Preset functions
#1.4: Added Voltage Modulator
#1.5: Fixed Current counter

#TO DO
#5)Set Current Limit
#6)Safetry Features

#!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!
#Do not edit this code without first reading the manual which should be located in the same directory as this program
#Any editing may cause damage to HVS or the wire chambers if not handled properly

#~~~~~~~~~~~~~~~~~~~~~~Notes~~~~~~~~~~~~~~~~~~~~~~~
#This Program does use a wildcard input for tkinter, eventually this should change
#Other libraries are used to control DACs and ADCs. Should eventually integrate them into this
#program for simplicity

#--------------Begin Program--------------------

#Note: tkinter is called differently between python versions and can cause errors
#This try-except will prevent any errors if a different python interepreter is used
try:
    #import Tkinter
    from Tkinter import *
    import Tkinter as tk
except ImportError: #python 3.x present
    #import tkinter
    from tkinter import *
    import tkinter as tk

#~~~~~~~~~~~~~~~~~~
#Packages Required
#~~~~~~~~~~~~~~~~~~
import time
import random
from Adafruit_MCP4725 import MCP4725
from mcp3428 import MCP3428
import smbus
import numpy as np

#~~~~~~~~~~~~~~~~~
#System Class
#~~~~~~~~~~~~~~~~~
mainWindow = Tk()

class Window(Frame):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Create Instances to control the DACs and ADCs
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # create bus object
    bus = smbus.SMBus(1)
    # create a dictionary of addresses and information needed for the ADC instance
    kwargs = {'address': 0x68, 'mode': 0x10, 'sample_rate': 0x08, 'gain':0x00}

    # create a ADC instance
    mcp3428 = MCP3428(bus, kwargs)

    # Create a DAC instance, initializing the class in this file
    # the dac variable names correspond to the addresses to the dac's in DECIMAL, while the
    # address given in the actual call for the MCP4725 class is in HEXADECIMAL

    #Max Current Dac
    dac96 = MCP4725(address=0x60, busnum=1)

    #voltage Dac
    dac97 = MCP4725(address=0x61, busnum=1)


    #conversion factors for 0-10V to 0-3000V
    voltageConversion = 300 * 1800 / 1709
    currentConversion = 3.3/10

    #~~~~~~~~~~~~~~~~~~~
    #Class variables
    #!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!
    #Only edit if you know what you're doing or with Prof. Miskimens's instruction
    #~~~~~~~~~~~~~~~~~~~
    rampSlope = 14
    curLimit = 4095
    bitVoltage = 0


    #The program has an error when it first starts up that causes voltage to start at 100 V
    #Set voltage to 0 when program begins
    dac97.set_voltage(0)

    def __init__(self, master = None):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #This Function initializes all
        #Tkinter functions
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Frame.__init__(self,master)#frame instance
        self.master = master
        self.init_window()#main window and menu bar
        self.main_widgets()#objects that inhabit the main page

    def init_window(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Building the main window and the cascade menu bar
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
        #title of the window
        self.master.title('High Voltage System')

        #cascade menus
        menu = Menu(mainWindow)
        mainWindow.config(menu = menu)

        #file cascade menu
        #basic functions
        file_C = Menu(menu)
        file_C.add_command(label='Exit', command = self.close_window)
        menu.add_cascade(label='File', menu=file_C)

        #windows cascade menu
        #opens other pop-up windows
        windows_C = Menu(menu)
        windows_C.add_command(label='Open Multi-Meter', command = self.openMeterWindow)
        windows_C.add_command(label='Open Advanced Settings', command = self.openExpertWindow)
        windows_C.add_command(label='Open Voltage Modulator', command = self.voltModulatorWindow)
        menu.add_cascade(label='Windows',menu=windows_C)

        #presets cascade menu
        #shows preset options
        presets_C = Menu(menu)
        presets_C.add_command(label='200V @ 10V/s', command = self.preset1)
        presets_C.add_command(label='1000V @ 10V/s', command = self.preset2)
        presets_C.add_command(label='1700V @ 10V/s', command = self.preset3)
        presets_C.add_command(label='1800V @ 10V/s', command = self.preset4)
        presets_C.add_command(label='0V @ 10V/s', command = self.preset5)
        menu.add_cascade(label='Presets',menu=presets_C)

    def main_widgets(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Widgets on the main page
        #Each "attribute" is defined here
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        #Voltage entry user input label and field
        
        Label(mainWindow, text = 'Enter Voltage to Ramp to: ').grid(row = 0)
        self.v_Entry = Entry(mainWindow)
        self.v_Entry.grid(row = 0, column = 1)

        #System Check Button (disabled)
        #v_Activate = Button(mainWindow, text = 'Sys Check', command=self.rampEntryCheck)
        #v_Activate.grid(row = 0, column = 2)

        #Button to begin ramping
        hvsEngage = Button(mainWindow, text = 'Begin Ramp', command = self.r_Entry)
        hvsEngage.grid(row = 0, column = 2)

        #Initialize textbox
        self.text_box = Text(mainWindow, height = 15, width = 45)
        self.text_box.grid(row = 2, column = 1)
        self.text_box.insert(tk.INSERT,'Voltage Ramp\n')
        self.text_box.insert(tk.INSERT,'-----\n')
        self.text_box.configure(state='disabled')

    
    def r_Entry(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Function to compare voltage entry to current voltage give by the ADC
        #Then begin ramping
        #Called by pressing "Begin Ramp" button
        #Passes values to Either voltage ramp up or ramp down
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        try:
            #Values only can be edited in Advanced mode
            Window.rampSlope = int(self.slopeEntry.get())
            Window.curLimit = int(self.ilimit.get())
            #curLimitTemp = int(self.ilimit.get())
            #Window.curLimit = (curLimitTemp/3000)*4095
        except:    #Default settings if fields are left empty
            Window.curLimit = 4095
            Window.rampSlope = 14

        #Get values of voltage and current
        voltage, current = self.voltageRampCheck()
        
        #Get goal Voltage 
        goalVolt = self.v_Entry.get()

        goalVolt = float(goalVolt)

        #Begin Comparison and ramping
        if goalVolt > voltage:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~
            #Conditions for voltage "Ramp Up"
            #~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            #print information to the text box
            self.text_box.configure(state = 'normal')
            self.text_box.insert(tk.INSERT, 'Voltage Ramping from ' + str(voltage) + ' Volts' +'\n')
            self.text_box.insert(tk.INSERT, 'Voltage Ramping to ' + str(goalVolt) + ' Volts' +'\n')
            self.text_box.insert(tk.INSERT, '----------\n')
            self.text_box.insert(tk.INSERT, 'Current Set to ' + str(current) + ' mA' +'\n')
            self.text_box.insert(tk.INSERT, '----------\n')
            self.text_box.configure(state = 'disabled')

            #begin ramping up
            self.voltageRampUp(goalVolt)

            #get updated information
            voltage, current = self.voltageRampCheck()

            #print updated information
            self.text_box.configure(state = 'normal')
            self.text_box.delete('1.0', END)
            self.text_box.insert(tk.INSERT, 'Voltage Brought to ' + str(voltage) + ' Volts' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.insert(tk.INSERT, 'Current at: ' + str(current) + ' mA' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.configure(state = 'disabled')
            
        else:

            #~~~~~~~~~~~~~~~~~~~~~~~~~
            #Conditions for voltage "Ramp Down"
            #~~~~~~~~~~~~~~~~~~~~~~~~~
            
            #print information to the text box
            self.text_box.configure(state = 'normal')
            self.text_box.insert(tk.INSERT, 'Voltage Ramping from ' + str(voltage) + ' Volts' + '\n')
            self.text_box.insert(tk.INSERT, 'Voltage Ramping to ' + str(goalVolt) + ' Volts' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.insert(tk.INSERT, 'Max Current Set to ' + str(current) + ' mA' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.configure(state = 'disabled')

            #begin ramping down
            self.voltageRampDown(goalVolt)

            #get updated information
            voltage, current = self.voltageRampCheck()

            #print updated information
            self.text_box.configure(state = 'normal')
            self.text_box.delete('1.0',END)
            self.text_box.insert(tk.INSERT, 'Voltage Brought to ' + str(voltage) + ' Volts' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.configure(state = 'disabled')

            
    def close_window(self):
        #~~~~~~~~~~~~~~~~~
        #Exit Window command
        #~~~~~~~~~~~~~~~~~
        exit()

    def voltageRampCheck(self):
        #~~~~~~~~~~~~~~~~~~~~~~~
        #takes readings of voltage and current at that moment
        #from the ADC and returns both in a tuple
        #~~~~~~~~~~~~~~~~~~~~~~~
        currentReading = self.mcp3428.take_single_reading(1)
        current = currentReading * self.currentConversion
        voltageReading = self.mcp3428.take_single_reading(0)
        voltage = voltageReading * self.voltageConversion
        return voltage, current

    def openExpertWindow(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~
        #Advanced settings menu for editing
        #attributes of the ramp
        #~~~~~~~~~~~~~~~~~~~~~~~
        expertWindow = Toplevel(mainWindow)

        expertWindow.title('Advanced Options')

        expertWindow.geometry("650x300")

        #Change the "slope of the ramp"
        Label(expertWindow, text = 'Enter Slope (leave blank for 10V/s): ').grid(row = 0, column = 0)

        #slope entry user input
        self.slopeEntry = Entry(expertWindow)
        self.slopeEntry.grid(row = 0, column = 1)

        #Change the current Limit
        Label(expertWindow, text = 'Enter Current Limit (leave blank for 800uA): ').grid(row = 1, column = 0)
        
        #current limit user input
        self.ilimit = Entry(expertWindow)
        self.ilimit.grid(row = 1, column = 1)

        #delay for slope
        #this currently does nothing
        Label(expertWindow, text = 'Enter Delay time (s) for voltage step: ').grid(row=2,column=0)
        self.rampDelayEntry = Entry(expertWindow)
        self.rampDelayEntry.grid(row=2,column=1)

        self.eWindowText = Text(expertWindow, height = 15, width = 50)
        self.eWindowText.grid(row = 3, column = 1)

        self.eWindowText.configure(state = 'normal')
        self.eWindowText.insert(tk.INSERT, '!!!!!!!!!!!!!!ATTENTION!!!!!!!!!!!!!!\n')
        self.eWindowText.insert(tk.INSERT, '!!!!!!!PLEASE READ BEFORE USE!!!!!!!!\n')
        self.eWindowText.insert(tk.INSERT, 'These fields should only be edited after\n')
        self.eWindowText.insert(tk.INSERT, 'the manual has been read and the code studied.\n')
        self.eWindowText.insert(tk.INSERT, 'Only meant to be used by an experienced user or\n')
        self.eWindowText.insert(tk.INSERT, 'under instruction from Prof. Miskimen.\n')
        self.eWindowText.insert(tk.INSERT, '-----------\n')
        self.eWindowText.insert(tk.INSERT, 'Please consult manual for more information.\n')
        self.eWindowText.configure(state = 'disabled')

    def openMeterWindow(self):
        #~~~~~~~~~~~~~~~~~~~~~
        #window that gives a live
        #update of voltage and current
        #~~~~~~~~~~~~~~~~~~~~~
        
        meterWindow = Toplevel(mainWindow)
        meterWindow.title('Multi-Meter')
        meterWindow.geometry("400x300")
        
        #Simple button to activate meter
        mMeter = Button(meterWindow, text = 'Run Meter', command = self.multiMeter)
        mMeter.pack()
        #mMeter.grid(row = 0, column = 0)

        #initialize text box in the multi-meter window
        self.meterBox = Text(meterWindow, height = 15, width = 45)
        #self.meterBox.grid(row = 1, column = 0)
        self.meterBox.pack()
        self.meterBox.insert(tk.INSERT, '--------\n')
        self.meterBox.insert(tk.INSERT, 'Multi-Meter \n')
        self.meterBox.insert(tk.INSERT, '--------\n')
        self.meterBox.configure(state = 'disabled')

    def voltModulatorWindow(self):
        voltWindow = Toplevel(mainWindow)
        voltWindow.title('Voltage Modulator')
        voltWindow.geometry("200x100")

        voltUpBut = Button(voltWindow, text = '+1 Bit Voltage', command = self.voltUp)
        voltUpBut.pack()

        voltDownBut = Button(voltWindow,text = '-1 Bit Voltage', command = self.voltDown)
        voltDownBut.pack()

    def voltUp(self):
        voltage, current = self.voltageRampCheck()
        Window.bitVoltage =  Window.bitVoltage + 1
        self.dac97.set_voltage(Window.bitVoltage)
        self.text_box.configure(state = 'normal')
        self.text_box.delete('1.0',END)
        self.text_box.insert(tk.INSERT, 'Voltage Raised to: ' + str(voltage) + ' Volts' + '\n')
        self.text_box.insert(tk.INSERT, '-----------\n')
        self.text_box.insert(tk.INSERT, 'Current at: ' + str(current) + ' mA' + '\n')
        self.text_box.insert(tk.INSERT, '-----------\n')
        self.text_box.configure(state = 'disabled')
    
    def voltDown(self):
        voltage, current = self.voltageRampCheck()
        Window.bitVoltage = Window.bitVoltage - 1
        self.dac97.set_voltage(Window.bitVoltage)
        self.text_box.configure(state = 'normal')
        self.text_box.delete('1.0',END)
        self.text_box.insert(tk.INSERT, 'Voltage Lowered to: ' + str(voltage) + ' Volts' + '\n')
        self.text_box.insert(tk.INSERT, '-----------\n')
        self.text_box.insert(tk.INSERT, 'Current at: ' + str(current) + ' mA' + '\n')
        self.text_box.configure(state = 'disabled')
        
    def preset1(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Preset 1 Ramp. Ramp to 200 Volts at
        #10V/s
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        voltage, current = self.voltageRampCheck()
        Window.rampSlope = 14
        Window.curLimit = 4095
        if voltage > 200:
            self.voltageRampDown(200)
        else:
            self.voltageRampUp(200)

    def preset2(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Preset 2 Ramp. Ramp up to 1000 Volts at
        #10V/s
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        voltage, current = self.voltageRampCheck()
        Window.rampSlope = 14
        Window.curLimit = 4095
        if voltage > 1000:
            self.voltageRampDown(1000)
        else:
            self.voltageRampUp(1000)

    def preset3(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Preset 3 Ramp. Ramp up to 1700 Volts at
        #10V/s
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        voltage, current = self.voltageRampCheck()
        Window.rampSlope = 14
        Window.curLimit = 4095
        if voltage > 1700:
            self.voltageRampDown(1700)
        else:
            self.voltageRampUp(1700)

    def preset4(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Preset 4 Ramp. Ramp up to 1800 Volts at
        #10V/s
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        Window.rampSlope = 14
        Window.curLimit = 4095
        self.voltageRampUp(1800)

    def preset5(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Preset 5 Ramp. Ramp down to 0 Volts at
        #10V/s
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Window.rampSlope = 14
        Window.curLimit = 4095
        self.voltageRampDown(0)

    def multiMeter(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Meter displaying voltage and current to text box in pop out box
        #since it is an infinite loop the window must be closed after starting
        #to run any other functions
        #There is currently an error where the system crashes due to the infinite loop
        #Built in a switch that allows a user to get value once to not lose control of system
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        mmSwitch = 0
        prevTime = time.time()
        if mmSwitch == 0:
            voltage,current = self.voltageRampCheck()
            self.meterBox.configure(state = 'normal')
            self.meterBox.delete('1.0', END)
            self.meterBox.insert(tk.INSERT, 'Voltage at: ' + str(voltage) + ' Volts' + '\n')
            self.meterBox.insert(tk.INSERT, '-----------\n')
            self.meterBox.insert(tk.INSERT, 'Current at: ' + str(current) + ' mA' + '\n')
            self.meterBox.insert(tk.INSERT, '-----------\n')
            self.meterBox.configure(state = 'disabled')
        if mmSwitch == 1:
            while 1:
                livetime = time.time()
                if livetime - prevTime < 1:
                    continue
                voltage, current = self.voltageRampCheck()
                prevTime = livetime
                self.meterBox.configure(state = 'normal')
                self.meterBox.insert(tk.INSERT, 'Voltage at: ' + str(voltage) + ' Volts' + '\n')
                self.meterBox.insert(tk.INSERT, '-----------\n')
                self.meterBox.insert(tk.INSERT, 'Current at: ' + str(current) + ' mA' + '\n')
                self.meterBox.insert(tk.INSERT, '-----------\n')
                self.meterBox.configure(state = 'disabled')
                mainWindow.update_idletasks()

    def voltageRampUp(self, goalVolt):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Ramp up function. Takes user input and
        #current voltage and steps up the voltage
        #until the goal voltage is reached
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #get voltage and current
        voltage, current = self.voltageRampCheck()
        
        # and is twelve bits (12 bits), the range
        # we can set these to are between 0 and 4095 for voltages that range from 0 V to 10 V.
        self.text_box.configure(state = 'normal')
        self.text_box.delete('1.0', END)
        self.text_box.insert(tk.INSERT, 'Voltage Starting at: ' + str(voltage) + ' Volts' + '\n')
        self.text_box.insert(tk.INSERT, '-----------\n')
        self.text_box.insert(tk.INSERT, 'Voltage Ramping to ' + str(goalVolt) + ' Volts' + '\n')
        self.text_box.insert(tk.INSERT, '-----------\n')
        self.text_box.insert(tk.INSERT, 'Max Current set to: ' + str(current) + ' mA' + '\n')
        self.text_box.configure(state = 'disabled')

        #A variable that is used for the ramping so the class variable can be saved then edited at the end
        tempBitVolt = Window.bitVoltage

        #Set DAC Voltage to the bit left from last time
        self.dac97.set_voltage(tempBitVolt)

        #set current limit
        self.dac96.set_voltage(self.curLimit)


        prevTime = time.time()

        goalVolt = float(goalVolt)

        #begin while loop of increments
        while 1:
            # read the voltage at the beginning of each iteration.
            # these readings are from 0 to 10 V, so convert wisely

            #Delay every loop to keep the ramp consistent
            
            #time.sleep(Window.rampDelay)

            livetime=time.time()
            
            if livetime-prevTime < 1:
                continue
            
            #Get updated values of voltage and current
            voltage, current = self.voltageRampCheck()
            #currentRead = self.mcp3428.take_single_reading(1)
            prevTime = livetime
            #Update text box to display this loop's information

            self.text_box.configure(state = 'normal')
            self.text_box.delete('1.0', END)
            self.text_box.insert(tk.INSERT, 'Voltage: (0 to 3000V): ' + str(voltage) + ' Volts' + '\n')
            self.text_box.insert(tk.INSERT, '--------------\n')
            self.text_box.insert(tk.INSERT, 'Current Set to: ' + str(current) + ' mA' + '\n')
            self.text_box.insert(tk.INSERT, '--------------\n')
            #self.text_box.insert(tk.INSERT, 'Current Reading: ' + str(currentRead) + '\n')
            self.text_box.configure(state = 'disabled')
            
            if goalVolt > voltage:
                #If the voltage has not reached the goal yet, add more bits
                tempBitVolt += Window.rampSlope
                #Display Bit information to text box
                self.text_box.configure(state = 'normal')
                self.text_box.insert(tk.INSERT, 'Bit: ' + str(tempBitVolt) + '\n')
                self.text_box.insert(tk.INSERT, '-----------\n')
                self.text_box.configure(state = 'disabled')
                mainWindow.update_idletasks()
                
                #send information to DAC
                self.dac97.set_voltage(tempBitVolt)
            else:
                #Reached goal voltage pass to hold voltage and update class variable
                Window.bitVoltage = tempBitVolt
                self.holdValue(goalVolt)
                #break out of infinite loop
                break

    def voltageRampDown(self, goalVolt):

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Ramp down function. Takes user input and
        #current voltage and steps down the voltage
        #until the goal voltage is reached
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #get initial values
        voltage, current = self.voltageRampCheck()

        #Set a temporary variable
        tempBitVolt = Window.bitVoltage

        #set starting voltage
        self.dac97.set_voltage(tempBitVolt)

        #Set Current Limit
        self.dac96.set_voltage(self.curLimit)

        #Print information to text box
        self.text_box.configure(state = 'normal')
        self.text_box.delete('1.0', END)
        self.text_box.insert(tk.INSERT, 'Voltage Starting at: ' + str(voltage) + ' Volts' + '\n')
        self.text_box.insert(tk.INSERT, '-----------\n')
        self.text_box.insert(tk.INSERT, 'Voltage Ramping to ' + str(goalVolt) + ' Volts' + '\n')
        self.text_box.configure(state = 'disabled')

        prevTime = time.time()

        goalVolt = float(goalVolt)
        
        while 1:

            #Delay for a set time
            #time.sleep(Window.rampDelay)

            livetime = time.time()
            if livetime-prevTime < 1:
                continue

            voltage, current = self.voltageRampCheck()
            
            prevTime = livetime

            #print information to text box
            self.text_box.configure(state = 'normal')
            self.text_box.delete('1.0', END)
            self.text_box.insert(tk.INSERT, 'Voltage: ' + str(voltage) + ' Volts' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.insert(tk.INSERT, 'Current: ' + str(current) + ' mA' + '\n')
            self.text_box.insert(tk.INSERT, '-----------\n')
            self.text_box.configure(state = 'disabled')

            if voltage > goalVolt:

                #if the voltage is still too high subtract bits
                tempBitVolt -= Window.rampSlope

                #Print bit information to text box
                self.text_box.configure(state = 'normal')
                self.text_box.insert(tk.INSERT, 'Bit: ' + str(tempBitVolt) + '\n')
                self.text_box.insert(tk.INSERT, '-----------\n')
                self.text_box.configure(state = 'disabled')

                mainWindow.update_idletasks()

                #send information to DAC
                self.dac97.set_voltage(tempBitVolt)
            else:

                #Reached goal value pass to class variable and holdValue function
                Window.bitVoltage = tempBitVolt
                self.holdValue(goalVolt)
                break

            if tempBitVolt <= 20 and goalVolt == 0:
                #condition if Voltage is goint to zero just set the Dac to zero at the end of 
                #the ramp instead of using holdValue
                self.dac97.set_voltage(0)
                Window.bitVoltage = 0
                break

    def holdValue(self, goalVolt):
        #~~~~~~~~~~~~~~~~~~~~~
        #A function that changes the voltage by one bit instead 
        #of the defined slope to get to the goal value
        #~~~~~~~~~~~~~~~~~~~~~~

        counts = 0

        #set class value to temp variable
        tempHoldBitVolt = Window.bitVoltage
        while 1:
            voltage, current = self.voltageRampCheck()
            if counts >= 100:
                
                #after this function runs 100 times the loop is broken
                self.dac97.set_voltage(tempHoldBitVolt)

                #print information to text box 
                self.text_box.configure(state = 'normal')
                self.text_box.delete('1.0', END)
                self.text_box.insert(tk.INSERT, 'Voltage Holding at: ' + str(voltage) + ' Volts' + '\n')
                self.text_box.insert(tk.INSERT, 'Current: ' + str(current) + ' mA' + '\n')
                self.text_box.configure(state = 'disabled')

                #send temp variable to class variable
                Window.bitVoltage = tempHoldBitVolt
                break
            counts = counts + 1

            #modulates voltage by +1/-1 until the voltage value is within an acceptable range
            if voltage < (goalVolt - 1):
                tempHoldBitVolt += 1
                self.dac97.set_voltage(tempHoldBitVolt)
                
            elif voltage > (goalVolt + 1):
                tempHoldBitVolt -= 1
                self.dac97.set_voltage(tempHoldBitVolt)
            
            #print voltage to text box
            self.text_box.configure(state = 'normal')
            self.text_box.delete('1.0', END)
            self.text_box.insert(tk.INSERT, 'Please Wait Voltage Correcting....\n')
            self.text_box.insert(tk.INSERT, '------------\n')
            self.text_box.insert(tk.INSERT, 'Voltage: ' + str(voltage) + ' Volts' + '\n')
            self.text_box.configure(state = 'disabled')

            mainWindow.update_idletasks()

mainWindow.geometry('650x300')
app = Window(mainWindow)

mainWindow.mainloop()
