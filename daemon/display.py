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

    def writeFire(self,State,ID,Seg,ReadT,TargT,RampT,ETR):
        line0 = 'Sta:' + str(State)
        line0 += str(self.blanks[len(line0)-20:])

        line1 = u'Pro:' + str(ID)
        line1 += str(self.blanks[len(line1)-10:])
        line1 += u'Seg:' + str(Seg) + ' ' + str(next(self._wheel))
        line1 += str(self.blanks[len(line1)-20:])

        line2 = u'Tmp:' + str(int(ReadT)) + '\xb0C'
        line2 += str(self.blanks[len(line2)-10:])
        line2 += u'Trg:' + str(int(TargT)) + '\xb0C'
        line2 += str(self.blanks[len(line2)-20:])

        line3 = u'Ram:' + str(int(RampT)) + '\xb0C'
        line3 += str(self.blanks[len(line3)-10:])
        line3 += 'T:' + ETR
        line3 += str(self.blanks[len(line3)-20:])

        self.cursor_pos = (0, 0)
        self.write_string(str(line0))

        self.cursor_pos = (1, 0)
        self.write_string(str(line1))

        self.cursor_pos = (2, 0)
        self.write_string(str(line2))

        self.cursor_pos = (3, 0)
        self.write_string(str(line3))

    def writeIdle(self,ReadT0,ReadI0,ReadT1,ReadI1,ReadT2,ReadI2):
        line0 = u'IDLE: '+next(self._wheel)
        line1 = u'Tmp0: '+str(int(ReadT0))+'\xb0C  '+str(int(ReadI0))+'\xb0C'
        line2 = u'Tmp1: '+str(int(ReadT1))+'\xb0C  '+str(int(ReadI1))+'\xb0C'
        line3 = u'Tmp2: '+str(int(ReadT2))+'\xb0C  '+str(int(ReadI2))+'\xb0C'

        line0 += str(self.blanks[len(line0)-20:])
        line1 += str(self.blanks[len(line1)-20:])
        line2 += str(self.blanks[len(line2)-20:])
        line3 += str(self.blanks[len(line3)-20:])

        lcd.cursor_pos = (0, 0)
        lcd.write_string(line0)

        lcd.cursor_pos = (1, 0)
        lcd.write_string(line1)

        lcd.cursor_pos = (2, 0)
        lcd.write_string(line2)

        lcd.cursor_pos = (3, 0)
        lcd.write_string(line3)

