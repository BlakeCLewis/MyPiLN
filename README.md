WARNING! Electricity and heat are dangerous! Please be careful and seek professional help if you are not experienced dealing with high voltage and heat. Use this code/information at your own risk.

Web-based Raspberry Pi Kiln Control Application:
- fork of pvarney/PiLN
- switched out LCD for pioled, then again for RPLCD, but with i2c interface(2 GPIO pins)
	+ i2c is slow, blanking to refresh is anoying, so display class writes without blanking
- switched out MySQL for sqlite3(low resource consumption)
- achieved my goal to run on Rasberry Pi Zero W: 
	+ sqlite3 instead of MySQL
	+ lighttpd instead of apache2 (apache memory was 1/2 pi zero memory, lighttpd does not even show up in top)
	+ 'startx chromium-browser --start-maximized' (chrome in X with no window manager)
	+ or 'startx konqueror', then shft-ctrl-F to go full screen
- kiln sitter(KS) as a sensor
	+ KS functions as 'ARMED', can not start firing without kilnsitter being armed
	+ mode 1: set top temp lower than KS cone, thermocouple temp is shutoff trigger, KS is safety
	+ mode 2: set top temp higher than KS cone, KS is shutoff trigger, thermocouple is safety
- display class:
	+ remove display code from main script
	+ easier to change display hardware

Future improvements:
- wrap pioled into display class
- thermocouple class:
	+ ease switching thermocouple chip,
	+ MAX31855 current harware,
	+ MAX31856 has 50/60hz filter and a correction table and can do multiple types including S, minimal change
	+ MAX31850 w/onewire interface, enables multiple thermocouples on one GPIO;
- performance watchdog:
	+ shutdown when a minimum rate cannot be maintained,
	+ notify with options(continue, abort firing, abort segment);
- inductive current sensors: monitor electric usage to calculate cost of firing, also as an element fault indicator;
- zone control: thermocouple/section, conrol sections independently;
- record ambient temp with firing data:
- crash/loss of power recovery:
	+ PI comes up, KS is armed & profile is 'Running' then consider unfinished segment
	+ compare last timestamp of 'Running' firing to current time
	+ compare temp at the timestamp to current temp
	+ notify (email)

Hardware:
- test rig1 - $10 Raspberry Pi zero w, $3 SSR, $2 k-type thermocouple, $17.50 adafruit.com MAX31855, hair blow dryer and an Amazon A6 cardboard box;
- 20x4 LCD w/ i2c backpack
	+ $13, (https://www.amazon.com/gp/product/B01GPUMP9C/ref=oh_aui_detailpage_o01_s00?ie=UTF8&psc=1) uses RPLCD library
- MAX31855 thermocouple module
	+ $17.50, Adafruit (https://www.adafruit.com/product/269);
- High temperature (2372 F) type K thermocouple
	+ $7/each, 3 pack, (https://www.aliexpress.com/item/High-Temperature-K-Type-Thermocouple-Sensor-for-Ceramic-Kiln-Furnace-1300-Temperature/32832729663.html?spm=a2g0s.9042311.0.0.3dd14c4dIQr1ud);
- 6 pack of thermocouples
	+ bought for testing and the thermocouple wire, 3 meters each - (https://www.amazon.com/gp/product/B00OLNZ6XI/ref=oh_aui_detailpage_o06_s02?ie=UTF8&psc=1);
- 1 - uln2003a darlington transitor array to switch 12V coil on the relays
	+ $1/each on amazon (also used for stepper motors), switches upto 7 channels;
- 3 - Deltrol 20852-81 relays
	+ This is equivelent to relay Skutt uses to switch sections/zones (Skutt model is SPDT, this is same series but DPDT),
	+ $17.50 each and about that much for shipping (https://www.galco.com/buy/Deltrol-Controls/20852-81);
- 12V power supply
	+ converts 120vac to 12vdc,
	+ $20 (https://www.amazon.com/gp/product/B00DECZ7WC/ref=oh_aui_detailpage_o01_s01?ie=UTF8&psc=1),
	+ might be over kill, but rail mounted,
	+ 12v power suply: relay coils, hdmi lcd, and  5v buck converter;
- 5V buck converter
	+ converts 12v to 5v USB connector for Pi power,
	+ $7 (https://www.amazon.com/gp/product/B071FJVRCT/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1);
- LCD screen and driver board, (most any hdmi monitor will work) ~$30;
- terminal blocks to distribute L1, L2, N and GND
	+ Ground, $6 (https://www.amazon.com/gp/product/B000K2MA9M/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1)
	+ L1,L2,Neutral, 3 @ $7/each, (https://www.amazon.com/gp/product/B000OTJ89Q/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1);
- #10 awg hi-temp appliance wire to each section;
- crimp terminals, #10 awg, hi-temp appliance
	+ $.16/each, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1);
	+ uses the same crimper used on the elements $16, (https://www.amazon.com/gp/product/B01L2TL63C/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1);
	+ the crimpers take muscle
- lugs #6 AWG copper
	+ $9 for 10 (https://www.amazon.com/gp/product/B073Y8Q9JQ/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
- big crimper
	+ $25, (https://www.amazon.com/gp/product/B07D7Q54N2/ref=oh_aui_detailpage_o01_s03?ie=UTF8&psc=1)
	+ I crimp 2 times, first time with correct size, second time reduced one notch(correct size is loose);
- din rail mounts
	+ $17/5 pair(https://www.amazon.com/gp/product/B01H1H86UU/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1);
- din rails
	+ $5/each (https://www.amazon.com/gp/product/B01FT485S0/ref=oh_aui_detailpage_o02_s01?ie=UTF8&psc=1);
- 14 THHN stranded, hardware store, to power 12V supply, white,red,greem 2' each
- heat shrink, Harbor Freight
- #10 32tpi tap and #21 jobber drill bit
	+ I have lots of 10-32 screws from rack mount hardware extras;
	+ tap a hole screw in a screw and use the $10 Harbor Freight angle grinder to flush it up on the back of the box.

Thermocouple tip: One side of the type-K thermocouple and type-k wire is magnetic (red side), Test with magnet to wire correctly.

I built a kiln shed and controller is on #0 kiln:
- #0 KS1027 new elements, lid repair, base repair, rust removal on controller boxes, painted, built steel rolling stand;
- #1 KS1027 Skutt, converted to gas, hit 1976F with one burner. (adding burner, 100lb LP tank, tweaking down draft), built steel rolling stand.
- #2 Jen-Ken, very good shape, kiln sitter(timer does not work), 2 ring, 10 brick 22" inside height, 06 bisques labors the last 100;


Stuff to get it to work:

- Pin-Out:

		MAX31855+:		3.3v
		MAX31855-:		GND
		MAX31855 CS:		GPIO 16
		MAX31855 DO:		GPIO 19
		MAX31855 CLK:		GPIO 21
		unl2003a 1:		GPIO 22
		unl2003a 3:		GPIO 23
		unl2003a 5:		GPIO 24
		unl2003a 8:		GND
		unl2003a 9:		12V
		RPLCD:		GPIO 2 SDA
		RPLCD:		GPIO 3 SCL
		RPLCD:		5V
		RPLCD:		GND

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
		chown pi:pi /var/www/html/style /var/www/html/images
		cp /home/PiLN/images/hdrback.png /var/www/html/images/hdrback.png
		cp /home/PiLN/images/piln.png   /var/www/html/images/piln.png
		cp /home/PiLN/style/style.css   /var/www/html/style/style.css

- needs update to switch out apache for lighttpd
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

		sudo raspi-config #enable interfaces ic2 & spi
		lsmod | grep spi

- Instal RPLCD for the 20x4 lcd:
		sudo pip install RPLCD
		sudo apt install python-smbus

- Install Adafruit MAX31855 Module:

		cd ~
		git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
		cd Adafruit_Python_MAX31855
		sudo python setup.py install

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

	+ Skutt KS1027 with old elements, oscilate at lower temps
			Proportional:  16.0
			Integral:       1.0
			Derivative:     0.6
			Time internal: 10 seconds

	+ blow dryer test rig (works great)
			Proportional:   6.00
			Integral:       0.08
			Derivative:     0.001
			Time internal:  6 seconds

- Using the Web App:

		On the same network that the RPi is connected, http://<RPi_IPAddress>/pilnapp/home.cgi
		Or on the controler RPi, http://localhost/pilnapp/home.cgi
