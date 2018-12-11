# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
from __future__ import print_function
from datetime import datetime
import time
import math
import datetime
import RPi.GPIO as GPIO, time, os
import urllib2

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
##=========================================================================================================
#paramters here
ct1_offset   = 0.0
max_voltage  = 600.0      # voltage sensor is 600A max
adc_samples  = 6000
ref_voltage  = 3300        ## 3300=3.3v 5000=5.0v
ref_ical     = 20
ref_sampleI  = 512
number_of_ct = 1
##=========================================================================================================
# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

## hardware SPI mapping
## MCP3008 VDD to Raspberry Pi 3.3V
## MCP3008 VREF to Raspberry Pi 3.3V
## MCP3008 AGND to Raspberry Pi GND
## MCP3008 DGND to Raspberry Pi GND
## MCP3008 CLK to Raspberry Pi SCLK
## MCP3008 DOUT to Raspberry Pi MISO
## MCP3008 DIN to Raspberry Pi MOSI
## MCP3008 CS/SHDN to Raspberry Pi CE0

print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)

values = [0]*8
ct     = [0]*8
array  = [0]*adc_samples
rms    = [0]*8
##=========================================================================================================
## RMS calculation function
def CalcIrms(ct):
    NUMBER_OF_SAMPLES = adc_samples
    SUPPLYVOLTAGE = ref_voltage ## 3300=3.3v 5000=5.0v
    ICAL = ref_ical
    sumI = 0
    sampleI = ref_sampleI
    filteredI = 0

    for n in range (0, NUMBER_OF_SAMPLES):
   
        lastSampleI = sampleI
    
        values[i] = mcp.read_adc(0)
        sampleI = values[i]
        array[n] = sampleI
        sampleI=values[i]
 
        lastFilteredI = filteredI
        filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI)
        sqI = filteredI * filteredI
        sumI += sqI           
        sampleI_old = sampleI    
   
        I_RATIO = ICAL * ((SUPPLYVOLTAGE/1000.0) / 1023.0)
        Irms = I_RATIO * math.sqrt(sumI / NUMBER_OF_SAMPLES)
        sumI = 0
        rms[i] = round((Irms),2)
    print(' ')
    return Irms
## end of RMS calculation
##=========================================================================================================
    
    
# mcp3008 input
ct1_adc = 0
ct2_adc = 1
ct3_adc = 2
ct4_adc = 3


# Main program loop.
while True:
# Read all the ADC channel values in a list.

    for i in range(number_of_ct):
    # The read_adc function will get the value of the specified channel (0-7).
        ct[0] = round(CalcIrms(values[i]),2)
# Print the ADC values.
#------------------------------------------------------------------------------------------------------
    print('Raw | {0:>4} | {1:>4} |'.format(*values), end='')
    print('AMP | {0:>4} | {1:>4} |'.format(*rms))

time.sleep(5);'
