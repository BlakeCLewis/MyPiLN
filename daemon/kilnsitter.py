"""
this is a test script and is not needed for pilnfired.py
close kilnsitter
run 'python3 kilnsitter.py'
    state should be 'ARMED'
open the kilnsitter by dropping the gate
    state will change to 'DISARMED' and exit

"""
from signal import *
import os
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
KS = 27
GPIO.setup(KS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def clean(*args):
    print('doing the cleanup')
    GPIO.cleanup()
    os._exit(0)

for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, clean)

def kilnsitter():
    state = GPIO.input(KS)
    return (state)

dastate = kilnsitter()

while dastate:
  print ('ARMED')
  dastate = kilnsitter()
  time.sleep(3)

print('DISARMED')

clean()

