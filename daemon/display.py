import RPi.GPIO as GPIO
import spidev
from RPLCD import i2c
from itertools import cycle

class display:
    def __init__(self):
        self = i2c.CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
                          cols=20, rows=4, dotsize=8, charmap='A02',
                          auto_linebreaks=False, backlight_enabled=True
        )
        smiley = (0b00000,0b01010,0b01010,0b00000,0b10001,0b10001,0b01110,0b00000)
        degree = (0b01100,0b10010,0b10010,0b01100,0b00000,0b00000,0b00000,0b00000)
        backslash = (0b00000,0b10000,0b01000,0b00100,0b00010,0b00001,0b00000,0b00000)
        lcd.create_char(0, smiley)    #\x00
        lcd.create_char(1, degree)    #\x01
        lcd.create_char(2, backslash) #\x02
        self._wheeley = '-','\x02','|','/','\x00'
        self._wheel = cycle(self._wheeley)
        self.blanks='                    '

    def writeFire(RunState,RunID,Segment,ReadTmp,TargetTmp,RampTmp,RemainTime):

        line0 = u'Sta:' + str(RunState)
        line0 += str(blanks[len(line0)-20:])

        line1 = u'Pro:' + str(RunID)
        line1 += blanks[len(line1)-10:]
        line1 += 'Seg:' + str(Seg) + ' ' + str(next(self._wheel))
        line1 += blanks[len(line1)-20:]
        
        line2 = u'Tmp:' + str(int(ReadTmp)) + '\x01'
        line2 += blanks[len(line2)-10:]
        line2 += 'Trg:' + str(int(TargetTmp)) + '\x01' 
        line2 += blanks[len(line2)-20:]

        line3 = u'Ram:' + str(int(RampTmp)) + '\x01'
        line3 += blanks[len(line3)-10:]
        line3 += 'T:' + RemainTime)

        self.cursor_pos = (0, 0)
        self.write_string(str(line0))
        self.cursor_pos = (1, 0)
        self.write_string(str(line1))
        self.cursor_pos = (2, 0)
        self.write_string(str(line2))
        self.cursor_pos = (3, 0)
        self.write_string(str(line3))

    def writeIdle():
        line0 = 'IDLE: ' + next(self._wheel)
        line1 = 'Tmp0: ' + str(int(ReadCTmp0)) + '\x01C ' + str(int(ReadCITmp0)) + '\x01C'
        line2 = 'Tmp1: ' + str(int(ReadCTmp1)) + '\x01C ' + str(int(ReadCITmp1)) + '\x01C'
        line3 = 'Tmp2: ' + str(int(ReadCTmp2)) + '\x01C ' + str(int(ReadCITmp2)) + '\x01C'
        line0 += blanks[len(line0)-20:]
        line1 += blanks[len(line1)-20:]
        line2 += blanks[len(line2)-20:]
        line3 += blanks[len(line3)-20:]

        lcd.cursor_pos = (0, 0)
        lcd.write_string(lines[0])
        lcd.cursor_pos = (1, 0)
        lcd.write_string(lines[1])
        lcd.cursor_pos = (2, 0)
        lcd.write_string(lines[2])
        lcd.cursor_pos = (3, 0)
        lcd.write_string(lines[3])

from itertools import cycle
class blake:
    def __init__(self):
         self._wheeley = '-','\x02','|','/','\x00'
         self._wheel = cycle(self._wheeley)
    def display(self):
         print(next(self._wheel))

duh=blake()
duh.display()

