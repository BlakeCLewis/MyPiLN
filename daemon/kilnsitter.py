"""
this is a test script and is not needed for pilnfired.py
close kilnsitter and run 'python3 kilnsitter.py'
state should be 'ARMED'
while klinsitter.py is running open the kilnsitter by dropping the gate
state should change to 'DISARMED'

"""
import os
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
KS = 27
GPIO.setup(KS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def clean(*args):
    GPIO.cleanup()
    os._exit(0)

def kilnsitter():
    state = GPIO.input(KS)
    return (state)

dastate = kilnsitter()
while dastate:
  print ('ARMED')
  dastate = kilnsitter()
  time.sleep(3)

print('DISARMED')

