import serial
import time

int_encode = b'2'
float_encode = b'42.3'
string1 = "Hello Friends! 28398\n"
string1_encode = string1.encode()

#ser = serial.Serial('/dev/ttyAMA0', 9600)

ser = serial.Serial(
    port = '/dev/ttyAMA0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

while 1:
    #ser.write(int_encode)
    ser.write(string1_encode)
    time.sleep(1)