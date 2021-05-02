#!/usr/bin/python3
# Docs: https://www.ics.com/blog/control-raspberry-pi-gpio-pins-python
# Docs: https://learn.sparkfun.com/tutorials/raspberry-gpio/all

import RPi.GPIO as GPIO
import time
ledPort = 12

GPIO.setmode(GPIO.BCM) # Not GPIO.BOARD
GPIO.setup(ledPort, GPIO.OUT)

#GPIO.output(ledPort, GPIO.HIGH)
GPIO.output(ledPort, GPIO.LOW)

#GPIO.cleanup()