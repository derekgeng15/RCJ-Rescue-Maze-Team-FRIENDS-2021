# After 5/16/21 Submission for RCJ Maze USA 2021
from comm import Comm
from nav import Nav

import time
import math
import struct
import numpy as np
import cv2
from LetterDetector import *
from ColorDetector import *
import RPi.GPIO as GPIO

def clearFile():
        print("Clearing file!")
        filePtr = open('wall.txt', 'w+')
        filePtr.truncate(0)
        filePtr.write("20 20 V\n")
        filePtr.close()

clearFile()

# Camera Stuff
capL = cv2.VideoCapture(1) # Left
capR = cv2.VideoCapture(0) # Right
capL.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capL.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
capL.set(cv2.CAP_PROP_FPS,30)
#cap.set(cv2.CAP_PROP_BUFFERSIZE, 10) # Buffer Size
capR.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capR.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
capR.set(cv2.CAP_PROP_FPS,30)
frameCount = 0

# Warming Up the camera
ret, frameL = capL.read()
ret, frameR = capR.read()
time.sleep(1)

frame_size = (320, 240)  #Width, Height
last_seen_frame=-5
cycle_count = 1

AI = Nav(readInWall=True)
COMM = Comm()

while True:
    print("\n--- CYCLE ", cycle_count, "---") # To denote new cycle
    cycle_count+= 1
    # Read in Arduino Wall Data for Current Tile
    msg = COMM.read()

    # Processing Wall Data and Inputting it Into Nav
    for i in range(4):
        if(msg[i]=="1"):
            AI.markWall((i + AI.direction) % 4)

    # Black Tile Procedure
    if len(msg) >= 4 and msg[0:4]=="1111":
        print("Blackout!")
        AI.blackout()
    
    # Calculate Movement Commands
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
    print("Commands: " + commandsMsg)

    # Writing Movement Commands to Arduino
    COMM.write(commandsMsg)
    
    # Finished Run Procedure
    if len(commands) == 0:
        print("WE\'RE DONE!!!!!!!!!!!!!!!!!!!!!!!")
        break

    # Victim Deteciton Loop
    letterBufferL = [None,None]
    letterBufferR = [None,None]

    while(COMM.in_waiting()): #cap.isOpened() and 

        # Capture frame-by-frame
        ret, frameL = capL.read()
        ret, frameR = capR.read() 
        writeFrames = True

        # Display the resulting frame
        #cv2.imshow('Camera1',frame)
        #cv2.imwrite("imgs/Camera1 - Left" + str(frameCount) + ".png", frameL)

        # Increasing frameCount
        frameCount += 1

        # Double Detection Buffer
        if last_seen_frame + 20 >= frameCount:
            continue
        
        # Victim Detection with Left Camera
        victimL = getColorVictimVectorized(frameL, direction="left", showFrame=False)
        if victimL == None:
            victimL =  getLetter(frameL, direction="left", showFrame=False, frameCounting=False, frameCount=frameCount)
        
        if victimL!=None:
            print("Saw Left Cam:", victimL, "at frame -", frameCount)
            if writeFrames:
                cv2.imwrite("imgs/Camera1 Left - " + str(frameCount) + ".png", frameL)
        else:
            print("Saw Nothing Left Cam! -", frameCount)

        # Victim Detection with Right Camera
        victimR = getColorVictimVectorized(frameR, direction="right", showFrame=False)
        if victimR == None:
            victimR =  getLetter(frameR, direction="right", showFrame=False, frameCounting=False, frameCount=frameCount)
        
        if victimR!=None:
            print("Saw Right Cam:", victimR, "at frame -", frameCount)
            if writeFrames:
                cv2.imwrite("imgs/Camera1 Right - " + str(frameCount) + ".png", frameR)
        else:
            print("Saw Nothing Right Cam! -", frameCount)
        
        # Updating Letter Buffer
        letterBufferL.append(victimL)
        letterBufferL.pop(0)
        letterBufferR.append(victimR)
        letterBufferR.pop(0)
        #letterBufferL.sort()
        #letterBufferR.sort()

        if letterBufferL[0] != None and (letterBufferL[0]==letterBufferL[1]):
            print("\n Found Left Victim!")
            COMM.sendVictim(victimL, "left")
            last_seen_frame = frameCount
            # if writeFrames:
            #     cv2.imwrite("imgs/Camera1 Left - " + str(frameCount) + ".png", frameL)
            break

        elif letterBufferR[0] != None and (letterBufferR[0]==letterBufferR[1]):
            print("\n Found Right Victim")
            COMM.sendVictim(victimR, "right")
            last_seen_frame = frameCount
            # if writeFrames:
            #     cv2.imwrite("imgs/Camera1 Right - " + str(frameCount) + ".png", frameR)
            break

capL.release()
capR.release()