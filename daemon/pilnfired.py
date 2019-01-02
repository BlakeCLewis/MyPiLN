#!/usr/bin/env python3

from signal import *
import os
import time
import math
import logging as L
import sys
import sqlite3
import RPi.GPIO as GPIO
import Adafruit_GPIO
import Adafruit_GPIO.SPI as SPI
#import Adafruit_MAX31856.MAX31856 as MAX31856
import Adafruit_MAX31855.MAX31855 as MAX31855
from display import display

# initialize display (hardware i2c in display.py)
lcd = display()
lcd.clear()

GPIO.setmode(GPIO.BCM)

AppDir = '/home/pi/git/MyPiLN'
StatFile = '/var/www/html/pilnstat.json'

#--- sqlite3 db file ---
SQLDB = '/var/www/db/MyPiLN/PiLN.sqlite3'

#--- Set up logging ---
LogFile = time.strftime(AppDir + '/log/pilnfired.log')
L.basicConfig(filename=LogFile,
#comment to disable:
#    level=L.DEBUG,
    format='%(asctime)s %(message)s'
)

#--- Global Variables ---
ITerm = 0.0
LastProcVal = 0.0
SegCompStat = 0
LastTmp = 0.0

#--- MAX31856 only works on SPI0, SPI1 cannot do mode=1 ---
#Sensor0 = MAX31856.MAX31856(spi = SPI.SpiDev(0, 0)) #SPI0,CE0
#--- MAX31855 ---
Sensor0 = MAX31855.MAX31855(spi = SPI.SpiDev(1, 0)) #SPI1,CE0
#Sensor1 = MAX31855.MAX31855(spi = SPI.SpiDev(1, 1)) #SPI1,CE1


#def getC():
#    if isinstance(sensor, MAX31856.MAX31856)
#        return sensor.read_temp_c()
#    elif isinstance(sensor, MAX31855.MAX31855)
#        return sensor.readTempC()

#--- Relays ---
HEAT = (24, 23, 22)
for element in HEAT:
    GPIO.setup(element, GPIO.OUT)
    GPIO.output(element, GPIO.LOW)

#--- kiln sitter ---
KS = 27
GPIO.setup(KS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def kilnsitter():
    state = GPIO.input(KS)
    return (state)

#--- Cleanup ---
def clean(*args):
    print("\nProgram ending! Cleaning up...\n")
    for element in HEAT:
        GPIO.output(element, False)
    GPIO.cleanup()
    lcd.close(clear=True)
    print("All clean - Stopping.\n")
    os._exit(0)

for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, clean)

time.sleep(1)

# PID Update
def Update(SetPoint, ProcValue, IMax, IMin, Window, Kp, Ki, Kd):

    L.debug("""Entering PID update with parameters SetPoint:%0.2f,
               ProcValue:%0.2f, IMax:%0.2f, IMin:%0.2f, Window:%d,
               Kp: %0.3f, Ki: %0.3f, Kd: %0.3f
            """ % (SetPoint, ProcValue, IMax, IMin, Window, Kp, Ki, Kd)
    )

    global ITerm, LastProcVal
    Err = SetPoint - ProcValue
    ITerm += (Ki * Err);
    if ITerm > IMax:
        ITerm = IMax
    elif ITerm < IMin:
        ITerm = IMin
    DInput = ProcValue - LastProcVal
    Output = Kp*Err + ITerm - Kd*DInput;
    if Output > IMax:
        Output = IMax
    elif Output < IMin:
        Output = IMin
    LastProcVal = ProcValue

    L.debug("""Exiting PID update with parameters Error:%0.2f,
               ITerm:%0.2f, DInput:%0.2f, Output:%0.2f
            """ % (Err, ITerm, DInput, Output)
    )

    return Output


def Fire(RunID, Seg, TargetTmp1, Rate, HoldMin, Window, Kp, Ki, Kd, cone=False):

    L.info("""Entering Fire function with parameters RunID:%d, Seg:%d,
              TargetTmp:%d, Rate:%d, HoldMin:%d, Window:%d
           """ % (RunID, Seg, TargetTmp1, Rate, HoldMin, Window)
    )
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
    KSTrg = False
    
    while RunState != "Stopped"  and  RunState != "Complete":
        if time.time() >= NextSec:
            Cnt += 1                         # record keeping only
            NextSec = time.time() + Window   # time at end of window
            LastTmp = ReadTmp
            ReadTmp = Sensor0.readTempC()
            ReadITmp = Sensor0.readInternalC()
            if math.isnan(ReadTmp)  or  ReadTmp == 0  or  ReadTmp > 1330:
                # error reading
                ReadTmp = LastTmp

            if RampTrg == 0:
                # if RampTmp has not yet reached TargetTmp increase RampTmp
                RampTmp += StepTmp

            if TmpDif > 0:  # Rising Segment

                #---- kilnsitter trigger ----
                if not kilnsitter() and not KSTrg:
                    # if KS triggered and not been here before
                    KSTrg == True
                    RampTmp = TargetTmp = ReadTmp
                    if ReadTrg == 0:
                        # HoldMin has not been set
                        EndSec = int(time.time()) + HoldMin*60
                        # stop RampTrg and ReadTrg checks
                        ReadTrg = RampTrg = 1
                    RunState = 'KilnSitter/Hold'
                    L.info("Kilnsitter Trigered - End seconds set to %d" % EndSec)

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
                    L.info("Set temp reached - End seconds set to %d" % EndSec)
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
                    L.info("Set temp reached - End seconds set to %d" % EndSec)
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
                Integral = 0.0
                L.info("""First pass of firing loop - TargetTmp:%0.2f,
                          StartTmp:%0.2f,RampTmp:%0.2f, TmpDif:%0.2f,
                          RampMin:%0.2f, Steps:%d, StepTmp:%0.2f,
                          Window:%d, StartSec:%d, EndSec:%d
                       """ % (TargetTmp, StartTmp, RampTmp, TmpDif, RampMin,
                              Steps, StepTmp, Window, StartSec, EndSec)
                )
            # run state through pid
            Output = Update(RampTmp, ReadTmp, 100, 0, Window, Kp, Ki, Kd)
            
            CycleOnSec = Window * Output * 0.01
            if CycleOnSec > Window:
                CycleOnSec = Window

            RemainSec = EndSec - int(time.time()) 
            RemMin, RemSec = divmod(RemainSec, 60)
            RemHr, RemMin = divmod(RemMin, 60)
            RemainTime = "%d:%02d:%02d" % (RemHr, RemMin, RemSec)
            L.debug("""RunID %d, Segment %d (loop %d) - RunState:%s,
                       ReadTmp:%0.2f, RampTmp:%0.2f, TargetTmp:%0.2f,
                       Output:%0.2f, CycleOnSec:%0.2f, RemainTime:%s
                    """ % (RunID, Seg, Cnt, RunState, ReadTmp, RampTmp,
                           TargetTmp, Output, CycleOnSec, RemainTime)
            )
           
            if Output > 0:
                L.debug("==>Relay On")
                for element in HEAT:
                    GPIO.output(element, True)
                time.sleep(CycleOnSec)

            if Output < 100:
                L.debug("==>Relay Off")
                for element in HEAT:
                    GPIO.output(element, False)

            L.debug("Write status information to status file %s:" % StatFile)

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
                + '  "segtime": "' + str(RemainTime) + '"\n'  
                + '}\n'
            )
            sfile.close()

            lcd.writeFire(RunState,RunID,Seg,ReadTmp,TargetTmp,RampTmp,RemainTime)

            L.debug("Writing stats to Firing DB table...")

            sql = """INSERT INTO firing(run_id, segment, dt,
                        set_temp, temp, int_temp, pid_output)
                     VALUES ( ?,?,?,?,?,?,? );
                  """
            p = (RunID, Seg, time.strftime('%Y-%m-%d %H:%M:%S'),
                 RampTmp, ReadTmp, ReadITmp, Output)
            try:
                SQLCur.execute(sql, p)
                SQLConn.commit()
            except:
                SQLConn.rollback()
                L.error("DB Update failed!")

            # Check if profile is still in running state
            sql = "SELECT * FROM profiles WHERE state=? AND run_id=?;"
            p = ('Running', RunID)
            SQLCur.execute(sql, p)
            result = SQLCur.fetchall()
            if len(result) == 0:
                L.warn("Profile no longer in running state - exiting firing")
                SegCompStat = 1 
                RunState = "Stopped"

            if time.time() > EndSec and ReadTrg == 1:
                # hold time is over and reached target
                RunState = "Complete"
    
# --- end Fire() ---

L.info("===START PiLN Firing Daemon===")
L.info("Polling for 'Running' firing profiles...")

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

    L.debug("Write status information to status file %s:" % StatFile)

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
            L.info("Run ID %d is active - starting firing profile" % RunID)

            StTime = time.strftime('%Y-%m-%d %H:%M:%S')
            L.debug("Update profile %d start time to %s" % (RunID, StTime))

            sql = "UPDATE profiles SET start_time=? WHERE run_id=?;"
            p = (StTime, RunID)
            try:
                SQLCur.execute(sql, p)
                SQLConn.commit()
            except:
                SQLConn.rollback()
                L.error("DB Update failed!")

            # Get segments
            L.info("Get segments for run ID %d" % RunID)

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
                    L.debug("Profile stopped - skipping segment %d" % Seg)
                else:
                    L.info("""Run ID %d, segment %d parameters:
                              Target Temp: %0.2f, Rate: %0.2f,
                              Hold Minutes: %d, Window Seconds: %d
                           """ % (RunID, Seg, TargetTmp, Rate, HoldMin, Window)
                    )
                    StTime = time.strftime('%Y-%m-%d %H:%M:%S')
                    L.debug("""Update segments set run id %d,
                               segment %d start time to %s
                            """ % (RunID, Seg, StTime)
                    )

                    #--- mark started segment with datatime ---
                    sql = """UPDATE segments SET start_time=?
                             WHERE run_id=? AND segment=?;
                          """
                    p = (StTime, RunID, Seg)
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                    except:
                        SQLConn.rollback()
                        L.error("DB Update failed!")

                    time.sleep(0.5)

                    #--- fire segment ---
                    Fire(RunID, Seg, TargetTmp, Rate, HoldMin, Window, Kp, Ki, Kd)
                    for element in HEAT:
                        GPIO.output(element, False) ## make sure elements are off

                    EndTime=time.strftime('%Y-%m-%d %H:%M:%S')
                    L.debug("Update run id %d, segment %d end time to %s"
                            % (RunID, Seg, EndTime)
                    )

                    #--- mark segment finished with datetime ---
                    sql = """UPDATE segments SET end_time=?
                            WHERE run_id=? AND segment=?;
                          """
                    p = (EndTime, RunID, Seg)
                    try:
                        SQLCur.execute(sql, p)
                        SQLConn.commit()
                    except:
                        SQLConn.rollback()
                        L.error("DB Update failed!")

                    lcd.clear()
            # --- end firing loop ---

            if SegCompStat == 1:
                L.info("Profile stopped - Not updating profile end time")
            else:
                EndTime = time.strftime('%Y-%m-%d %H:%M:%S')
                L.debug("""Update profile end time to %s
                           and state to %s for run id %d
                        """ % (EndTime, 'Completed', RunID)
                )

                sql = "UPDATE profiles SET end_time=?, state=? WHERE run_id=?;"
                p = (EndTime, 'Completed', RunID)
                try:
                    SQLCur.execute(sql, p)
                    SQLConn.commit()
                except:
                    SQLConn.rollback()
                    L.error("DB Update failed!")

            SegCompStat = 0

            L.info("Polling for 'Running' firing profiles...")
    time.sleep(2)

SQLConn.close()
