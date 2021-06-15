# After 5/16/21 Submission for RCJ Maze USA 2021
from commLOP import Comm
from nav import Nav

import time
import math
import struct
import numpy as np
import cv2
from ColorDetector import *
from LetterDetector import *
import RPi.GPIO as GPIO

def clearFile():
        print("Clearing file!")
        filePtr = open('wall.txt', 'w+')
        filePtr.truncate(0)
        filePtr.write("20 20 V\n")
        filePtr.close()

clearFile()

# Camera Stuff
capL = cv2.VideoCapture(0) # Left
capR = cv2.VideoCapture(1) # Right
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

while True:
    #clearFile()
    last_seen_frame=-5
    cycle_count = 1
    AI = Nav(readInWall=True)
    COMM = Comm()
    time.sleep(0.3)
    
    while True:
        print("\n--- CYCLE ", cycle_count, "---") # To denote new cycle
        cycle_count+= 1
        # Read in Arduino Wall Data for Current Tile
        msg, lop = COMM.read()
        
        if lop:
            break
        
        # Black Tile Procedure
        if len(msg) >= 4 and msg[0:4]=="1111":
            print("Blackout!")
            AI.blackout()
            #continue
        else:
            # Processing Wall Data and Inputting it Into Nav
            for i in range(4):
                if(msg[i]=="1"):
                    AI.markWall((i + AI.direction) % 4)
                    
        if 'CHECKPOINT' in msg:
            AI.markCheckpoint()
            AI.flush()
        
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

        # Will exit if wall data is in buffer or if detectionPin is set high
        while(COMM.in_waiting() and not COMM.doneDetection()): #cap.isOpened() and 

            # Capture frame-by-frame
            ret, frameL = capL.read()
            ret, frameR = capR.read() 
            writeFrames = True

            # Increasing frameCount
            frameCount += 1

            # Display the resulting frame
            #if writeFrames:
            #cv2.imwrite("imgs/Camera1 - Left" + str(frameCount) + ".png", frameL)
            #cv2.imwrite("imgs/Camera1 - Right" + str(frameCount) + ".png", frameR)

            # Double Detection Buffer
            if last_seen_frame + 15 >= frameCount: # Frame skip is 25 for easy 2 field
                continue
            
            # Victim Detection with Left Camera
            victimL = getColorVictimVectorized(frameL, direction="left", showFrame=False)
            if victimL == None:
                victimL =  getLetter(frameL, direction="left", showFrame=False, frameCounting=False, frameCount=frameCount)
            
            if victimL!=None:
                print("Saw Left Cam:", victimL, "at frame -", frameCount)
                if writeFrames:
                    #cv2.imwrite("imgs/Camera1 Left (V) - " + str(frameCount) + ".png", frameL)
                    pass
            else:
                pass
                #print("Saw Nothing Left Cam! -", frameCount)

            # Victim Detection with Right Camera
            victimR = getColorVictimVectorized(frameR, direction="right", showFrame=False)
            if victimR == None:
                victimR =  getLetter(frameR, direction="right", showFrame=False, frameCounting=False, frameCount=frameCount)
            
            if victimR!=None:
                print("Saw Right Cam:", victimR, "at frame -", frameCount)
                if writeFrames:
                    #cv2.imwrite("imgs/Camera1 Right (V) - " + str(frameCount) + ".png", frameR)
                    pass
            else:
                pass
                #print("Saw Nothing Right Cam! -", frameCount)
            
            # Updating Letter Buffer
            if victimL=="H": # Add this only for difficult field 2
                letterBufferL.append(victimL)
                letterBufferL.pop(0)
            letterBufferL.append(victimL)
            letterBufferL.pop(0)
            if victimR=="H": # Add this only for difficult field 2
                letterBufferR.append(victimR)
                letterBufferR.pop(0)
            letterBufferR.append(victimR)
            letterBufferR.pop(0)
            #letterBufferL.sort()
            #letterBufferR.sort()

            if letterBufferL[0] != None and (letterBufferL[0]==letterBufferL[1]):
                print("\n Found Left Victim!")
                COMM.sendVictim(victimL, "left")
                last_seen_frame = frameCount
                if writeFrames:
                    cv2.imwrite("imgs/Camera1 Left - " + str(frameCount) + ".png", frameL)
                #break

            elif letterBufferR[0] != None and (letterBufferR[0]==letterBufferR[1]):
                print("\n Found Right Victim")
                COMM.sendVictim(victimR, "right")
                last_seen_frame = frameCount
                if writeFrames:
                    cv2.imwrite("imgs/Camera1 Right - " + str(frameCount) + ".png", frameR)
                #break
    print("\n\n\n=====RESETTING PROGRAM=====\n\n\n")
    AI.clearFileBuffer()
capL.release()
capR.release()


