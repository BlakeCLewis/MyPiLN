"""
this is a test of reading ACS785 hall effect current sensor w/ a MCP3008 ADC
"""
import time
from Adafruit_GPIO import SPI
from Adafruit_MCP3008 import MCP3008

SPI_PORT   = 0
SPI_DEVICE = 1
mcp = MCP3008(spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE))

print('Reading MCP3008 values, press Ctrl-C to quit...')
"""
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
# Main program loop.
while True:
    # Read all the ADC channel values in a list.
    values = [0]*8
    for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    time.sleep(0.1)
        # Grab the difference between channel 0 and 1 (i.e. channel 0 minus 1).
        # Note you can specify any value in 0-7 to grab other differences:
        #  - 0: Return channel 0 minus channel 1
        #  - 1: Return channel 1 minus channel 0
        #  - 2: Return channel 2 minus channel 3
        #  - 3: Return channel 3 minus channel 2
        #  - 4: Return channel 4 minus channel 5
        #  - 5: Return channel 5 minus channel 4
        #  - 6: Return channel 6 minus channel 7
        #  - 7: Return channel 7 minus channel 6
"""
while True:
    avalue = []
    bvalue = []
    cvalue = []
    for x in range(20):
        avalue.append(mcp.read_adc_difference(1))
        bvalue.append(mcp.read_adc_difference(3))
        cvalue.append(mcp.read_adc_difference(5))
        time.sleep(0.01)
    aamp=((max(avalue)-min(avalue))*5/62)
    bamp=((max(bvalue)-min(bvalue))*5/62)
    camp=((max(cvalue)-min(cvalue))*5/62)
    print('L1: '+str(aamp)+' ='+str(max(avalue))+'-'+str(min(avalue))+'*5/62')
    print('L2: '+str(bamp)+' ='+str(max(bvalue))+'-'+str(min(bvalue))+'*5/62')
    print('L2: '+str(camp)+' ='+str(max(cvalue))+'-'+str(min(cvalue))+'*5/62')
    time.sleep(5)
"""
sct-013 1v range over 50amps
MCP3008a, 0-1024 digital w/ 512 being 0V, 0 is -1.65V, 1024 is +1.65V

ADC 512 steps for 1.65V
1/1.65 = x/512
512/1.65 = 310
50amps=310steps

off=515
on= 428-609
median 518
(609-428)/2 = 90

(609-428)*50/2/310 = 14.5 amps
25/310=5/62

take ~30 samples
amps=(max()-min())*5/62

"""
