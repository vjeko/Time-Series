#!/usr/bin/python

import RPi.GPIO as GPIO  
import time

PIN = 2
INTERVAL = 4

GPIO.setmode(GPIO.BCM)  
#GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, 0)
time.sleep(INTERVAL)
GPIO.output(PIN, 1)
