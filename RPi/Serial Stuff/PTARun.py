import serial
import time

int_encode = b'2'
float_encode = b'42.3'
confirm ="Confirm\n"
#string1_encode = string1.encode()

#ser = serial.Serial('/dev/ttyAMA0', 9600)

ser = serial.Serial(
    port = '/dev/ttyAMA0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

counter = 0

while True:
    #ser.write(int_encode)
    direction = ""
    counter += 1
    if counter == 0:
        direction = "N"
    elif counter == 1:
        direction = "E"
    elif counter == 2:
        direction = "S"
    else:
        direction = "W"
        counter = -1
    ser.write((direction + "\n").encode())
    print("Printed: " + direction)
    done = False
    while not done:
        #print("Bytes in buff: " + str(ser.in_waiting))
        try:
            while(ser.in_waiting > 0): #if there's something in the buffer
        #    print("Reading:")
                print("Got confirmed:")
                x = ser.read_until("\n")
                print(x.decode("ascii"), end="\n")
                done = True
         #   print("Bytes in buff: " + str(ser.in_waiting))
        except IOError as e:
            print ("Something Bad Happened!")
            print(e)
        time.sleep(0.25)
'''while not (ser.in_waiting > 0):
    pass
print(ser.in_waiting)
x = ser.read()
print(x.decode("ascii"), end="")
if(x=="Confirm\n"):
    print("Done!")
else:
    print("NO!")
time.sleep(1)'''
