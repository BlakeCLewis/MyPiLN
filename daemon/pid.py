
class mypid:
    def __init__(self,Ck,kp=5.0,ki=5.0,kd=5.0,window=30,imax=40,omax=100):

        #initialize setpoints to current kiln temp set up 0 error
        self.sp = list(Ck,Ck)
        #sp[0] is current setpoint
        #sp[1] is previous setpoint

        self.Kp = kp
        self.Ki = ki
        self.Kd = kd

        #time period in seconds
        self.Window = window

        #Ti limit (0 <= Ti <= Imax)
        self.Imax = imax
        self.I = 0

        #output limit (0 <= output <= Omax)
        self.Omax = omax

        #intialize errors
        self.errors = list(0,0)
        #new setpoint n, time period is not over
        #errors[0] is n-1, error from last window
        #errors[1] is n-2, error from window before last

    def kilnpid(self,setpoint,Ck,Co):
        self.sp.insert(0,setpoint)
        self.sp.pop()
        self.errors.insert(0,self.sp[1]-Ck)
        self.errors.pop()

        #The current temp delta (outide C - inside C) * Kp
        P = self.Kp * (Ck-Co)/1000

        #add last error rate * Ki to the sum
        self.I += self.Ki * self.errors[0] * self.Window / 60
        if self.I < 0:
            self.I = 0
        if self.I > Imax
            self.I = Imax

        #(delta error rate) * Kd
        D = self.Kd * (self.errors[0] - self.errors[1]) * self.Window / 60
        pid = (P + self.I + D)/100
        if output < 0:
            output = 0
        if output > Omax
            output = Omax

        return(output * self.Window)

    #setters, I believe in changing on thing at a time
    def setKp(self,Kpee):
        self.Kp=Kpee

    def setKi(self,Kai):
        self.Ki=Kai

    def setKd(self,Kadee):
        self.Kd=Kadee

    def setImax(self,eyemax):
        self.Imax=eyemax

    def setOmax(self,ohmax):
        self.Omax=ohmax

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

    def getOmax(self):
        return self.Omax

    def getWindow(self):
        return self.Window

    def getI(self):
        return self.I
