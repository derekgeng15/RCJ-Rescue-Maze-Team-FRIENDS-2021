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

AI.markWall(0, writeToFile=False)
AI.markWall(1, writeToFile=False)
AI.markWall(3, writeToFile=False)

commands = AI.calculate()

print("Current Location:", AI.getLocation())
print("Previous Location:", AI.getPrevLocation())
print("Current Direction:", AI.getDirection())
print("Print Right:", (AI.getDirection()+1)%4)
print("Print Left:", (AI.getDirection()+3)%4)


commands = AI.calculate()

print("Current Location:", AI.getLocation())
print("Previous Location:", AI.getPrevLocation())
print("Current Direction:", AI.getDirection())
print("Print Right:", (AI.getDirection()+1)%4)
print("Print Left:", (AI.getDirection()+3)%4)

commands = AI.calculate()

print("Current Location:", AI.getLocation())
print("Previous Location:", AI.getPrevLocation())
print("Current Direction:", AI.getDirection())
print("Print Right:", (AI.getDirection()+1)%4)
print("Print Left:", (AI.getDirection()+3)%4)

print("Tile Number", coordinateDictionary[AI.getLocation()])

AI.markWall(2, writeToFile = False)

commands = AI.calculate()

print("Current Location:", AI.getLocation())
print("Previous Location:", AI.getPrevLocation())
print("Current Direction:", AI.getDirection())
print("Print Right:", (AI.getDirection()+1)%4)
print("Print Left:", (AI.getDirection()+3)%4)
