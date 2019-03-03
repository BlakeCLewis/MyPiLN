from signal import *
import os
import time
import RPi.GPIO as GPIO


Window = 10
cycle_percent_of_window = (100,-1,20,40,60,80,10,200,)
#-1 will not trigger 'on' state
#200 will be reduced to 100

GPIO.setmode(GPIO.BCM)
HEAT = (24,)
for element in HEAT:
    GPIO.setup(element, GPIO.OUT)
    GPIO.output(element, GPIO.LOW)

#--- Cleanup ---
def clean(*args):
    print("\nProgram ending! Cleaning up...\n")
    for element in HEAT:
        GPIO.output(element, False)
    GPIO.cleanup()
    print("All clean - Stopping.\n")
    os._exit(0)

for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, clean)

for Output in cycle_percent_of_window:
    CycleOnSec = Window * Output * 0.01
    if CycleOnSec > Window:
        CycleOnSec = Window
    if Output > 0:
        print("==>Relay On")
        for element in HEAT:
            GPIO.output(element, True)
        time.sleep(CycleOnSec)
    if Output < 100:
        print("==>Relay Off")
        for element in HEAT:
            GPIO.output(element, False)
    time.sleep(Window-CycleOnSec)
clean()
