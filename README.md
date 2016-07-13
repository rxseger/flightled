# flightled

Light up LEDs wired to Raspberry Pi's GPIO ports when flights are observed

## Installation
Save `flightled.py` to `/home/pi/ads-b/flightled.py`.

Save `flightled` to `/etc/init/flightled` and symlink it with
`sudo ln -s /etc/init.d/flightled /etc/rc5.d/S01flightled` to run on startup (optional).

Install and configure [dump1090](https://github.com/mutability/dump1090). It is assumed
to be running locally at localhost:30003, if remote edit `SBS1_HOST` and `SBS1_PORT` as needed.

Connect a green LED on pin #29 (GPIO 5), and red LED on pin #31 (GPIO 6). You can of course
use other output devices  and pins, edit `LED_G` and `LED_R` as desired.

Start with `sudo /etc/init.d/flightled start`.

## Configuration

By default:

* The green LED will light when any flight with a callsign is observed

* The red LED will light when a callsign in `watchlist.txt` is observed

for various lengths of time, edit `flightled.py` to configure. Logs
to `/var/log/flightled.log` by default.

## See also

Original article describing this software:

* [Raspberry Pi 3 GPIO: pushbuttons, LEDs for RC and BARR](https://medium.com/@rxseger/raspberry-pi-3-gpio-pushbuttons-leds-for-rc-and-barr-a1b947dc6b40#.cyiizfryh)

## License

MIT
