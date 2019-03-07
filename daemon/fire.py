#!/usr/bin/env python3
from signal import *
import os
import time
import math
import sys
import sqlite3
import RPi.GPIO as GPIO
import Adafruit_GPIO
import Adafruit_GPIO.SPI as SPI
from Adafruit_MAX31856 import MAX31856 as MAX31856
from display import display
# initialize display (hardware i2c in display.py)
lcd = display()
lcd.clear()
GPIO.setmode(GPIO.BCM)
AppDir = '/home/mypiln/MyPiLN'
StatFile = '/home/mypiln/MyPiLN/html/pilnstat.json'
#--- sqlite3 db file ---
SQLDB = '/home/mypiln/MyPiLN/db/PiLN.sqlite3'
#--- Global Variables ---
ITerm = 0.0
LastErr = 0.0
SegCompStat = 0
LastTmp = 0.0
#--- MAX31856 only works on SPI0, SPI1 cannot do mode=1 ---
SPI_PORT = 0    #SPI0
SPI_DEVICE = 0  #CS0
Sensor0 = MAX31856(tc_type=MAX31856.MAX31856_K_TYPE,spi = SPI.SpiDev(SPI_PORT,SPI_DEVICE))
#---output GPIOs for 3 Relays ---
#HEAT = (22, 23, 24)
#---testing w/ 1 relay ---
HEAT = (24)
for element in HEAT:
    GPIO.setup(element, GPIO.OUT)
    GPIO.output(element, GPIO.LOW)
#--- input GPIO for kilnsitter ---
KS = 27
GPIO.setup(KS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def kilnsitter():
    state = GPIO.input(KS)
    return (state)
#--- Cleanup ---
def clean(*args):
    print("\nProgram ending! Cleaning up...\n")
    lcd.close(clear=True)
    for element in HEAT:
        GPIO.output(element, False)
    GPIO.cleanup()
    print("All clean - Stopping.\n")
    os._exit(0)
for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, clean)
time.sleep(1)
def Fire(RunID, Seg, TargetTmp1, Rate, HoldMin, Window, Kp, Ki, Kd, KSTrg):
"""
fires a segment
  initial state
  ramp loop
  hold loop
  update display
  update json stat file for web interface
  sql update firing table for record of firing


"""
    global SegCompStat
    global wheel
    TargetTmp = TargetTmp1
    RampMin = 0.0
    RampTmp = 0.0
    ReadTmp = 0.0
    LastTmp = 0.0
    StartTmp = 0.0
    TmpDif = 0.0
    Steps = 0.0
    StepTmp = 0.0
    StartSec = 0.0
    EndSec  = 0.0
    NextSec = 0.0
    RunState = "Ramp"
    Cnt = 0
    RampTrg = 0
    ReadTrg = 0
    while RunState != "Stopped"  and  RunState != "Complete":
        if time.time() >= NextSec:
            Cnt += 1                         # record keeping only
            NextSec = time.time() + Window   # time at end of window
            LastTmp = ReadTmp
            ReadTmp = Sensor0.read_temp_c()
            ReadITmp = Sensor0.read_internal_temp_c()
            if math.isnan(ReadTmp)  or  ReadTmp == 0  or  ReadTmp > 1330:
                # error reading
                ReadTmp = LastTmp
            if RampTrg == 0:
                # if RampTmp has not yet reached TargetTmp increase RampTmp
                RampTmp += StepTmp
            if TmpDif > 0:  # Rising Segment
                #---- kilnsitter trigger ----
                if not kilnsitter() and KSTrg:
                    # if KS open and not been here before
                    KSTrg = False
                    RampTmp = TargetTmp = ReadTmp
                    if ReadTrg == 0:
                        # HoldMin has not been set
                        EndSec = int(time.time()) + HoldMin*60
                        # stop RampTrg and ReadTrg checks
                        ReadTrg = RampTrg = 1
                    RunState = 'KilnSitter/Hold'
                #---- RampTrg ----
                if RampTrg == 0 and RampTmp >= TargetTmp:
                    # RampTmp (window target temp) is 1 cycle away
                    # only will trigger once per segment
                    # RampTmp will no longer be incremented
                    RampTmp = TargetTmp
                    # reduce RampTmp to TargetTemp
                    RampTrg = 1
                    # set the ramp indicator
                    if ReadTrg == 1:
                        RunState = "Ramp/Hold"
                    else:
                        RunState = "Ramp complete"
                #---- ReadTrg ----
                if ((TargetTmp-ReadTmp <= TargetTmp*0.006) 
                    or (ReadTmp >= TargetTmp)) and ReadTrg == 0:
                    ReadTrg = 1
                    EndSec = int(time.time()) + HoldMin*60
                    if RampTrg == 1:
                        RunState = "Target/Hold"
                    else:
                        RunState = "Target Reached"
            elif TmpDif < 0: # Falling Segment
                # Ramp temp dropped to target
                if RampTmp <= TargetTmp  and  RampTrg == 0:
                    RampTmp = TargetTmp
                    RampTrg = 1
                    if ReadTrg == 1:
                        RunState = "Target/Ramp"
                    else:
                        RunState = "Ramp complete"
                if ((ReadTmp-TargetTmp <= TargetTmp*0.006)
                        or (ReadTmp <= TargetTmp)) and ReadTrg == 0:
                    # Read temp dropped to target or close enough
                    ReadTrg = 1
                    EndSec = int(time.time()) + HoldMin*60
                    if RampTrg == 1:
                        RunState = "Ramp/Target"
                    else:
                        RunState = "Target Reached"
            if StartTmp == 0:
                # initial setup
                StartTmp = ReadTmp
                StartSec = int(time.time())
                NextSec = StartSec + Window
                TmpDif = TargetTmp - StartTmp
                RampMin = abs(TmpDif) * 60 / Rate # minutes to target at rate
                Steps = RampMin * 60 / Window     # steps of window size
                StepTmp = TmpDif / Steps          # degrees / step
                # estimated end of segment
                EndSec = StartSec + RampMin*60 + HoldMin*60
                RampTmp = StartTmp + StepTmp      # window target
                if ((TmpDif > 0 and RampTmp > TargetTmp) 
                   or (TmpDif < 0 and RampTmp < TargetTmp)):
                    # Hey we there before we even started!
                    RampTmp = TargetTmp # set window target to final target
                LastErr = 0.0
            # run state through pid
            Output = Update(RampTmp, ReadTmp, 100, 0, Window, Kp, Ki, Kd)
            CycleOnSec = Window * Output * 0.01
            if CycleOnSec > Window:
                CycleOnSec = Window
            RemainSec = EndSec - int(time.time()) 
            RemMin, RemSec = divmod(RemainSec, 60)
            RemHr, RemMin = divmod(RemMin, 60)
            RemTime = "%d:%02d:%02d" % (RemHr, RemMin, RemSec)
            if Output > 0:
                for element in HEAT:
                    GPIO.output(element, True)
                time.sleep(CycleOnSec)
            if Output < 100:
                for element in HEAT:
                    GPIO.output(element, False)
            # Write status to file for reporting on web page
            sfile = open(StatFile, "w+")
            sfile.write('{\n' +
                '  "proc_update_utime": "' + str(int(time.time())) + '",\n'
                + '  "readtemp": "' + str(int(ReadTmp)) + '",\n' 
                + '  "run_profile": "' + str(RunID) + '",\n' 
                + '  "run_segment": "' + str(Seg) + '",\n' 
                + '  "ramptemp": "' + str(int(RampTmp)) + '",\n' 
                + '  "targettemp": "' + str(int(TargetTmp)) + '",\n' 
                + '  "status": "' + str(RunState) + '",\n' 
                + '  "segtime": "' + str(RemTime) + '"\n'  
                + '}\n'
            )
            sfile.close()
            lcd.writeFire(RunState,RunID,Seg,ReadTmp,TargetTmp,RampTmp,RemTime)
            sql = """INSERT INTO firing(run_id, segment, dt, set_temp, temp, int_temp, pid_output) VALUES ( ?,?,?,?,?,?,? ); """
            p = (RunID, Seg, time.strftime('%Y-%m-%d %H:%M:%S'),
                 RampTmp, ReadTmp, ReadITmp, Output)
            try:
                SQLCur.execute(sql, p)
                SQLConn.commit()
            except:
                SQLConn.rollback()
            # Check if profile is still in running state
            sql = "SELECT * FROM profiles WHERE state=? AND run_id=?;"
            p = ('Running', RunID)
            SQLCur.execute(sql, p)
            result = SQLCur.fetchall()
            if len(result) == 0:
                SegCompStat = 1 
                RunState = "Stopped"
            if time.time() > EndSec and ReadTrg == 1:
                # hold time is over and reached target
                RunState = "Complete"
    return KSTrg
# --- end Fire() ---
lcd.clear()
SQLConn = sqlite3.connect(SQLDB)
SQLConn.row_factory = sqlite3.Row
SQLCur = SQLConn.cursor()
while 1:
    # Get temp
    ReadTmp = Sensor0.readTempC()
    ReadITmp = Sensor0.readInternalC()
    ReadTmp1 = Sensor0.readTempC()
    ReadITmp1 = Sensor0.readInternalC()
    #ReadTmp2 = Sensor2.read_temp_c)
    #ReadITmp2 = Sensor2.read_internal_temp_c()
    if math.isnan(ReadTmp):
        ReadTmp = LastTmp
    sfile = open(StatFile, "w+")
    sfile.write('{\n' +
        '  "proc_update_utime": "' + str(int(time.time())) + '",\n'
        + '  "readtemp": "' + str(int(ReadTmp)) + '",\n'
        + '  "run_profile": "none",\n'
        + '  "run_segment": "n/a",\n'
        + '  "ramptemp": "n/a",\n'
        + '  "status": "n/a",\n'
        + '  "targettemp": "n/a"\n'
        + '}\n'
    )
    sfile.close()
    lcd.writeIdle(ReadTmp,ReadITmp,ReadTmp1,ReadITmp1) #,ReadT2,ReadI2)
    if kilnsitter(): #if kilnsitter is armed
        KSseg = True
        # --- Check for 'Running' firing profile ---
        sql = "SELECT * FROM profiles WHERE state=?;"
        p = ('Running',)
        SQLCur.execute(sql, p)
        Data = SQLCur.fetchall()
        #--- if Running profile found, then set up to fire, woowo! --
        if len(Data) > 0:
            RunID = Data[0]['run_id']
            Kp = float(Data[0]['p_param'])
            Ki = float(Data[0]['i_param'])
            Kd = float(Data[0]['d_param'])
            StTime = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "UPDATE profiles SET start_time=? WHERE run_id=?;"
            p = (StTime, RunID)
            try:
                SQLCur.execute(sql, p)
                SQLConn.commit()
            except:
                SQLConn.rollback()
            # Get segments
            sql = "SELECT * FROM segments WHERE run_id=?;"
            p = (RunID,)
            SQLCur.execute(sql, p)
            ProfSegs = SQLCur.fetchall()
            # --- begin firing loop ---
            for Row in ProfSegs:
                RunID = Row['run_id']
                Seg = Row['segment']
                TargetTmp = Row['set_temp']
                Rate = Row['rate']
                HoldMin = Row['hold_min']
                Window = Row['int_sec']
                if SegCompStat == 1:
                else:
                    StTime = time.strftime('%Y-%m-%d %H:%M:%S')
                    #--- mark started segment with datatime ---
                    sql = """UPDATE segments SET start_time=?  WHERE run_id=? AND segment=?; """
                    p = (StTime, RunID, Seg)
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                    except:
                        SQLConn.rollback()
                    time.sleep(0.5)
                    #--- fire segment ---
                    KSTrg = KSseg
                    KSseg = Fire(RunID, Seg, TargetTmp, Rate, HoldMin, Window, Kp, Ki, Kd, KSTrg)
                    for element in HEAT:
                        GPIO.output(element, False) ## make sure elements are off
                    EndTime=time.strftime('%Y-%m-%d %H:%M:%S')
                    #--- mark segment finished with datetime ---
                    sql = """UPDATE segments SET end_time=?  WHERE run_id=? AND segment=?; """
                    p = (EndTime, RunID, Seg)
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                    except:
                        SQLConn.rollback()
                    lcd.clear()
            # --- end firing loop ---
            if SegCompStat == 1:
            else:
                EndTime = time.strftime('%Y-%m-%d %H:%M:%S')
                sql = "UPDATE profiles SET end_time=?, state=? WHERE run_id=?;"
                p = (EndTime, 'Completed', RunID)
                try:
                    SQLCur.execute(sql, p)
                    SQLConn.commit()
                except:
                    SQLConn.rollback()
            SegCompStat = 0
    time.sleep(2)
SQLConn.close()
