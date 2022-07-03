# file: voltage_ramp.py
# brief: Sets ramp for the High Voltage Supply

import time
import random
import Adafruit_MCP4725
import mcp3428
import smbus
import numpy as np

# create bus object
bus = smbus.SMBus(1)
# create a dictionary of addresses and information needed for the ADC instance
kwargs = {'address': 0x68, 'mode': 0x10, 'sample_rate': 0x08, 'gain':0x00}

# crate a ADC instance
mcp3428 = mcp3428.MCP3428(bus, kwargs)

# Create a DAC instance, initializing the class in this file
# the dac variable names correspond to the addresses to the dac's in DECIMAL, while the
# address given in the actual call for the MCP4725 class is in HEXADECIMAL

#Max Current Dac
dac96 = Adafruit_MCP4725.MCP4725(address=0x60, busnum=1)

#voltage Dac
dac97 = Adafruit_MCP4725.MCP4725(address=0x61, busnum=1)

voltageConversion = 300 * 1800 / 1709
currentConversion = 3.3/10

#returns voltage and current
def voltageRampCheck():
    currentReading = mcp3428.take_single_reading(1)
    current = currentReading * currentConversion
    voltageReading = mcp3428.take_single_reading(0)
    voltage = voltageReading * voltageConversion
    return voltage, current

def voltageRampUp(goalVoltage):
    
    bitVoltage = 0
    bitCurrent = 4095
    
    # set the voltage to zero. Since the DAC recieves a voltage in bits,
    # and is twelve bits (12 bits), the range
    # we can set these to are between 0 and 4095 for voltages that range from 0 V to 10 V.
    print('------------')
    print('Voltage set to 0 V...')
    print('------------')
    print('Max Current Set to 3.3 mA')
    print('------------')
    
    dac97.set_voltage(bitVoltage)
    dac96.set_voltage(bitCurrent)   
    
    # start timer: we need timers to regulate the rate at which the high voltage is incremented
    
    prevTime = time.time()

    #begin while loop of increments
    while 1:
        # read the voltage at the beginning of each iteration.
        # these readings are from 0 to 10 V, so convert wisely

        #get the livetime and what until 1 second passes
        livetime = time.time()
        if livetime-prevTime < 1:
            continue

        currentReading = mcp3428.take_single_reading(1)
        current = currentReading * currentConversion
        voltageReading = mcp3428.take_single_reading(0)
        voltage = voltageReading * voltageConversion

        #resets the prevTime variable for the next increment
        prevTime = livetime
        print('-----------------------------')        
        print('voltage (0 to 3000 V): ' + str(voltage))
        print('voltage (Reading): ' + str(voltageReading))
        print('-----------------------------')
        print('max current (0 to 10 V): ' + str(current))
        print('-----------------------------')
                
        if voltage < goalVoltage:
            bitVoltage += 50
            print('bit: ' + str(bitVoltage))
            print('-----------------------------')
            dac97.set_voltage(bitVoltage)
        else:
            holdValue(goalVoltage, bitVoltage)
            break

def voltageRampDown(goalVoltage):
    #get initial values
    voltageReading = mcp3428.take_single_reading(0)
    currentReading = mcp3428.take_single_reading(1)
    bitCurrent = 4095

    #for now this number has to be manually changed to properly use ramp down
    bitVoltage = 250
    
    prevTime = time.time()

    while 1:

        livetime = time.time()
        if livetime-prevTime < 1:
            continue

        currentReading = mcp3428.take_single_reading(1)
        current = currentReading * currentConversion
        voltageReading = mcp3428.take_single_reading(0)
        voltage = voltageReading * voltageConversion
        prevTime = livetime

        print('-----------------------------')
        print('voltage: ' + str(voltage))
        print('-----------------------------')
        print('max current: ' + str(current))
        print('-----------------------------')

        if voltage > goalVoltage: #and voltage >= 100:
            bitVoltage -= 50
            print('bit: ' + str(bitVoltage))
            print('-----------------------------')
            dac97.set_voltage(bitVoltage)
        if bitVoltage < 100:
            dac97.set_voltage(0)
            break



def holdValue(goalVoltage, bitVoltage):
    print('Bringing to ' + str(goalVoltage) + 'Volts.....')
    counts = 0
    bitCurrent = 4095
    while 1:
        voltageReading = mcp3428.take_single_reading(0)
        voltage = voltageReading * voltageConversion

        if counts >= 100:
            dac97.set_voltage(bitVoltage)
            break
        counts = counts + 1
        if voltage < (goalVoltage - 1):
            bitVoltage += 1
            dac97.set_voltage(bitVoltage)
        elif voltage > (goalVoltage + 1):
            bitVoltage -= 1
            dac97.set_voltage(bitVoltage)
            print('voltage: ' + str(mcp3428.take_single_reading(0) * voltageConversion))
        
#reset the parameters of the ramp below, then run the function voltage_ramp.exe
if __name__ == '__main__':
    print('Voltage Ramp')
    print('\r\n')
    goalVoltage = int(input('Enter high voltage amount: '))
    voltRead = mcp3428.take_single_reading(0)
    if voltRead < goalVoltage:
        voltageRampUp(goalVoltage)
    else:
        voltageRampDown(goalVoltage)
