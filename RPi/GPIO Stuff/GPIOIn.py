#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
ledPort = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPort, GPIO.IN)

#for i in range(10):
while True:
    inp = GPIO.input(ledPort)
    if inp:
        print("Reading in HIGH!")
    else:
        print("Reading in LOW!")
    time.sleep(0.5)

GPIO.cleanup()