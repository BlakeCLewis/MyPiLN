import Adafruit_GPIO as Adafruit_GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31856.MAX31856 as MAX31856
import Adafruit_MAX31855.MAX31855 as MAX31855

#MAX31856 uses mode 1
#MAX31855 uses mode 0
#they need to be on different hardware CS pins
# this will multiplex the 2 CS pins by doning CS on non SPI hardware pins
# we will manually set the non hardware CS pins to double up

class MAX3185X(MAX31856,MAX31855): #w1 
    def __init__():
        #--- MAX31856 only works on SPI0, SPI1 cannot do mode=1 ---
        _tc0 = MAX31856.MAX31856__init__(spi = SPI.SpiDev(0, 0)) #SPI0,CE0
        #--- MAX31855 ---
        _tc1 = MAX31855.MAX31855__init__(spi = SPI.SpiDev(0, 1)) #SPI0,CE1
        #--- MAX31850
        #have to figure this one out I have been using kernel w1 driver

        GPIO.setmode(GPIO.BCM)
        self.csPin1=5
        self.csPin2=6
        GPIO.setup(self.csPin1, GPIO.OUT)
        GPIO.setup(self.csPin2, GPIO.OUT)

    def _read56():
        C=self._tc0.read_temp_c()
        IC=self._tc0.read_internali_temp_c()
        return (C,IC) 

    def _read55():
        C=self._tc1.readTempC()
        ICself._tc1.readInternalC()
        return (C,IC) 

    def readtc0():
        t=self._read56()
        return t

    def readtc1():
        GPIO.output(self.csPin2, GPIO.LOW)
        GPIO.output(self.csPin1, GPIO.HIGH)
        t=self._read55()
        GPIO.output(self.csPin1, GPIO.LOW)
        return t

    def readtc2():
        GPIO.output(self.csPin1, GPIO.LOW)
        GPIO.output(self.csPin2, GPIO.HIGH)
        t=self._read55()
        GPIO.output(self.csPin2, GPIO.LOW)
        return t
