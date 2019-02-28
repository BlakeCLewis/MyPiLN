Electricity and heat are dangerous! Evaluate the risk and make go no go decision!

Stuff to get it to work:

- Pin-Out:

		RPLCD:		GPIO 2 SDA
		RPLCD:		GPIO 3 SCL
		RPLCD:		5V
		RPLCD:		GND
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
		unl2003a 16:	relay #1 coil - (input is accross the chip on pin1)
		unl2003a 14:	relay #2 coil - (input is pin3)
		unl2003a 12:	relay #3 coil - (input is pin5)
        12V:	relay 1,2 and 3 coils

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

- !!!!!!! needs update to switched out Apache for lighttpd !!!
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

- Tuning: 

	+ Skutt KS1027 with old elements, oscilate at lower temps, does well over 600C:
			Proportional:  20.0
			Integral:       0.2
			Derivative:     0.2
			Time internal: 30 seconds
            The response cycle is about 4 minutes.

- Using the Web App:

		On the same network that the RPi is connected, http://<RPi_IPAddress>/pilnapp/home.cgi
		Or, on the controler RPi, http://localhost/pilnapp/home.cgi

- Start the firing daemon:

		python3 ./daemon/pilnfired.py
