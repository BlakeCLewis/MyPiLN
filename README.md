# CLONE of pvarney/PiLN
branch blake_1 is my working branch converting to sqlite and pioled



Web-based Raspberry Pi Kiln Control Application

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
- Test rig - Raspberry Pi zero w, SSR, $2 k-type thermocouple, adafruit MAX31855, hair blow dryer and a cardboard box;
- I use a pi with a $7 thermocouple on the manual kiln during bisque firing to monitor temps and rates;
- MAX31855 thermocouple module from Adafruit (https://www.adafruit.com/product/269);
- High temperature (2372 F) type K thermocouple ($7) (https://www.aliexpress.com/item/High-Temperature-K-Type-Thermocouple-Sensor-for-Ceramic-Kiln-Furnace-1300-Temperature/32832729663.html?spm=a2g0s.9042311.0.0.3dd14c4dIQr1ud);
- 6 pack of thermocouples for the thermocouple wire 3 meters each - (https://www.amazon.com/gp/product/B00OLNZ6XI/ref=oh_aui_detailpage_o06_s02?ie=UTF8&psc=1);
- 3 LEDs for 'relay on' indicator and resistors for LEDs;
- 1 - unl2003a darlington transitor array to switch 12V coil on the relays;
- 3 - Deltrol  20852-81 relays $17.50 each and about that much for shipping (https://www.galco.com/buy/Deltrol-Controls/20852-81) (This is equivelent to relay Skutt uses to switch sections/zones);
- 12V power supply (converts 120vac to 12vdc) (https://www.amazon.com/gp/product/B00DECZ7WC/ref=oh_aui_detailpage_o01_s01?ie=UTF8&psc=1) $20
     + 5V buck converter to power PI (reduces 12v to 5v) $4
     + LCD screen and driver board (most any hdmi monitor will work) ~$30;
- Terminal blocks to distribute L1, L2, N and GND
  	 + Ground: 1 - (https://www.amazon.com/gp/product/B000K2MA9M/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1) $6
  	 + L1,L2,Neutral: 3 - (https://www.amazon.com/gp/product/B000OTJ89Q/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1) $7/each;
- Wired 2 #10 awg to each section, all wires on the Kiln are Hi Temp Appliance wire;
- Crimp terminals are Hi Temp Appliance, uses the same crimper used on the elements (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1), ~50 cent/each, The crimpers take muscle;
- Grimp lugs #6 AWG copper (SELTERM 10 Pack 6 Gauge 6 AWG #10 Stud UL Heavy Duty Copper Crimp Lugs Welding Cable Bare Copper Eyelet Lug) 10@$9;
- Din rail mounts (https://www.amazon.com/gp/product/B01H1H86UU/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1) $17/5 pair;
- Din rails (https://www.amazon.com/gp/product/B01FT485S0/ref=oh_aui_detailpage_o02_s01?ie=UTF8&psc=1) $5/each;
- 14 THHN stranded, hardware store, to power 12V supply, white,red,greem 2' each
  
Thermocouple tip: One side of both the thermocouple and special wire is magnetic (red side), Test with magnet to wire correctly. 

Install:

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
		git clone https://github.com/pvarney/PiLN .
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

- To enable automatic startup of the daemon (Had to do the copy/enable/delete/link in order to get systemctl enable to work):

		cp /home/PiLN/daemon/pilnfired.service /etc/systemd/system/
		sudo systemctl daemon-reload
		sudo systemctl enable pilnfired
		sudo rm /etc/systemd/system/pilnfired.service
		sudo ln -s /home/PiLN/daemon/pilnfired.service /etc/systemd/system/pilnfired.service
		sudo systemctl daemon-reload
		sudo systemctl start pilnfired
		sudo systemctl status pilnfired
		
- Tuning: I spent a while adjusting the PID parameters to get the best results and am still tuning. Your tuning parameters will depend on your specific application, but I used the following which might be a good starting point:

		Proportional:	6.00
		Integral:	0.04
		Derivative:	0.00
	I also had good results setting the interval seconds to 10, which is the default.

Using the Web App:
- On the same network that the RPi is connected to, go to http://<RPi_IPAddress>/pilnapp/home.cgi
