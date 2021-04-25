import serial
import time
from nav import Nav
import math
import struct
import numpy as np
import cv2
from LetterDetector import *

def clearFile():
        print("Clearing file!")
        filePtr = open('wall.txt', 'w+')
        filePtr.truncate(0)
        filePtr.write("20 20 V\n")
        filePtr.close()

clearFile()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS,30)
frameCount = 0

frame_size = (320, 240)  #Width, Height
#result = cv2.VideoWriter('imgs/cam.mp4', cv2.VideoWriter_fourcc(*'MLPG'), 10, frame_size)

AI = Nav(readInWall=False)

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
            x = ser.read_until("\n")
            msg = x.decode('ascii')
            print("Got:", msg, end="\n")
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
    letterBuffer = [None,None,None]
    while(cap.isOpened() and ser.in_waiting == 0):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Display the resulting frame
        #cv2.imshow('Camera1',frame)
        cv2.imwrite("imgs/Camera1 - " + str(frameCount) + ".png", frame)
        #result.write(frame)
        
        letter = getLetter(frame, showFrame=False, frameCounting=True, frameCount=frameCount)
        frameCount+=1

        if letter!=None:
            #ser.write((commandsMsg).encode())
            #print("Sent: " + commandsMsg)
            print("Saw:", letter)
            #continue
        else:
            print("Saw Nothing!")
        
        letterBuffer.append(letter)
        letterBuffer.pop(0)
        if letterBuffer[0] != None and (letterBuffer[0]==letterBuffer[1] and letterBuffer[1]==letterBuffer[2]):
            print("Sent Letter to Arduino:", letter)
            '''ser.write((letter).encode())
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
                time.sleep(0.05)'''

result.release()
cap.release()