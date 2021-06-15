/*
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
   comm.writeOut("1001");
   delay(50);
   comm.writeOut("GET MOVE");
   delay(50);
  //ONLY UNCOMMENT THIS if you want to read in stuff (reading in integers)
  //int msg = (comm.readIn()).toInt();
  //Serial.println("Returned: " + String(msg));
  
  //ONLY UNCOMMENT THIS if you want to read in stuff (reading in strings)
  Serial.println("Returned: " + comm.readIn());
  while(1);
  delay(500);
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

#include <Wire.h>
#include "ArduinoMaze.h"
#include <MeMegaPi.h>
#include "SerialArduino.h"
#include <String.h>

SA comm;

enum STATE{
  READING, FOLLOWING
}state;

void test(String p){
  path = p;
  if(followPath()){
      Serial.print("DONE");
      while(1);
  }
}

void setup()
{
  
 begin();
}
void loop()
{
  readSensors();
  String walls = "";
  if(_laser->getDist(0) < 100) {
    Serial.println(_laser->getDist(0));
    walls+="1";
    Serial.println("First Sensor Seen");
  }
  else
    walls+="0";
  if(_laser->getDist(3) < 100) {
    Serial.println("Second Sensor Seen");
    walls+="1";
  }
  else
    walls+="0";
  walls+="0";
  if(_laser->getDist(2) < 100) {
    Serial.println("Third Sensor Seen");
    walls+="1";
  }
  else
    walls+="0";
  
  comm.writeOut(walls);
   delay(50);
   comm.writeOut("GET MOVE");
   delay(50);
  //ONLY UNCOMMENT THIS if you want to read in stuff (reading in integers)
  //int msg = (comm.readIn()).toInt();
  //Serial.println("Returned: " + String(msg));
  
  //ONLY UNCOMMENT THIS if you want to read in stuff (reading in strings)
  Serial.println("Returned: " + comm.readIn());
  while(1);
  delay(500);
//  switch(state){
//    case STATE::READING:{
//      readTile();
//      getPath();
//      state = STATE::FOLLOWING;
//      break;
//    }
//    case STATE::FOLLOWING:{
//      if(followPath())
//        state = STATE::READING;
//      break;
//    }
//  }
  //print();
  //_chassis->print();
  
  //_chassis->getLeftMotor()->run(100);
  //_chassis->getRightMotor()->run(100);
  //_chassis->goMm(300);
  print();
  //_chassis->turnTo(-90);
  //test("URL");
}
*/
