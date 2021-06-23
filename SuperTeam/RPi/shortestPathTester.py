from nav import Nav

import time
import math
import struct
import numpy as np

def clearFile():
        print("Clearing file!")
        filePtr = open('wall.txt', 'w+')
        filePtr.truncate(0)
        filePtr.write("20 20 V\n")
        filePtr.close()


coordinateDictionary = {(20, 20) : 1, (19, 20) : 2, (18, 20) : None, (17, 20) : 3,
                            (17, 19) : None, (17, 18) : 9, (17, 17): 12, (18, 17) : 11,
                            (19, 17) : 10, (20, 17) : None, (20, 18) : 6, (20, 19) : 4,
                            (19, 19) : 5, (18, 19) : None, (18, 18) : 8, (19, 18) : 7}

clearFile()

AI = Nav(readInWall=True)

'''AI.markWall(2, writeToFile=False)

print(AI.calculatePath((20,20), (17,17), 0))'''

AI.markWall(0, writeToFile=False)
AI.markWall(1, writeToFile=False)
AI.markWall(3, writeToFile=False)
AI.markWall(1, loc=(19, 17), writeToFile=False)
AI.markWall(0, loc=(17, 18), writeToFile=False)

Hcoord = (17, 18)
Ycoord = (19, 17)
Hside = 2
Yside = 3

print("Hcoord:", Hcoord)
print("Hside:", Hside)
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