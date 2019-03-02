"""
this is test file only and is not needed for working program
"""
import time
from Adafruit_GPIO import SPI
from Adafruit_MAX31856 import MAX31856
from display import display

SPI_PORT = 0
SPI_DEVICE = 0
sensor = MAX31856(hardware_spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE))

lcd = display()
lcd.clear()

def clean(*args):
    lcd.close(clear=True)
    GPIO.cleanup()
    os._exit(0)

temp = sensor.read_temp_c()
internal = sensor.read_internal_temp_c()
print('Thermocouple Temperature: {0:0.3F}*C'.format(temp))
print('    Internal Temperature: {0:0.3F}*C'.format(internal))

while True:
    datime =  time.time()
    temp = sensor.read_temp_c()
    internal = sensor.read_internal_temp_c()
    lcd.writeIdle(temp,internal,temp,internal)
    time.sleep(3)



