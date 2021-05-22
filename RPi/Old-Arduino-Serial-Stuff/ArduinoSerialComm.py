# Arduino Serial with Comm Library
from comm import Comm
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

# Warming Up the camera
ret, frame = cap.read()
time.sleep(1)

frame_size = (320, 240)  #Width, Height
#result = cv2.VideoWriter('imgs/cam.mp4', cv2.VideoWriter_fourcc(*'MLPG'), 10, frame_size)

AI = Nav(readInWall=False)

while True:
    # Reading in Wall Data for current tile from Arduino
    msg = comm.read()
    for i in range(4):
            if(msg[i]=="1"):
                AI.markWall((i + AI.direction) % 4)


    # Waiting for Arduino to request Commands
    msg = comm.read()
    
    # Command Logic
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
    #commandsMsg = commandsMsg + "\n"

    # Writing 
    print("Sending Commands. . .")
    comm.write(commandsMsg)

    # Victim Deteciton Loop
    print("Starting Victim Detection")
    letterBuffer = [None,None,None]
    while(cap.isOpened() and comm.in_waiting == 0):
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
            #continue
        else:
            print("Saw Nothing! -", frameCount)
        
        frameCount+=1

        letterBuffer.append(letter)
        letterBuffer.pop(0)
        if letterBuffer[0] != None and (letterBuffer[0]==letterBuffer[1] and letterBuffer[1]==letterBuffer[2]):
            print("Sent Letter to Arduino:", letter)
            #comm.writeOut(letter)
    print("Finished Detection!")

#result.release()
cap.release()