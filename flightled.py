#!/usr/bin/python
# Light up LEDs using GPIO in response to dump1090 flights
import socket
import select
import time
import datetime
import os
import RPi.GPIO as GPIO

# Durations to keep the LEDs turned on for after observation
INTERESTING_EXPIRE = 60*60*12 # 12 hours
MUNDANE_EXPIRE = 2#seconds
SELECT_TIMEOUT = 1#seconds

# assumes running a dump1090 instance locally
SBS1_HOST = "127.0.0.1"
SBS1_PORT = 30003

# List of callsigns to consider "interesting", versus mundane
WATCHLIST_PATH = "/home/pi/ads-b/watchlist.txt"

LOG_PATH = "/var/log/flightled.log"

# Pins
LED_G = 29 # G5
LED_R = 31 # G6
LED_Y = 32 # G12
LED_B = 33 # G13
GPIO.setmode(GPIO.BOARD)
GPIO.setup([LED_G, LED_R, LED_Y, LED_B], GPIO.OUT, initial=GPIO.HIGH)

def light_leds(values=True):
    if values is True: values = [0,0,1,0]
    if values is False: values = [0,0,0,0]

    [g, r, y, b] = values
    GPIO.output(LED_G, not g)
    GPIO.output(LED_R, not r)
    GPIO.output(LED_Y, not y)
    GPIO.output(LED_B, not b)
#light_leds(False)

def log(*a):
    s = " ".join(map(str, a))
    if not os.getenv("QUIET"): print s
    ts = datetime.datetime.now().isoformat()
    fd = file(LOG_PATH, "at+")
    fd.write("%s\t%s\n" % (ts, s))
    fd.flush()
    fd.close()


def main():
    log("Starting")
    GPIO.output(LED_G, True)
    GPIO.output(LED_R, True)

    watchlist = {}
    for line in file(WATCHLIST_PATH, 'rt').readlines():
       callsign = line.strip()
       watchlist[callsign] = 0
    watchlist["AAL1540"]=0
   
    while True: 
        try:
            s = socket.socket()
            s.connect((SBS1_HOST, SBS1_PORT))
            break
        except socket.error as e:
            log("Socket error %s, retrying..." % (e,))
            time.sleep(2)

 
    last_interesting = None
    last_mundane = None

    while True:
        readable, writable, exceptional = select.select([s], [], [s], SELECT_TIMEOUT)
    
        if readable:
            data = s.recv(1024)
            if len(data) == 0:
                log("Received EOF")
                break
            lines = data.split('\r\n')
            callsigns = {}
            for line in lines:
                fields = line.split(',')
                if len(fields) < 11: continue
                #print fields
                # read dump1090 flight data
                # SBS1 port 30003 format http://woodair.net/SBS/Article/Barebones42_Socket_Data.htm
                #print fields
                callsign = fields[10]
                callsign = callsign.strip() # space-padded for some reason
                if len(callsign) > 0:  # not all messages have callsigns
                    if callsign in watchlist:
                        watchlist[callsign] += 1
                        log("INTERESTING",callsign,watchlist[callsign],line)
                        last_interesting = time.time()
                        GPIO.output(LED_R, False)
                    else:
                        #log("Mundane",callsign)
                        last_mundane = time.time()
                        GPIO.output(LED_G, False)
        if exceptional:
            log("Exceptional condition from socket")
            # TODO: restart program?
            break
        
        if last_interesting and time.time() - last_interesting > INTERESTING_EXPIRE:
            log("Clearing interesting, expired %s" % (INTERESTING_EXPIRE,))
            GPIO.output(LED_R, True)
            last_interesting = None
    
        if last_mundane and time.time() - last_mundane > MUNDANE_EXPIRE:
            #log("Clearing mundane, expired %s" % (MUNDANE_EXPIRE,))
            GPIO.output(LED_G, True)
            last_mundane = None
   
if __name__ == "__main__":
    while True:
        main() 
