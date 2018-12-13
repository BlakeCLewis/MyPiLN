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
        self._blanks='                    '

    def writeFire(RunState,RunID,Segment,ReadTmp,TargetTmp,RampTmp,RemainTime):        
        self.cursor_pos = (0, 0)
        self.write_string(u'Sta:' + str(RunState) + blanks[20-len(RunState)-20:])
        self.cursor_pos = (1, 0)
        self.write_string(u'Pro:' + str(RunID) + blanks[len(RunID)-20:])
        self.cursor_pos = (1, 10)
        self.write_string(u'Seg:' + str(Seg) + ' ' + next(self._wheel))
        self.cursor_pos = (2, 0)
        self.write_string(u'Tmp:' + str(int(ReadTmp)) + '\x01' + blanks[len(ReadTmp+' ')-20:])
        self.cursor_pos = (2, 10)
        self.write_string(u'Trg:' + str(int(TargetTmp)) + '\x01' )
        self.cursor_pos = (3, 0)
        self.write_string(u'Ram:' + str(int(RampTmp)) + '\x01' + blanks[len(RampTmp+' ')-20:])
        self.cursor_pos = (3, 10)
        self.write_string('T:' + RemainTime)

    def writeIdle():
        lines[0] = 'IDLE: ' + next(self._wheel)
        lines[1] = 'Tmp0: ' + str(int(ReadCTmp0)) + '\x01C ' + str(int(ReadCITmp0)) + '\x01C'
        lines[2] = 'Tmp1: ' + str(int(ReadCTmp1)) + '\x01C ' + str(int(ReadCITmp1)) + '\x01C'
        lines[3] = 'Tmp2: ' + str(int(ReadCTmp2)) + '\x01C ' + str(int(ReadCITmp2)) + '\x01C'
        lines[0] += str(blanks[len(lines[0])-20:])
        lines[2] += str(blanks[len(lines[2])-20:])
        lines[1] += str(blanks[len(lines[1])-20:])
        lines[3] += str(blanks[len(lines[3])-20:])

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

