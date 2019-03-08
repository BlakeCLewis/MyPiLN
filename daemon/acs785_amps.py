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


"""
sct-013 1v range over 50amps

off=515
on= 428-609
median 518
609-518.5 = 90.5

sct-013 is 1V at 50amps
ADC 512 steps for 1.65V
50amps=310steps

50amps = 1V/1.65 =310S/512

x/50=90/310

90*50/310 = 14.5 amps

take ~20 samples
amps=(max-min)*50/310

"""
