This code branch is the current usable branch. It has been stripped down to the minimial stuff. No pictures in the readme, code is the most usable.


Electricity and heat are dangerous! Evaluate the risk and make your go/no-go decision!

Stuff to get it to work:

- Pin-Out:

		kilnsitter:	3.3v
		kilnsitter:	GPIO 27

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

		unl2003a 1:	GPIO 22 
		unl2003a 3:	GPIO 23
		unl2003a 5:	GPIO 24
		unl2003a 8:	GND
		unl2003a 9:	12V
		unl2003a 16:	relay #1 coil
		unl2003a 14:	relay #2 coil
		unl2003a 12:	relay #3 coil
		12V:		relay 1,2 and 3 coils

- Install PiLN files in /home and create log directory:

		sudo adduser mypiln
		su - mypiln
		git clone git@github.com:BlakeCLewis/MyPiLN.git .
		mkdir ./log

- Install sqlite3:

		sudo apt-get install sqlite3

- Configure raspberry pi interfaces:

		sudo raspi-config
		#enable interfaces ic2 & spi

- Instal RPLCD for the 20x4 lcd:

		sudo pip3 install RPLCD

- Install MAX31856 Module:

		cd
		sudo apt-get update
		sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
		git clone https://github.com/adafruit/Adafruit_Python_GPIO.git
		cd Adafruit_Python_GPIO
		sudo python3 setup.py install
		cd
		git clone git@github.com:johnrbnsn/Adafruit_Python_MAX31856.git
		cd Adafruit_Python_MAX31856
		sudo python3 setup.py install
- test modules:

		cd ~/MyPiLN/daemon
		python3 display.py
		python3 max31856_test.py

- Install lighthttpd:

		sudo apt-get install lighttpd
                sudo cp lighttpd.conf /etc/lighttpd/
                cd /etc/lighttpd/conf-enabled
                sudo ln -s ../conf-available/10-cgi.conf .
                sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
                sudo iptables save
                cd 
                chown www-data:www-data MyPiLN/html/pilnstat.json

- Accessing the Web App:

		On the same network that the RPi is connected, http://<RPi_IPAddress>/pilnapp/home.cgi
		Or, on the controler RPi, http://localhost/pilnapp/home.cgi
		The graphing is google api and requires web access by the browser 

- Start the firing daemon:

		python3 /home/mypiln/MyPiLN/daemon/pilnfired.py &


- Tuning: 

	+ Skutt KS1027 with old elements:

			Proportional:   3.0
			Integral:       0.4
			Derivative:    13.0
			Time internal: 30 seconds
			The response cycle is about 4 minutes.

