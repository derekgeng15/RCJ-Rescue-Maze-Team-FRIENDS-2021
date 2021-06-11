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

clearFile()

AI = Nav(readInWall=True)

commands = AI.calculate()

AI.markWall()