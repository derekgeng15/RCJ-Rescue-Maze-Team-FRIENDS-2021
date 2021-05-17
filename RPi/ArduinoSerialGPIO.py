# Arduino Serial without Comm Library
import serial
import time
from nav import Nav
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

def convertVictimToKits(victim):
    victim.upper()
    if victim=="H":
        return "3"
    if victim=="S":
        return "2"
    if victim=="U":
        return "0"
    if victim=="RED":
        return "1"
    if victim=="YELLOW" or victim[0]=='y' or victim[0]=="Y":
        return "1"
    if victim=="GREEN":
        return "0"
    return "0"

# GPIO Stuff
# Port 4 on StereoPi
# Port 22 on MegaPi
COMPORT = 4 # Make sure this is correct
GPIO.setmode(GPIO.BCM)
GPIO.setup(COMPORT, GPIO.OUT)
GPIO.output(COMPORT, GPIO.LOW)

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

last_seen_frame=-5

while True:
    #Waiting for Arduino to give Wall Data for current tile
    done = False
    print("Waiting...")
    msg = ""
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
    #ser.flush()
    #ser.write("Confirm\n".encode())
    #print("Responded to Arduino Confirm!")
    if len(msg) >= 4 and msg[0:4]=="1111":
        print("Blackout!")
        AI.blackout()
    
    '''if len(msg) < 10:
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
    '''
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
    if len(commands) == 0:
        print("WE\'RE DONE!!!!!!!!!!!!!!!!!!!!!!!")
        break
    '''done = False
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

    # Victim Deteciton Loop
    letterBufferL = [None,None]
    letterBufferR = [None,None]
    prev_victim = ""
    #last_seen_frame = frameCount
    while(ser.in_waiting == 0): #cap.isOpened() and 
        # Capture frame-by-frame
        ret, frameL = capL.read()
        ret, frameR = capR.read() 
        # Display the resulting frame
        #cv2.imshow('Camera1',frame)
        #cv2.imwrite("imgs/Camera1 - Left" + str(frameCount) + ".png", frameL)
        #result.write(frame)
        
        '''letter = getLetter(frame, showFrame=False, frameCounting=False, frameCount=frameCount)

        if letter!=None:
            #ser.write((commandsMsg).encode())
            #print("Sent: " + commandsMsg)
            print("Saw:", letter, "at frame -", frameCount)
            cv2.imwrite("imgs/Camera1 - " + str(frameCount) + ".png", frame)
            #continue 
        else:
            print("Saw Nothing! -", frameCount)'''

        if last_seen_frame + 20 >= frameCount:
            frameCount += 1
            continue

        victimL = getColorVictimVectorized(frameL, direction="left", showFrame=False)
        if victimL == None:
            victimL =  getLetter(frameL, direction="left", showFrame=False, frameCounting=False, frameCount=frameCount)
        
        if victimL!=None:
            #ser.write((commandsMsg).encode())
            #print("Sent: " + commandsMsg)
            print("Saw Left Cam:", victimL, "at frame -", frameCount)
            cv2.imwrite("imgs/Camera1 Left - " + str(frameCount) + ".png", frameL)
            #continue 
        else:
            print("Saw Nothing Left Cam! -", frameCount)

        victimR = getColorVictimVectorized(frameR, direction="right", showFrame=False)
        if victimR == None:
            victimR =  getLetter(frameR, direction="right", showFrame=False, frameCounting=False, frameCount=frameCount)
        
        if victimR!=None:
            #ser.write((commandsMsg).encode())
            #print("Sent: " + commandsMsg)
            print("Saw Right Cam:", victimR, "at frame -", frameCount)
            cv2.imwrite("imgs/Camera1 Right - " + str(frameCount) + ".png", frameR)
            #continue 
        else:
            print("Saw Nothing Right Cam! -", frameCount)
        
        frameCount+=1

        letterBufferL.append(victimL)
        letterBufferL.pop(0)
        letterBufferR.append(victimR)
        letterBufferR.pop(0)
        #letterBufferL.sort()
        #letterBufferR.sort()
        cv2.waitKey(1)
        #if letterBuffer[0] != None and (letterBuffer[0]==letterBuffer[1] and letterBuffer[1]==letterBuffer[2]):
        if letterBufferL[0] != None and (letterBufferL[0]==letterBufferL[1]):
            if ser.in_waiting != 0:
                continue
            print("Set Interrupt Pin to High!")
            GPIO.output(COMPORT, GPIO.HIGH)
            time.sleep(0.15)
            GPIO.output(COMPORT, GPIO.LOW)
            print("Set Interrupt Pin back to Low!")
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
                time.sleep(0.05)'''
            ser.write((convertVictimToKits(victimL) + "L VICTIM - " + str(frameCount) +"\n").encode())
            print("Sent Left Cam Victim to Arduino:", victimL)
            ser.flush()
            #time.sleep(1.5)
            
            last_seen_frame = frameCount
            #cv2.imwrite("imgs/Camera1 Left - " + str(frameCount) + ".png", frameL)
            break

        elif letterBufferR[0] != None and (letterBufferR[0]==letterBufferR[1]):
            if ser.in_waiting != 0:
                continue
            print("Set Interrupt Pin to High!")
            GPIO.output(COMPORT, GPIO.HIGH)
            print("Sent Right Cam Victim to Arduino:", victimR)
            ser.write((convertVictimToKits(victimR) + "R VICTIM - " + str(frameCount) + "\n").encode())
            ser.flush()
            time.sleep(0.15)
            GPIO.output(COMPORT, GPIO.LOW)
            #time.sleep(1.5)
            print("Set Interrupt Pin back to Low!")
            last_seen_frame = frameCount
            #cv2.imwrite("imgs/Camera1 Right - " + str(frameCount) + ".png", frameR)
            break
        

capL.release()
capR.release()