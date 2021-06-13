import serial
import struct
import time
import numpy as np
import RPi.GPIO as GPIO

'''int_encode = b'2'
float_encode = b'42.3'
confirm ="Confirm\n"
#string1_encode = string1.encode()

#ser = serial.Serial('/dev/ttyAMA0', 9600)
'''

class Comm:
    def __init__(self):
        self.ser = serial.Serial(
            port = '/dev/serial0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )

        # GPIO Stuff
        self.INTERRUPT = 4 # Port 3 on MegaPi
        self.BITONE = 16 # Corresponds to Pin 49 on Arduino
        self.BITTWO = 20 # Corresponds to Pin 5 on Arduino
        self.DIRECTIONPIN = 21 # Corresponds to Pin 4 on Arduino
        self.DETECTIONPIN = 26 # Corresponds to Pin 6 on Arduino
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INTERRUPT, GPIO.OUT)
        GPIO.setup(self.BITONE, GPIO.OUT)
        GPIO.setup(self.BITTWO, GPIO.OUT)
        GPIO.setup(self.DIRECTIONPIN, GPIO.OUT)
        GPIO.setup(self.DETECTIONPIN, GPIO.IN)
        self.setPins() # Default sets all pins to low

    # If there's stuff in the serial buffer
    def in_waiting(self):
        return self.ser.in_waiting == 0

    # If the detection pin is set to high (then stop detection)
    def doneDetection(self):
        return GPIO.input(self.DETECTIONPIN)

    # Sets all pins (interrupt, letter, bitone, bittwo)
    def setPins(self, interrupt=GPIO.LOW, bittone=GPIO.LOW, bittwo=GPIO.LOW, directionpin=GPIO.LOW):
        GPIO.output(self.INTERRUPT, interrupt)
        GPIO.output(self.BITONE, bittone)
        GPIO.output(self.BITTWO, bittwo)
        GPIO.output(self.DIRECTIONPIN, directionpin)

    # Just waits for buffer to be availble, and then reads it in
    def read(self):
        done = False
        LOP = False
        print("Waiting...")
        while not done:
            try:
                while(self.in_waiting()): #if there's something in the buffer
                    pass
                size = self.ser.in_waiting
                x = self.ser.read_until("\n")
                msg = x.decode('ascii')
                if msg[0:5]=="RESET":
                    LOP = True
                print("Recieved: \"", msg, "\" from arduino")
                print("Message Size:", size)
                done = True
            except IOError as e:
                print ("Something Bad Happened!")
                print(e)
            time.sleep(0.05)
        return msg, LOP

    # Just writes a message to arduino
    def write(self, msg):
        self.ser.write((msg+'\n').encode())
        self.ser.flush()
        print("Wrote: \"", msg, "\" to arduino")

    def convertVictimToKits(self, victim):
        victim.upper()
        if victim=="H":
            return 3
        if victim=="S":
            return 2
        if victim=="U":
            return 0
        if victim=="RED":
            return 1
        if victim=="YELLOW" or victim[0]=='y' or victim[0]=="Y":
            return 1
        if victim=="GREEN":
            return 0
        return 0
    
    def sendVictim(self, victim, direction):
        # Number of kits
        numberOfKits = self.convertVictimToKits(victim)
        bits = [GPIO.LOW, GPIO.LOW]
        if numberOfKits == 1:
            bits = [GPIO.HIGH, GPIO.LOW]
        if numberOfKits == 2:
            bits = [GPIO.LOW, GPIO.HIGH]
        if numberOfKits == 3:
            bits = [GPIO.HIGH, GPIO.HIGH]

        # Direction
        dir = None
        if direction == "left":
            dir = GPIO.LOW
        else:
            dir = GPIO.HIGH
        
        # Send over victim info
        print("Sending Victim:", numberOfKits, direction)
        self.setPins(bittone=bits[0], bittwo=bits[1], directionpin=dir)

        # Interrupts the Arduino to notify found victim
        print("Set Interrupt Pin to High!")
        GPIO.output(self.INTERRUPT, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.INTERRUPT, GPIO.LOW)
        print("Set Interrupt Pin back to Low!")
        
        #self.setPins() # Reset all pins back to low
        print("Done!")

# OUTDATED===================================================================
'''
# Read and then write a confirm message
def readIn():
    msg = read()
    write("Confirm\n")
    print("Sent Confirmation Message!")
    return msg

# Write and then read a confirm message
def writeOut(msg):
    write(msg)
    confimration = read()
    print("Recieved Confimration Message!")
'''
