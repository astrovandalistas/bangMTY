This is Python code written to run on a RaspberryPi and control v2.0 of the Arma Sonora Telematica. It's a simple state machine that gets tweets with a specific hashtag and controls a motor and some lights through relays connected to the GPIO pins.

Dependencies:
- WiringPi-Python (https://github.com/WiringPi/WiringPi-Python)
	- sudo apt-get install python-dev
	- sudo apt-get install python-setuptools
	- git clone https://github.com/WiringPi/WiringPi-Python.git
	- cd WiringPi-Python
	- git submodule update --init
	- open WiringPi/wiringPi/piNes.c 
	- change #include \<wiringPi.h\> to #include "wiringPi.h" in WiringPi/wiringPi/piNes.c
	- sudo python setup.py install
	- cd WiringPi
	- ./build

- pygame (sudo apt-get install python-pygame)

More info here: http://astrovandalistas.cc/ast/
