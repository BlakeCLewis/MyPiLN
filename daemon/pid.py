
class mypid:
    def __init__(self,Ck,kp=.5,ki=5,kd=5,window=30,imin=100,imax=0,omin=100,omax=0):

        #initialize setpoints to current kiln temp set up 0 error
        self.sp = list(Ck,Ck)
        #sp[0] is current setpoint
        #sp[1] is previous setpoint

        self.Kp = kp
        self.Ki = ki
        self.Kd = kd

        self.Window = window
        #time period in seconds

        #Ti limit (Imin <= Ti <= Imax)
        self.Imin = imin
        self.Imax = imax
        self.I = 0

        #output limit (Omin <= output <= Omax)
        self.Omin = omin
        self.Omax = omax

        self.errors = list(0,0)
        #current setpoint is 'n' is not over
        #errors[0] is n-1 last window's error
        #errors[1] is n-2 window's error 

    def kilnpid(self,setpoint,Ck,Co):
        self.sp.insert(0,setpoint)
        self.sp.pop()
        self.errors.insert(0,self.sp[1]-Ck)
        self.errors.pop()

        #The current temp delta (outide C - inside C) * Kp
        P = self.Kp * (Ck-Co)

        #add last error rate * Ki to the sum
        self.I += self.Ki * self.errors[0] * self.Window / 60
        if self.I<Imin:
            self.I=Imin
        if self.I>Imax
            self.I=Imax

        #(delta error rate) * Kd
        D = self.Kd * (self.errors[0] - self.errors[1]) * self.Window / 60
        pid = (P + self.I + D)/100
        if output<Omin:
            output=Omin
        if output>Omax
            output=Omax

        return(output * self.Window)

    #setters, I believe in changing on thing at a time
    def setKp(self,KP):
        self.Kp=KP

    def setKi(self,Kai):
        self.Ki=Kai

    def setKd(self,Kadie):
        self.Kd=Kadie

    def setImax(self,eyemax):
        self.Imax=eyemax

    def setImin(self,eyemin):
        self.Imin=eyemin

    def setOmax(self,ohmax):
        self.Omax=ohmax

    def setOmin(self,ohmin):
        self.Omin=ohmin

    def setWindow(self,bod):
        self.Window=bod

    def setI(self,eye):
        self.I = eye

    #getters
    def getKp(self):
        return self.Kp

    def getKi(self):
        return self.Ki

    def getKd(self):
        return self.Kd

    def getImax(self):
        return self.Imax

    def getImin(self):
        return self.Imin

    def getOmax(self):
        return self.Omax

    def getOmin(self):
        return self.Omin

    def getWindow(self):
        return self.Window

    def getI(self):
        return self.I
