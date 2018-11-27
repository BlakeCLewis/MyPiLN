
#Web-based Raspberry Pi Kiln Control Application:
- Forked of pvarney/PiLN
- Switched out LCD for pioled
- Switched out MySQL for sqlite3


WARNING! Electricity and heat are dangerous! Please be careful and seek professional help if you are not experienced dealing with high voltage and heat. Use this code/information at your own risk.

Future improvements:
- overheat shutdown
- Kiln Sitter(KS) as a sensor, use an Orton KS bar in KS and wire KS to GPIO;
- performance watchdog, shutdown when a minimum rate cannot be maintained;
- abstract thermocouple code to ease changing thermocouple chip (MAX31856 has 50/60hz filter and a correction table)(MAX31850 onewire);
- abstract display code to ease changing display (LCD, pioled);
- zone control, thermocouple/section, conrol sections independently);
- inductive current sensors: monitor electric usage to calculate cost of firing, also as an element fault indicator;
- record ambient temp in the with the firing profile:
- congifuration file to set up all the paths, pins and choose hardware;
- crash/loss of power recovery;

Hardware:
- Test rig - $10 Raspberry Pi zero w, $3 SSR, $2 k-type thermocouple, $17.50 adafruit.com MAX31855, hair blow dryer and an amazon cardboard box;
- I use a pi with $7 thermocouple (below) on the manual kiln during bisque firing to monitor temps and rates;
- MAX31855 thermocouple module
    + $17.50, Adafruit (https://www.adafruit.com/product/269);
- High temperature (2372 F) type K thermocouple
    + $7/each, 3 pack, (https://www.aliexpress.com/item/High-Temperature-K-Type-Thermocouple-Sensor-for-Ceramic-Kiln-Furnace-1300-Temperature/32832729663.html?spm=a2g0s.9042311.0.0.3dd14c4dIQr1ud);
- 6 pack of thermocouples
    + bought for the thermocouple wire, 3 meters each - (https://www.amazon.com/gp/product/B00OLNZ6XI/ref=oh_aui_detailpage_o06_s02?ie=UTF8&psc=1);
- 3 LEDs for 'relay on' indicator and resistors for LEDs;
- 1 - uln2003a darlington transitor array to switch 12V coil on the relays
     + untested, switch 12V on relay, using GPIO
     + $1/each on amazon (also used for stepper motors), can switch 7 channels;
- 3 - Deltrol  20852-81 relays
     + This is equivelent to relay Skutt uses to switch sections/zones
     + $17.50 each and about that much for shipping (https://www.galco.com/buy/Deltrol-Controls/20852-81);
- 12V power supply
     + converts 120vac to 12vdc
     + $20 (https://www.amazon.com/gp/product/B00DECZ7WC/ref=oh_aui_detailpage_o01_s01?ie=UTF8&psc=1);
- 5V buck converter
     + converts 12v to 5v USB out for Pi power
     + $7 (https://www.amazon.com/gp/product/B071FJVRCT/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1);
- LCD screen and driver board, (most any hdmi monitor will work) ~$30;
- Terminal blocks to distribute L1, L2, N and GND
  	 + Ground, $6 (https://www.amazon.com/gp/product/B000K2MA9M/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1)
  	 + L1,L2,Neutral, 3 @ $7/each, (https://www.amazon.com/gp/product/B000OTJ89Q/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1);
- Wired 2 lengths of  #10 awg to each section, all wires on the Kiln are Hi Temp Appliance wire;
- Crimp terminals, #10 awg, Hi Temp Appliance
     +~$.16/each, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1);
     + uses the same crimper used on the elements $16, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1);
     + the crimpers take muscle
- Crimp lugs #6 AWG copper
     + $9 for 10 (https://www.amazon.com/gp/product/B073Y8Q9JQ/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
-  Big crimper
     + $25, (https://www.amazon.com/gp/product/B07D7Q54N2/ref=oh_aui_detailpage_o01_s03?ie=UTF8&psc=1)
     + I crimp 2 times, first time with correct size, second time reduced one notch(correct size is loose);
- Din rail mounts
     + $17/5 pair(https://www.amazon.com/gp/product/B01H1H86UU/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1);
- Din rails
     + $5/each (https://www.amazon.com/gp/product/B01FT485S0/ref=oh_aui_detailpage_o02_s01?ie=UTF8&psc=1);
- 14 THHN stranded, hardware store, to power 12V supply, white,red,greem 2' each
- heat shrink, Harbor Frieght
- #10 32tpi tap and #21 jobber drill bit
     + I have lots of 10-32 screws from rack mount hardware extras(data center)
     + tap a hole screw in a screw and use the $10 Harbor Frieght angle grinder to flush it up on the back of the box.

Thermocouple tip: One side of both the thermocouple and special wire is magnetic (red side), Test with magnet to wire correctly. 

Stuff to get it to work:

- Pin-Out:

		MAX31855+:		3.3v,    Pin 17
		MAX31855-:		GROUND,  Pin 20
		MAX31855 CLK:		GPIO 25, Pin 22
		MAX31855 CS:		GPIO 24, Pin 18
		MAX31855 DO:		GPIO 18, Pin 12
		unl2003a 1: 		GPIO 23, Pin 16
		unl2003a 8:		GROUND,  Pin 25
		PiOLED: 		3.3v,    Pin 1
		PiOLED: 		5v,      Pin 2
		PiOLED: 		GPIO 2,  Pin 3
		PiOLED: 		5v,      Pin 4
		PiOLED: 		GPIO 3,  Pin 5
		PiOLED: 		GND,     Pin 6

- Install PiLN files in /home and create log directory:

		sudo adduser PiLN
		su - PiLN
		git clone git@github.com:BlakeCLewis/MyPiLN.git .
		mkdir ./log
		
- Install sqlite3:

		sudo apt-get install sqlite3
		
- Set up directories/link for web page:

		sudo mkdir /var/www/html/images
		sudo mkdir /var/www/html/style
		sudo ln -s /home/PiLN/images/hdrback.png /var/www/html/images/hdrback.png
		sudo ln -s /home/PiLN/images/piln.png    /var/www/html/images/piln.png
		sudo ln -s /home/PiLN/style/style.css    /var/www/html/style/style.css
	
- Add the following ScriptAlias and Directory parameters under "IfDefine ENABLE_USR_LIB_CGI_BIN" in /etc/apache2/conf-available/serve-cgi-bin.conf:
	
		ScriptAlias /pilnapp/ /home/PiLN/app/
		  <Directory "/home/PiLN/app/">
		    AllowOverride None
		    Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
		    Require all granted
		  </Directory>

- Create links to enable cgi modules:
	
		cd /etc/apache2/mods-enabled
		sudo ln -s ../mods-available/cgid.conf cgid.conf
		sudo ln -s ../mods-available/cgid.load cgid.load
		sudo ln -s ../mods-available/cgi.load cgi.load

- Restart Apache:
	
		sudo systemctl daemon-reload
		sudo systemctl restart apache2
		
- Install required Python packages:

		sudo apt-get update
		sudo apt-get install build-essential python-dev python-smbus

- Install pioled requirements:

		These git clones can be done by a user other than PiLN

		git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
		cd ./Adafruit_Python_GPIO/
		sudo python3 setup.py install

		git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
		cd ./Adafruit_Python_SSD1306/
		sudo python3 setup.py install

		sudo raspi-config #enable interfaces ic2 & spi
		lsmod | grep spi
		
- Install Adafruit MAX31855 Module:

		cd ~
		git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
		cd Adafruit_Python_MAX31855
		sudo python setup.py install		
		
- Required Python modules (separate installs were not required for these using the latest Raspian build as of July 2017): cgi, jinja2, sys, re, datetime, json, time, logging, RPi.GPIO.

- create the sqlite3 database:

		sudo mkdir -p /var/www/db/PiLN/
		sudo chown -R PiLN:PiLN /var/www/db
		sqlite3 /var/www/db/PiLN/PiLN.sqlite3
		sqlite> .read /home/PiLN/PiLN.sql;

- (I do not use this yet) To enable automatic startup of the daemon (Had to do the copy/enable/delete/link in order to get systemctl enable to work):

		cp /home/PiLN/daemon/pilnfired.service /etc/systemd/system/
		sudo systemctl daemon-reload
		sudo systemctl enable pilnfired
		sudo rm /etc/systemd/system/pilnfired.service
		sudo ln -s /home/PiLN/daemon/pilnfired.service /etc/systemd/system/pilnfired.service
		sudo systemctl daemon-reload
		sudo systemctl start pilnfired
		sudo systemctl status pilnfired
		
- Tuning: 

        Patrick's suggestion
		Proportional:	6.00
		Integral:	0.04
		Derivative:	0.00
        Time internal: 10 seconds

	    I use 'time interval = 4 seconds' for the blow dryer test rig.

Using the Web App:
- On the same network that the RPi is connected to, go to http://<RPi_IPAddress>/pilnapp/home.cgi
