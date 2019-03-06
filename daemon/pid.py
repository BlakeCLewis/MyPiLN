"""
I use Celsius for a few reasons:
  #1 The thermocouple reports Celsius and converting to F creates rounding errors
  #2 If using F, and user wants C, then double conversion really sucks
  #3 This is science, so C it is!

From kiln firing data, using a marginally stable algorithm, averaging output
   of every temp bracket 100-200,200-300,...
At ouside temp of 4C, I used temp - 4, each bracket has an average output
  increase of 6, <100C is 5%, 100-200 is 12%, ...
At 1000C it is ~= 60%. A few holds in the firing allowed comparing climbs to holds.
Based on this data, I propose that the heat loss of the system requires
  about 6% of 'on' time/100C temp diff inside to outside.

  P =  Kp/1000 * (Tk-To)
  'Tk' is temp inside
  'To' temp outside (using internal temp of thermocouple chip)
  1000 allows integer changes in Kp instead of .006, we can use 6
  P is the ~= heat required to compensate for insulation value of the system

  I += Ki * error[n-1] * Window / 60
  error[n-1] is the error from the last window.
  This window has not even started, so it's error is unknown.
  Window is sample interval in seconds which scales the error to a rate
  A 30 sec window w/ an error=2, is the same as a 60 sec window w/ error=4
  The Window size can change without a change in Ki to compensate

  D = Kd * (error[n-1] - error[n-2]) * Window / 60
  error[n-1] is last window error (setpoint[n-1]-current_temp)
  error[n-2] error from the window before n-1
  D = (e1 - e2) * s/60 # change in error rate per minute
  If error rate decreases, we are reaching the goal and we need to slow down to not overshoot
  Again the  Window size can change without a change in Kd to compensate

"""

class mypid:
    def __init__(self,Ck,kp=5.0,ki=5.0,kd=5.0,window=45,imax=40,omax=100):

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
