Electricity and heat are dangerous! Evaluate the risk and make go no go decision!

Stuff to get it to work:

- Pin-Out:

		RPLCD SDA:	GPIO 2
		RPLCD SCL:	GPIO 3
		RPLCD:		5V
		RPLCD:		GND
		MAX31855 3vo:		3.3v
		MAX31855 GND:		GND
		MAX31855 CS:		GPIO 16
		MAX31855 DO:		GPIO 19
		MAX31855 CLK:		GPIO 21
		unl2003a 1:		GPIO 22 
		unl2003a 3:		GPIO 23
		unl2003a 5:		GPIO 24
		unl2003a 8:		GND
		unl2003a 9:		12V
		unl2003a 16:	relay #1 coil
		unl2003a 14:	relay #2 coil
		unl2003a 12:	relay #3 coil
		12V:			relay 1,2 and 3 coils

- Install PiLN files in /home and create log directory:

		sudo adduser mypiln
		su - mypiln
		git clone git@github.com:BlakeCLewis/MyPiLN.git .
		mkdir ./log

- Install sqlite3:

		sudo apt-get install sqlite3

- Install lighthttpd:

		sudo apt-get install lighthttpd

- python3:

- Configure raspberry pi interfaces:

		sudo raspi-config
		#enable interfaces ic2 & spi

- Instal RPLCD for the 20x4 lcd:

		sudo pip3 install RPLCD
		sudo apt install python3-smbus

- Install Adafruit MAX31855 Module:
		cd ~
		git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
		cd Adafruit_Python_MAX31855
		sudo python3 setup.py install

- Start the firing daemon:

		python3 /home/mypiln/MyPiLN/daemon/pilnfired.py &

- Using the Web App:

		On the same network that the RPi is connected, http://<RPi_IPAddress>/pilnapp/home.cgi
		Or, on the controler RPi, http://localhost/pilnapp/home.cgi

- Tuning: 

	+ Skutt KS1027 with old elements, oscilate at lower temps, does well over 600C:
			Proportional:  20.0
			Integral:       0.2
			Derivative:     0.2
			Time internal: 30 seconds
			The response cycle is about 4 minutes.
