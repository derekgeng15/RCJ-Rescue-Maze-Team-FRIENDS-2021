import serial
import struct
import time
import numpy as np

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

def in_waiting():
    return ser.in_waiting

# Just waits for buffer to be availble, and then reads it in
def read():
    done = False
    print("Waiting...")
    while not done:
        try:
            while(ser.in_waiting == 0): #if there's something in the buffer
                pass
            #print("Size: " + str( ser.in_waiting))
            x = ser.read_until("\n")
            msg = x.decode('ascii')
            print("Got: \"", msg, "\" from arduino", end="\n")
            done = True
            # print("Bytes in buff: " + str(ser.in_waiting))
        except IOError as e:
            print ("Something Bad Happened!")
            print(e)
        time.sleep(0.05)
    #ser.flush()
    return msg

# Just writes a message to arduino
def write(msg):
    ser.write((msg+"\n").encode())
    #ser.flush()
    print("Wrote:\"", msg, "\" to arduino")

# Read and then write a confirm message
def readIn():
    msg = read()
    write("Confirm\n")
    print("Sent Confirmation Message!")
    return msg

# Write and then read a confirm message
def writeOut(msg):
    write(msg)
    confimration = read()
    print("Recieved Confimration Message!")
