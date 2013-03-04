This is Python code written to run on a RaspberryPi and control v2.0 of the Arma Sonora Telematica. It's a simple state machine that gets tweets with a specific hashtag and controls a motor and some lights through relays connected to the GPIO pins.

More info here: http://astrovandalistas.cc/ast/

Dependencies:
* WiringPi-Python (https://github.com/WiringPi/WiringPi-Python)
	* sudo apt-get install python-dev
	* sudo apt-get install python-setuptools
	* git clone https://github.com/WiringPi/WiringPi-Python.git
	* cd WiringPi-Python
	* git submodule update --init
	* open WiringPi/wiringPi/piNes.c in a text editor and change #include \<wiringPi.h\> to #include "wiringPi.h"
	* sudo python setup.py install
	* cd WiringPi
	* ./build

* pygame (sudo apt-get install python-pygame)

* Tweepy (https://github.com/tweepy/tweepy)
	* sudo easy_install pip
	* sudo pip install tweepy

* Twython (https://github.com/ryanmcgrath/twython)
	* sudo easy_install twython

After installing all dependencies:
* git clone https://github.com/thiagohersan/bangMTYRpiPy.git
* cd bangMTYRpiPy
* ./bangMTY.py

---

The FontStruction [“Otis”](http://fontstruct.com/fontstructions/show/17629) by Nate Cox is licensed under a [Creative Commons Attribution Non-commercial No Derivatives license](http://creativecommons.org/licenses/by-nc-nd/3.0/).
