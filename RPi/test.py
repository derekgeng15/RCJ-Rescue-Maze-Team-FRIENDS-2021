import RPi.GPIO as GPIO
import time

COMPORT = 4 # Make sure this is correct
GPIO.setmode(GPIO.BCM)
GPIO.setup(COMPORT, GPIO.OUT)
GPIO.output(COMPORT, GPIO.LOW)

for i in range(10):
    GPIO.output(COMPORT, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(COMPORT, GPIO.LOW)
    time.sleep(0.01)
    