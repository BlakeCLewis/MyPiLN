from itertools import cycle


class blah:
    def __init__(self):
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
        print(str(line0))
        print(str(line1))
        print(str(line2))
        print(str(line3))
    def writeIdle(self,ReadT0,ReadI0,ReadT1,ReadI1,ReadT2,ReadI2):
        line0 = u'IDLE: '+next(self._wheel)
        line1 = u'Tmp0: '+str(int(ReadT0))+'\xb0C  '+str(int(ReadI0))+'\xb0C'
        line2 = u'Tmp1: '+str(int(ReadT1))+'\xb0C  '+str(int(ReadI1))+'\xb0C'
        line3 = u'Tmp2: '+str(int(ReadT2))+'\xb0C  '+str(int(ReadI2))+'\xb0C'
        line0 += str(self.blanks[len(line0)-20:])
        line1 += str(self.blanks[len(line1)-20:])
        line2 += str(self.blanks[len(line2)-20:])
        line3 += str(self.blanks[len(line3)-20:])
        print(str(line0))
        print(str(line1))
        print(str(line2))
        print(str(line3))

duh=blah()
duh.writeFire('Running',19,2,556,1315,108,'10:00:10')
duh.writeIdle(1222,20,1225,20,1223,20)
