#include <Wire.h>
//#include "MotorController.h"
#include "Adafruit_VL53L0X.h"
#include "SerialArduino.h"
#include <String.h>

SA comm;

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial2.begin(9600);
  while (!Serial)
  {
    delay(1);
  }
  Serial.println("Begin!");
}

void loop()
{
  //getDir();
  //ONLY UNCOMMENT THIS if you want to write stuff out
  // comm.writeOut("5");

  //ONLY UNCOMMENT THIS if you want to read in stuff (reading in integers)
  //int msg = (comm.readIn()).toInt();
  //Serial.println("Returned: " + String(msg));
  
  //ONLY UNCOMMENT THIS if you want to read in stuff (reading in strings)
  Serial.println("Returned: " + comm.readIn());
  
  delay(500);
}
