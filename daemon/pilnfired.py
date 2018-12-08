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
import Adafruit_MAX31855.MAX31855 as MAX31855
import spidev
from RPLCD import i2c
GPIO.setmode(GPIO.BCM)

# --- RPLCD setup ---
lcd=i2c.CharLCD(
  i2c_expander='PCF8574',
  address=0x27,port=1,
  cols=20,rows=4,dotsize=8,
  charmap='A02',
  auto_linebreaks=True,
  backlight_enabled=True
)
smiley=(0b00000,0b01010,0b01010,0b00000,0b10001,0b10001,0b01110,0b00000)
lcd.create_char(0,smiley)
lcd.create_char(1,[0b01100,0b10010,0b10010,0b01100,0b00000,0b00000,0b00000,0b00000])
lcd.create_char(2,[0b00000,0b10000,0b01000,0b00100,0b00010,0b00001,0b00000,0b00000])
time.sleep(1)
# --- RPLCD setup end ---

SQLDB = '/var/www/db/MyPiLN/PiLN.sqlite3'
AppDir = '/home/pi/git/MyPiLN'

#Status File
StatFile = '/var/www/html/pilnstat.json'

# Set up logging
LogFile = time.strftime( AppDir + '/log/pilnfired.log' )
L.basicConfig(
  filename=LogFile,
#comment to disable:
#  level=L.DEBUG,
  format='%(asctime)s %(message)s'
)

# Global Variables
#LastErr  = 0.0
#Integral = 0.0
ITerm = 0.0
LastProcVal = 0.0
SegCompStat = 0
LastTmp  = 0.0
wheel = '-'

# MAX31855
SPI_PORT = 1
#SPI_DEVICE0 = 0  #18
#Sensor0 = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE0))
#SPI_DEVICE1 = 1  #17
#Sensor0 = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE1))
SPI_DEVICE2 = 2  #16
Sensor0 = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE2))

# Relay
HEAT = 22
GPIO.setup (HEAT,GPIO.OUT)
GPIO.output(HEAT,GPIO.LOW)

def clean(*args):
  print ("\nProgram ending! Cleaning up...\n")
  GPIO.output(HEAT,False)
  GPIO.cleanup()
  lcd.close(clear=True)
  print ("All clean - Stopping.\n")
  os._exit(0)

for sig in (SIGABRT,SIGINT,SIGTERM):
    signal(sig, clean)

# Celsius to Fahrenheit
def CtoF(c):
  return c * 9.0 / 5.0 + 32.0

  
# PID Update
def Update ( SetPoint, ProcValue, IMax, IMin, Window, Kp, Ki, Kd ):

  L.debug( "Entering PID update with parameters SetPoint:%0.2f, ProcValue:%0.2f, IMax:%0.2f, IMin:%0.2f," %
    ( SetPoint, ProcValue, IMax, IMin ))
  L.debug( "  Window:%d, Kp: %0.3f, Ki: %0.3f, Kd: %0.3f" %
    ( Window, Kp, Ki, Kd ))

  global ITerm, LastProcVal

  Err = SetPoint - ProcValue
  ITerm+= (Ki * Err);

  if ITerm > IMax:
    ITerm = IMax
  elif ITerm < IMin:
    ITerm = IMin

  DInput = ProcValue - LastProcVal

  #Compute PID Output
  Output = Kp * Err + ITerm - Kd * DInput;
  if Output > IMax:
    Output = IMax
  elif Output < IMin:
    Output = IMin

  #Remember for next time
  LastProcVal = ProcValue


  L.debug(
    "Exiting PID update with parameters Error:%0.2f, ITerm:%0.2f, DInput:%0.2f, Output:%0.2f" %
    ( Err, ITerm, DInput, Output )
  )

  return Output



#  global LastErr, Integral
#
#  Err      = SetPoint - ProcValue
#
#  Pterm    = Kp * Err
#
#  Dterm    = Kd * ( Err - LastErr )
#  LastErr  = Err
#
#  Integral+= Err
#  if Integral > IMax:
#    Integral = IMax
#  elif Integral < IMin:
#    Integral = IMin
#  Iterm = Ki * Integral
#
#  Output = Pterm + Iterm + Dterm
#
#  L.debug(
#    "Exiting PID update with parameters Error:%0.2f, Integral:%0.2f, Pterm:%0.2f, Iterm:%0.2f, Dterm:%0.2f, Output:%0.2f" %
#    ( Err, Integral, Pterm, Iterm, Dterm, Output )
#  )
#
#  if Output > 100:
#    Output = 100
#  elif Output < 0:
#    Output = 0
#  if Output < 0:
#    Output = 0
#
#  return Output


# Loop to run each segment of the firing profile
def Fire(RunID,Seg,TargetTmp,Rate,HoldMin,Window,Kp,Ki,Kd):

  L.info( "Entering Fire function with parameters RunID:%d, Seg:%d, TargetTmp:%d, Rate:%d," % ( RunID, Seg, TargetTmp, Rate ))
  L.info( "  HoldMin:%d, Window:%d" % ( HoldMin, Window ))

  global SegCompStat
  global wheel

  HoldSec  = HoldMin * 60
  RampMin  = 0.0
  RampTmp  = 0.0
  ReadTmp  = 0.0
  LastTmp  = 0.0
  StartTmp = 0.0
  TmpDif   = 0.0
  Steps    = 0.0
  StepTmp  = 0.0
  StartSec = 0.0
  EndSec   = 0.0
  NextSec  = 0.0
  RunState = "Ramp"
  Cnt      = 0
  RampTrg  = 0
  ReadTrg  = 0
  
  while RunState != "Stopped" and RunState != "Complete":

    if time.time() >= NextSec:
      Cnt += 1
      NextSec = time.time() + Window

      # Get temp
      LastTmp   = ReadTmp
      ReadCTmp  = Sensor0.readTempC()
      ReadTmp   = CtoF(ReadCTmp)
      ReadCITmp = Sensor0.readInternalC()
      ReadITmp  = CtoF(ReadCITmp)
      #if math.isnan(ReadTmp) or ( abs( ReadTmp - LastTmp ) > ( 2 * Window ) ) or ReadTmp == 0 or ReadTmp > 2400:
      if math.isnan(ReadCTmp) or ReadCTmp == 0 or ReadCTmp > 1315:
        ReadTmp = LastTmp

      if RampTrg == 0:
        RampTmp += StepTmp

      if TmpDif > 0:

        # Ramp temp reached target
        if RampTmp >= TargetTmp and RampTrg == 0:
          RampTmp = TargetTmp
          RampTrg = 1
          if ReadTrg == 1:
            RunState = "Ramp complete/target temp reached"
          else:
            RunState = "Ramp complete"

        # Read temp reached target
        if ( ( TargetTmp - ReadTmp <= TargetTmp * 0.006 ) or ( ReadTmp >= TargetTmp ) ) and ReadTrg == 0:
          ReadTrg = 1
          EndSec = int(time.time()) + ( HoldMin * 60 )
          L.info( "Set temp reached - End seconds set to %d" % EndSec )
          if RampTrg == 1:
            RunState = "Ramp complete/target temp reached"
          else:
            RunState = "Target temp reached"

      elif TmpDif < 0:

        # Ramp temp reached target
        if RampTmp <= TargetTmp and RampTrg == 0:
          RampTmp = TargetTmp
          RampTrg = 1
          if ReadTrg == 1:
            RunState = "Ramp complete/target temp reached"
          else:
            RunState = "Ramp complete"

        # Read temp reached target
        if ( ( ReadTmp - TargetTmp <= TargetTmp * 0.006 ) or ( ReadTmp <= TargetTmp ) ) and ReadTrg == 0:
          ReadTrg = 1
          EndSec = int(time.time()) + ( HoldMin * 60 )
          L.info( "Set temp reached - End seconds set to %d" % EndSec )
          if RampTrg == 1:
            RunState = "Ramp complete/target temp reached"
          else:
            RunState = "Target temp reached"

      if StartTmp == 0:
        StartTmp = ReadTmp
        StartSec = int(time.time())
        NextSec  = StartSec + Window
        TmpDif   = TargetTmp - StartTmp
        RampMin  = ( abs (TmpDif) / Rate ) * 60
        Steps    = ( RampMin * 60 ) / Window
        StepTmp  = TmpDif / Steps
        EndSec   = StartSec + ( RampMin * 60 ) + ( HoldMin * 60 )
        RampTmp = StartTmp + StepTmp
        if ( TmpDif > 0 and RampTmp > TargetTmp ) or ( TmpDif < 0 and RampTmp < TargetTmp ):
          RampTmp = TargetTmp
        LastErr  = 0.0
        Integral = 0.0

        L.info( "First pass of firing loop - TargetTmp:%0.2f, StartTmp:%0.2f, RampTmp:%0.2f, TmpDif:%0.2f," %
          ( TargetTmp, StartTmp, RampTmp, TmpDif ))
        L.info( "  RampMin:%0.2f, Steps:%d, StepTmp:%0.2f, Window:%d, StartSec:%d, EndSec:%d" %
          ( RampMin, Steps, StepTmp, Window, StartSec, EndSec ) )
    
      Output = Update(RampTmp,ReadTmp,100,0,Window,Kp,Ki,Kd)

      CycleOnSec  = Window * ( Output * 0.01 )
      if CycleOnSec > Window:
        CycleOnSec = Window

      RemainSec = EndSec - int ( time.time() ) 
      RemMin, RemSec = divmod(RemainSec, 60)
      RemHr, RemMin  = divmod(RemMin, 60)
      RemainTime = "%d:%02d:%02d" % (RemHr, RemMin, RemSec)
      L.debug( "RunID %d, Segment %d (loop %d) - RunState:%s," % ( RunID, Seg, Cnt, RunState ))
      L.debug( "  ReadTmp:%0.2f, RampTmp:%0.2f, TargetTmp:%0.2f, Output:%0.2f, CycleOnSec:%0.2f, RemainTime:%s" %
        ( ReadTmp, RampTmp, TargetTmp, Output, CycleOnSec, RemainTime )
      )

      if Output > 0:
        L.debug("==>Relay On")
        GPIO.output(HEAT,True)
        time.sleep(CycleOnSec)

      if Output < 100:
        L.debug("==>Relay Off")
        GPIO.output(HEAT,False)

      # Write status to file for reporting on web page
      L.debug( "Write status information to status file %s:" % StatFile )
      sfile = open(StatFile,"w+")
      sfile.write('{\n' +
        '  "proc_update_utime": "' + str(int(time.time())) + '",\n' +
        '  "readtemp": "'          + str(int(ReadTmp))     + '",\n' +
        '  "run_profile": "'       + str(RunID)            + '",\n' +
        '  "run_segment": "'       + str(Seg)              + '",\n' +
        '  "ramptemp": "'          + str(int(RampTmp))     + '",\n' +
        '  "targettemp": "'        + str(int(TargetTmp))   + '",\n' +
        '  "status": "'            + str(RunState)         + '",\n' +
        '  "segtime": "'           + str(RemainTime)       + '"\n'  +
        '}\n'
      )
      sfile.close()

      if wheel == '-':
        wheel = '\x02'
      elif wheel == '\x02':
        wheel = '|'
      elif wheel == '|':
        wheel = '/'
      elif wheel == '/':
       wheel = '\x00'
      else:
        wheel = '-'

      #------ display ------
      lcd.cursor_pos = (0, 0)
      lcd.write_string(u'Sta:' +str(RunState)+'       ')
      lcd.cursor_pos = (1, 0)
      lcd.write_string(u'Pro:' +str(RunID)+'       ')
      lcd.cursor_pos = (1, 10)
      lcd.write_string(u'Seg:' +str(Seg)+' '+wheel+'   ')
      lcd.cursor_pos = (2, 0)
      lcd.write_string(u'Tmp:' +str(int(ReadTmp))+'\x01    ')
      lcd.cursor_pos = (2, 10)
      lcd.write_string(u'Trg:' +str(int(TargetTmp))+'\x01    ')
      lcd.cursor_pos = (3, 0)
      lcd.write_string(u'Ram:' +str(int(RampTmp))+'\x01     ')
      lcd.cursor_pos = (3, 10)
      lcd.write_string('T:'   +RemainTime)
      #------ display ------

      L.debug("Writing stats to Firing DB table...")
      sql = "INSERT INTO firing (run_id, segment, dt, set_temp, temp, int_temp, pid_output) VALUES ( ?,?,?,?,?,?,? );"
      p = ( RunID, Seg, time.strftime('%Y-%m-%d %H:%M:%S'), RampTmp, ReadTmp, ReadITmp, Output )
      try:
        SQLCur.execute( sql, p )
        SQLConn.commit()
      except:
        SQLConn.rollback()
        L.error("DB Update failed!")


      # Check if profile is still in running state
      sql = 'SELECT * FROM profiles WHERE state=? AND run_id=?;'
      p = ( 'Running', RunID )
      SQLCur.execute( sql, p )
      result = SQLCur.fetchall()
      if len(result) == 0:
        L.warn("Profile no longer in running state - exiting firing")
        SegCompStat = 1 
        RunState = "Stopped"
  
      if time.time() > EndSec and ReadTrg == 1:
        RunState = "Complete"
  
#      L.debug(
#            "RunState:%s, TargetTmp:%0.2f, StartTmp:%0.2f, RampTmp:%0.2f, TmpDif:%0.2f, RampMin:%0.2f, Steps:%d, StepTmp:%0.2f, Window:%d, StartSec:%d, EndSec:%d" %
#            ( RunState, TargetTmp, StartTmp, RampTmp, TmpDif, RampMin, Steps, StepTmp, Window, StartSec, EndSec ) 
#          )



L.info("===START PiLN Firing Daemon===")
L.info("Polling for 'Running' firing profiles...")

lcd.clear()
while 1:
  # Get temp
  ReadCTmp  = Sensor0.readTempC()
  ReadTmp   = CtoF(ReadCTmp)
  ReadCITmp = Sensor0.readInternalC()
  ReadITmp  = CtoF(ReadCITmp)
  if math.isnan(ReadTmp):
    ReadTmp = LastTmp

  # Write statu to file for reporting on web page
  L.debug( "Write status information to status file %s:" % StatFile )
  sfile = open(StatFile,"w+")
  sfile.write('{\n' +
    '  "proc_update_utime": "' + str(int(time.time())) + '",\n' +
    '  "readtemp": "'          + str(int(ReadTmp))     + '",\n' +
    '  "run_profile": "none",\n' +
    '  "run_segment": "n/a",\n' +
    '  "ramptemp": "n/a",\n' +
    '  "status": "n/a",\n' +
    '  "targettemp": "n/a"\n' +
    '}\n'
  )
  sfile.close()

  if wheel == '-':
    wheel = '\x02'
  elif wheel == '\x02':
    wheel = '|'
  elif wheel == '|':
    wheel = '/'
  elif wheel == '/':
    wheel = '\x00'
  else:
    wheel = '-'

  #------ display ------
  lcd.cursor_pos = (0,0)
  lcd.write_string( 'IDLE: '+wheel+'              ')
  lcd.cursor_pos = (2,0)
  lcd.write_string('Tmp: '+str(int(ReadTmp))+'\x01          ')
  #------ end display ------

  # --- Check for 'Running' firing profile ---
  SQLConn = sqlite3.connect(SQLDB)
  SQLConn.row_factory = sqlite3.Row
  SQLCur  = SQLConn.cursor()
  sql = 'SELECT * FROM profiles WHERE state=?;'
  p = ( 'Running', )
  SQLCur.execute( sql, p )
  Data = SQLCur.fetchall()
  #--- if Running prfile found set up to fire --
  if len(Data) > 0:
    RunID = Data[0]['run_id']
    Kp = float(Data[0]['p_param'])
    Ki = float(Data[0]['i_param'])
    Kd = float(Data[0]['d_param'])
    L.info("Run ID %d is active - starting firing profile" % RunID)

    StTime=time.strftime('%Y-%m-%d %H:%M:%S')
    L.debug('Update profile %d start time to %s' % ( RunID, StTime ) )
    sql = 'UPDATE profiles SET start_time=? WHERE run_id=?;'
    p = ( StTime, RunID )
    try:
      SQLCur.execute( sql, p )
      SQLConn.commit()
    except:
      SQLConn.rollback()
      L.error("DB Update failed!")

    # Get segments
    L.info("Get segments for run ID %d" % RunID)
    sql = 'SELECT * FROM segments WHERE run_id=?;'
    p = ( RunID, )
    SQLCur.execute( sql, p )
    ProfSegs = SQLCur.fetchall()

    # --- begin firing loop ---
    for Row in ProfSegs:
      RunID     = Row['run_id']
      Seg       = Row['segment']
      TargetTmp = Row['set_temp']
      Rate      = Row['rate']
      HoldMin   = Row['hold_min']
      Window    = Row['int_sec']

      if SegCompStat == 1:
        L.debug("Profile stopped - skipping segment %d" % Seg)
      else:
        L.info( "Run ID %d, segment %d parameters: Target Temp: %0.2f, Rate: %0.2f," % ( RunID, Seg, TargetTmp, Rate ))
        L.info( "  Hold Minutes: %d, Window Seconds: %d" % ( HoldMin, Window ))

        #--- mark started segment with datatime ---
        StTime=time.strftime('%Y-%m-%d %H:%M:%S')
        L.debug("Update segments set run id %d, segment %d start time to %s" % ( RunID, Seg, StTime ) )
        sql = "UPDATE segments SET start_time=? WHERE run_id=? AND segment=?;"
        p = ( StTime, RunID, Seg )
        try:
          SQLCur.execute( sql, p )
          SQLConn.commit()
        except:
          SQLConn.rollback()
          L.error("DB Update failed!")
        time.sleep(0.5)

        #--- fire segment ---
        Fire(RunID,Seg,TargetTmp,Rate,HoldMin,Window,Kp,Ki,Kd)
        GPIO.output(HEAT,False) ## Turn off GPIO pin
        #--- end fire segment ---
        #--- mark segment finished with datetime ---
        EndTime=time.strftime('%Y-%m-%d %H:%M:%S')
        L.debug("Update run id %d, segment %d end time to %s" % ( RunID, Seg, EndTime ) )
        sql = 'UPDATE segments SET end_time=? WHERE run_id=? AND segment=?;'
        p = ( EndTime, RunID, Seg )
        try:
          SQLCur.execute( sql, p )
          SQLConn.commit()
        except:
          SQLConn.rollback()
          L.error("DB Update failed!")
    # --- end firing loop ---

    if SegCompStat == 1:
        L.info("Profile stopped - Not updating profile end time")
    else:
      EndTime=time.strftime('%Y-%m-%d %H:%M:%S')
      L.debug("Update profile end time to %s and state to %s for run id %d" % ( EndTime, 'Completed', RunID ) )
      sql = 'UPDATE profiles SET end_time=?, state=? WHERE run_id=?;'
      p = ( EndTime, 'Completed', RunID )
      try:
        SQLCur.execute( sql, p )
        SQLConn.commit()
      except:
        SQLConn.rollback()
        L.error("DB Update failed!")

    SegCompStat = 0

    L.info("Polling for 'Running' firing profiles...")

  SQLConn.close()
  time.sleep(2)
