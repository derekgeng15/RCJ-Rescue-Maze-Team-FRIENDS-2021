# Arduino Serial without Comm Library
import serial
import time
from nav import Nav
import math
import struct
import numpy as np
import cv2
from LetterDetector import *
import RPi.GPIO as GPIO

def clearFile():
        print("Clearing file!")
        filePtr = open('wall.txt', 'w+')
        filePtr.truncate(0)
        filePtr.write("20 20 V\n")
        filePtr.close()

clearFile()

# GPIO Stuff
# Port 4 on StereoPi
# Port 22 on MegaPi
COMPORT = 4 # Make sure this is correct
GPIO.setmode(GPIO.BCM)
GPIO.setup(COMPORT, GPIO.OUT)
GPIO.output(COMPORT, GPIO.LOW)

# Camera Stuff
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS,30)
#cap.set(cv2.CAP_PROP_BUFFERSIZE, 10) # Buffer Size
frameCount = 0

# Warming Up the camera
ret, frame = cap.read()
time.sleep(1)

frame_size = (320, 240)  #Width, Height
#result = cv2.VideoWriter('imgs/cam.mp4', cv2.VideoWriter_fourcc(*'MLPG'), 10, frame_size)

AI = Nav(readInWall=True)

int_encode = b'2'
float_encode = b'42.3'
confirm ="Confirm\n"
#string1_encode = string1.encode()

#ser = serial.Serial('/dev/ttyAMA0', 9600)

ser = serial.Serial(
    port = '/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

while True:
    #Waiting for Arduino to give Wall Data for current tile
    done = False
    print("Waiting...")
    while not done:
        try:
            while(ser.in_waiting == 0): #if there's something in the buffer
                pass
            print("Size: " + str( ser.in_waiting))
            x = ser.read_until('\n')
            msg = x.decode('ascii')
            print("Got:", msg, end='\n')
            for i in range(4):
                if(msg[i]=="1"):
                    AI.markWall((i + AI.direction) % 4)
            done = True
         #   print("Bytes in buff: " + str(ser.in_waiting))
        except IOError as e:
            print ("Something Bad Happened!")
            print(e)
        time.sleep(0.05)
    ser.flush()
    ser.write("Confirm\n".encode())
    print("Responded to Arduino Confirm!")

    # Waiting for Arduino to request Commands
    done = False
    print("Waiting...")
    while not done:
        try:
            while(ser.in_waiting == 0): #if there's something in the buffer
                pass
            print("Size: " + str( ser.in_waiting))
            x = ser.read_until("\n")
            msg = x.decode('ascii')
            print("Got:", msg, end="\n")
            done = True
         #   print("Bytes in buff: " + str(ser.in_waiting))
        except IOError as e:
            print ("Something Bad Happened!")
            print(e)
        time.sleep(0.05)
    ser.flush()
    ser.write("Confirm\n".encode())
    print("Responded to Arduino Confirm!")
    
    commands = AI.calculate()
    commandsMsg = ""
    for command in commands:
        unformattedCommand = AI.convertCommand(command)
        if unformattedCommand == 0:
            formattedCommand = 'U'
        elif unformattedCommand == 1:
            formattedCommand = 'R'
        elif unformattedCommand == 2:
            formattedCommand = 'D'
        else:
            formattedCommand = 'L'
        commandsMsg+=formattedCommand
    commandsMsg = commandsMsg + '\n'

    ser.write((commandsMsg).encode())
    print("Send Command: " + commandsMsg)
    done = False
    while not done:
        try:
            while(ser.in_waiting > 0): #if there's something in the buffer
                pass
            print("Got confirm message:")
            x = ser.read_until("\n")
            print("Got:", x.decode("ascii"), end="\n")
            done = True
        except IOError as e:
            print ("Something Bad Happened!")
            print(e)
        time.sleep(0.05)

    # Victim Deteciton Loop
    letterBuffer = [None,None]
    while(ser.in_waiting == 0): #cap.isOpened() and 
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Display the resulting frame
        #cv2.imshow('Camera1',frame)
        #cv2.imwrite("imgs/Camera1 - " + str(frameCount) + ".png", frame)
        #result.write(frame)
        
        letter = getLetter(frame, showFrame=False, frameCounting=False, frameCount=frameCount)

        if letter!=None:
            #ser.write((commandsMsg).encode())
            #print("Sent: " + commandsMsg)
            print("Saw:", letter, "at frame -", frameCount)
            cv2.imwrite("imgs/Camera1 - " + str(frameCount) + ".png", frame)
            #continue 
        else:
            print("Saw Nothing! -", frameCount)
        
        frameCount+=1

        letterBuffer.append(letter)
        letterBuffer.pop(0)
        cv2.waitKey(1)
        #if letterBuffer[0] != None and (letterBuffer[0]==letterBuffer[1] and letterBuffer[1]==letterBuffer[2]):
        if letterBuffer[0] != None and (letterBuffer[0]==letterBuffer[1]):
            print("Set Interrupt Pin to High!")
            GPIO.output(COMPORT, GPIO.HIGH)
            print("Sent Letter to Arduino:", letter)
            ser.write((letter + " LETTER\n").encode())
            ser.flush()
            time.sleep(0.15)
            '''done = False
            while not done:
                try:
                    while(ser.in_waiting > 0): #if there's something in the buffer
                        pass
                    print("Got confirm message:")
                    x = ser.read_until("\n")
                    print("Got:", x.decode("ascii"), end="\n")
                    done = True
                    print("Buffer State:", ser.in_waiting)
                except IOError as e:
                    print ("Something Bad Happened!")
                    print(e)
                time.sleep(0                                                                        .05)'''

            GPIO.output(COMPORT, GPIO.LOW)
            print("Set Interrupt Pin back to Low!")
            break

result.release()
cap.release()