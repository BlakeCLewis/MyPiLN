import RPi.GPIO as GPIO
import spidev
from RPLCD import i2c
from itertools import cycle

class display:(i2c)
    def __init__(self):
        i2c.CharLCD.__init__(self,i2c_expander='PCF8574', address=0x27, port=1,
                    cols=20, rows=4, dotsize=8, charmap='A02',
                    auto_linebreaks=False, backlight_enabled=True
        )
        smile=(0b00000,0b01010,0b01010,0b00000,0b10001,0b10001,0b01110,0b00000)
        degre=(0b01100,0b10010,0b10010,0b01100,0b00000,0b00000,0b00000,0b00000)
        bksls=(0b00000,0b10000,0b01000,0b00100,0b00010,0b00001,0b00000,0b00000)
        self.display.create_char(0, smile) #\x00
        self.display.create_char(1, degre) #\x01
        self.display.create_char(2, bksls) #\x02
        self._wheeley = '-','\x02','|','/','\x00'
        self._wheel = cycle(self._wheeley)
        self.blank20 = '                    '

    def writeFire(self,State,ID,Seg,ReadT,TargT,RampT,ETR):

        line0 = str(State) + '                   '

        line1a = 'Pr ' + str(ID) + '      '
        line1b = 'Sg ' + str(Seg) + ' ' + str(next(self._wheel)) + '   '
        line1 = line1a[0:11] + line1b[0:9]

        line2a = 'Tm ' + str(int(ReadT)) + '\x01C  '
        line2b = 'Rp ' + str(int(RampT)) + '\x01  '
        line2 = line2a[0:11] + line2b[0:10]

        line3a = 'Tr ' + str(int(TargT)) + '\x01C   '
        line3b = ETR
        line3 = line3a[0:11] + line3b[0:8]

        self.display.cursor_pos = (0, 0)
        self.display.write_string(line0[0:19])
        self.display.cursor_pos = (1, 0)
        self.display.write_string(line1[0:19])
        self.display.cursor_pos = (2, 0)
        self.display.write_string(line2[0:19])
        self.display.cursor_pos = (3, 0)
        self.display.write_string(line3[0:19])

    def writeIdle(self,ReadT0,ReadI0,ReadT1,ReadI1): #,ReadT2,ReadI2):
        line0='IDLE: ' + next(self._wheel)
        line1='T0 ' + str(int(ReadT0)) + '\x01C  ' + str(int(ReadI0)) + '\x01C'
        line2='T1 ' + str(int(ReadT1)) + '\x01C  ' + str(int(ReadI1)) + '\x01C'
        #line3='T2 ' + str(int(ReadT2)) + '\x01C  ' + str(int(ReadI2)) + '\x01C'

        line0 += str(self.blank20[len(line0)-19:])
        line1 += str(self.blank20[len(line1)-19:])
        line2 += str(self.blank20[len(line2)-19:])
        #line3 += str(self.blank20[len(line3)-19:])

        self.display.cursor_pos = (0, 0)
        self.display.write_string(line0[0:19])
        self.display.cursor_pos = (1, 0)
        self.display.write_string(line1[0:19])
        self.display.cursor_pos = (2, 0)
        self.display.write_string(line2[0:19])
        #self.display.cursor_pos = (3, 0)
        #self.display.write_string(line3[0:19])

def main(n):
    duh=display()
    for i in range(n):
        duh.writeFire('Running',19,2,556+i*4,1315,108,'10:00:10')
        print ('')
    #for i in range(n):
    #    duh.writeIdle(1222+i*2,20,1225+1*2,20,1223,20)
    #    print ('')
    sleep(3)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
#https://www.programiz.com/python-programming/inheritance
