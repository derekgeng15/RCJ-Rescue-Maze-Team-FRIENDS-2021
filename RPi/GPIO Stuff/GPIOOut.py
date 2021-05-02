#!/usr/bin/python3
# Port 12 is PWM

import RPi.GPIO as GPIO
import time
ledPort = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(ledPort, GPIO.OUT)

for i in range(10):
    print(i)
    GPIO.output(ledPort, GPIO.HIGH)
    print("HIGH!")
    time.sleep(0.3)
    GPIO.output(ledPort, GPIO.LOW)
    print("LOW!")
    time.sleep(0.3)
    print()

GPIO.cleanup()