#!/usr/bin/python3

"""
#requires: display.py

#buy parts:
https://www.amazon.com/gp/product/B01GPUMP9C/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1
https://www.adafruit.com/product/3263
https://www.amazon.com/Temperature-Thermocouple-Ceramic-connector-CR-06/dp/B0713X6XG3/ref=sr_1_25?keywords=k-type&qid=1551683054&s=gateway&sr=8-25


#wiring
  RPLCD VCC:	5V
  RPLCD GND:	GND
  RPLCD SDA:	GPIO 2
  RPLCD SCL:	GPIO 3

  MAX31856 3vo:	3.3v
  MAX31856 GND:	GND
  MAX31856 SDO:	GPIO 9
  MAX31856 SDI:	GPIO 10
  MAX31856 CS:	GPIO 8
  MAX31856 SCK:	GPIO 11

#configure pi for lcd(ic2) and max31856(spi)
sudo raspi-config
  #enable interfaces ic2 & spi

#install sqlite3, pip3 and other python3 stuffs
sudo apt-get update
sudo apt-get install sqlite3
sudo apt-get install build-essential python3-pip python3-dev python3-smbus

#libraries from github
cd ~
git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
  cd Adafruit_Python_GPIO
  sudo python3 setup.py install
  cd
git clone git@github.com:johnrbnsn/Adafruit_Python_MAX31856.git
  cd Adafruit_Python_MAX31856
  sudo python3 setup.py install

#install library for LCD using python installer 'pip3'
sudo pip3 install RPLCD

#create schema
sqlite3 /home/pi/kilnlog.sqlite3
  CREATE TABLE firelog(RunID number, datime datetime, t number); 

#make this file executable:
  chmod +x logger.py

startup logging
./logger.py -i <intger Run_ID> -s <interval in seconds>

#access data
sqlite3 /home/pi/kilnlog.sqlite3
  select * from firelog where runid=32 order by datime asc;

"""
import sys, getopt
from signal import *
import os
import time
import sqlite3
from Adafruit_GPIO import SPI
from Adafruit_MAX31856 import MAX31856
from display import display

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:s:",["runid=","seconds="])
    except getopt.GetoptError:
        print('logger.py -i <RunID> -s <seconds>')
        sys.exit(2)
    for opt, arg in opts:
       if opt == '-h' or (opt != '-i' and opt != '-s'):
          print ('logger.py -i <RunID> -s <seconds>')
          sys.exit()
       elif opt in ("-i", "--RunID="):
          RunID = arg
          print ('RunID is ', RunID)
       elif opt in ("-s", "--seconds="):
          interval_seconds = int(arg)
          print ('interval_seconds is ', interval_seconds)

    lcd = display()
    lcd.clear()

    SQLDB = '/home/mypiln/kilnlog.sqlite3'
    SQLConn = sqlite3.connect(SQLDB)
    SQLConn.row_factory = sqlite3.Row
    SQLCur = SQLConn.cursor()

    sql="INSERT INTO firelog(RunID, datime, t)VALUES(?,?,?);"

    SPI_PORT = 0
    SPI_DEVICE = 0
    sensor = MAX31856(hardware_spi=SPI.SpiDev(SPI_PORT,SPI_DEVICE))
    t_now = sensor.read_temp_c()
    print('TC: {0:0.3F}*C'.format(t_now))
    temps=[t_now, t_now, t_now]
    lastTime = time.time() - interval_seconds
    while True:
        datime = time.time()
        if lastTime + interval_seconds <= datime:
            t_now = sensor.read_temp_c()
            if temps.insert(0, t_now):
                temps.pop()
            p = (RunID, time.strftime('%Y-%m-%d %H:%M:%S'), t_now)
            lcd.writeLog(RunID, time.strftime('%H:%M:%S'), temps[0], temps[1], temps[2])
            print('TC: {0:0.3F}*C'.format(t_now))
            try:
                SQLCur.execute(sql, p)
                SQLConn.commit()
            except:
                SQLConn.rollback()
                print("DB Update failed!")
            lastTime=datime;
            time.sleep(interval_seconds-1)

if __name__ == "__main__":
   main(sys.argv[1:])
