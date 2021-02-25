
import time
import serial
ser = serial.Serial(
    port = '/dev/ttyAMA0',
    baudrate = 9600)
'''    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1'''
#)


while True:
    #print("Bytes in buff: " + str(ser.in_waiting))
    try:
        while(ser.in_waiting > 0): #if there's something in the buffer
    #    print("Reading:")
            x = ser.read()
            print(x.decode("ascii"), end="")
     #   print("Bytes in buff: " + str(ser.in_waiting))
    except IOError as e:
        print ("Something Bad Happened!")
        print(e)
    time.sleep(0.25)

#ser.flush()