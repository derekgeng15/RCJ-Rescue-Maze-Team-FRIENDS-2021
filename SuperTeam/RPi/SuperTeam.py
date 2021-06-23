# After 5/16/21 Submission for RCJ Maze USA 2021
from commLOP import Comm
from nav import Nav
from server import Server

print("Starting Server Object. . .")
s = Server()

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
capL.set(cv2.CAP_PROP_BUFFERSIZE, 2)
#cap.set(cv2.CAP_PROP_BUFFERSIZE, 10) # Buffer Size
capR.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capR.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
capR.set(cv2.CAP_PROP_FPS,30)
capR.set(cv2.CAP_PROP_BUFFERSIZE, 2)
frameCount = 0

# Warming Up the camera
ret, frameL = capL.read()
ret, frameR = capR.read()
time.sleep(1)

frame_size = (320, 240)  #Width, Height

while True:
    #clearFile()
    last_seen_frame=0
    cycle_count = 1
    AI = Nav(readInWall=True)
    COMM = Comm()
    Hlocation = -1 # H Tile Location
    Ylocation = -1 # Y Tile Location
    Hcoord = None
    Ycoord = None
    Hside = -1 # H Side
    Yside = -1 # Y side
    coordinateDictionary = {(20, 20) : 1, (19, 20) : 2, (18, 20) : None, (17, 20) : 3,
                            (17, 19) : None, (17, 18) : 9, (17, 17): 12, (18, 17) : 11,
                            (19, 17) : 10, (20, 17) : None, (20, 18) : 6, (20, 19) : 4,
                            (19, 19) : 5, (18, 19) : None, (18, 18) : 8, (19, 18) : 7}
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
        
        last_seen_frame = frameCount

        # Will exit if wall data is in buffer or if detectionPin is set high
        while(COMM.in_waiting()): #cap.isOpened() and 
            
            # Capture frame-by-frame
            ret, frameL = capL.read()
            ret, frameR = capR.read() 
            writeFrames = True
            
            if last_seen_frame + 15 <= frameCount: # COMM.doneDetection() or 
                continue
            
            print("Last Seen Frame", last_seen_frame)
            print("Frame Count", frameCount)

            # Increasing frameCount
            frameCount += 1
            
            if frameCount == 1 or frameCount == 2:
                continue

            # Display the resulting frame
            if writeFrames:
                #cv2.imwrite("imgs/Camera1 - Left" + str(frameCount) + ".png", frameL)
                #cv2.imwrite("imgs/Camera1 - Right" + str(frameCount) + ".png", frameR)
                pass
            
            # Double Detection Buffer
            #if last_seen_frame + 15 >= frameCount: # Frame skip is 25 for easy 2 field
            #    continue
            
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
            letterBufferL.append(victimL)
            letterBufferL.pop(0)
            letterBufferL.append(victimL)
            letterBufferL.pop(0)
            
            letterBufferR.append(victimR)
            letterBufferR.pop(0)
            letterBufferR.append(victimR)
            letterBufferR.pop(0)
            #letterBufferL.sort()
            #letterBufferR.sort()

            if letterBufferL[0] != None and (letterBufferL[0]==letterBufferL[1]):
                print("\n Found Left Victim!")
                COMM.sendVictim(victimL, "left")
                #frameCount += 15
                if writeFrames:
                    cv2.imwrite("imgs/Camera1 Left - " + str(frameCount) + ".png", frameL)
                #break

            elif letterBufferR[0] != None and (letterBufferR[0]==letterBufferR[1]):
                print("\n Found Right Victim")
                COMM.sendVictim(victimR, "right")
                #frameCount += 15
                if writeFrames:
                    cv2.imwrite("imgs/Camera1 Right - " + str(frameCount) + ".png", frameR)
                #break
            
        print("Done Detection Pin:", COMM.doneDetection())
        if True: # COMM.doneDetection() is not working for some reason
            print('\n')
            if letterBufferL[0] == 'H':
                print("Found H:", AI.getPrevLocation())
                Hlocation = coordinateDictionary[AI.getPrevLocation()]
                Hcoord = AI.getPrevLocation()
                print("Tile:", Hlocation)
                Hside = (AI.getPrevDirection()+3)%4
                print("Side:", Hside)
            elif letterBufferL[0] == "Yellow":
                print("Found Yellow:", AI.getPrevLocation())
                Ylocation = coordinateDictionary[AI.getPrevLocation()]
                Ycoord = AI.getPrevLocation()
                print("Tile:", Ylocation)
                Yside = (AI.getPrevDirection()+3)%4
                print("Side:", Yside)
            if letterBufferR[0] == 'H':
                print("Found H:", AI.getPrevLocation())
                Hlocation = coordinateDictionary[AI.getPrevLocation()]
                Hcoord = AI.getPrevLocation()
                print("Tile:", Hlocation)
                Hside = (AI.getPrevDirection()+1)%4
                print("Side:", Hside)
            elif letterBufferR[0] == "Yellow":
                print("Found Yellow:", AI.getPrevLocation())
                Ylocation = coordinateDictionary[AI.getPrevLocation()]
                Ycoord = AI.getPrevLocation()
                print("Tile:", Ylocation)
                Yside = (AI.getPrevDirection()+1)%4
                print("Side:", Yside)
            print('\n')
            
    if Hlocation != -1 and Ylocation != -1:
        # Maze must be completely explored for this to work
        print('SAW BOTH H AND YELLOW VICTIMS')

        print("Hlocation:", Hlocation)
        print("Hcoord:", Hcoord)
        print("Hside:", Hside)
        print("Ylocation:", Ylocation)
        print("Ycoord:", Ycoord)
        print("Yside:", Yside)
        
        homeToH, direction = AI.calculatePath((20, 20), Hcoord, 0)
        HToY, direction = AI.calculatePath(Hcoord, Ycoord, direction)
        YToH, direction = AI.calculatePath(Ycoord, (20, 20), direction)

        def parseCommands(commands):
            parsed = ""
            for command in commands:
                if command=='FORWARD':
                    parsed += 'F'
                elif command=='RIGHT':
                    parsed += 'R'
                elif command=='BACKWARD':
                    parsed += 'B'
                else:
                    parsed += 'L'
            return parsed

        homeToH = parseCommands(homeToH)
        HToY = parseCommands(HToY)
        YToH = parseCommands(YToH)
        path = homeToH + 'H' + str(Hside) + HToY + 'Y' + str(Yside) + YToH

        print("Calculated Path:", path)
        
        #s.sendData(Hlocation, Hside, Ylocation, Yside)
        #print("Sent Server Data!")
                
    print("\n\n\n=====RESETTING PROGRAM=====\n\n\n")
    AI.clearFileBuffer()
capL.release()
capR.release()


