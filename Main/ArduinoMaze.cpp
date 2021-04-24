#include "ArduinoMaze.h"

FSTATE fstate = TURNING;
DIRECTION currDir;

Chassis *_chassis;
LaserSystem *_laser;
SA *_comm;
IRTherm therm1;
IRTherm therm2;

double threshold = 200;
String path;
int step;
void lMotorEncInterrupt()
{
  _chassis->updLEnc();
}
void rMotorEncInterrupt()
{
  _chassis->updREnc();
}
DIRECTION getDir(char c){
  switch(c){
    case 'U':
      return UP;
    case 'R':
      return RIGHT;
    case 'D':
      return DOWN;
    case 'L':
      return LEFT;
  }
}
void begin(){
  _chassis = new Chassis();
  _laser = new LaserSystem();
  _comm = new SA();
  Serial.begin(115200);
  Serial2.begin(9600);
  while (!Serial)
    delay(1);
  Serial.println("Begin!");
  Wire.begin();
  _chassis->init();
  _chassis->reset();
  _laser->init();
  if (therm1.begin(0x5a) == false) {
    Serial.println("Qwiic IR thermometer 1 did not acknowledge! Running I2C scanner.");
    while(1);
  }
  if (therm2.begin(0x5b) == false) {
    Serial.println("Qwiic IR thermometer 2 did not acknowledge! Running I2C scanner.");
    while(1);
  }
  therm1.setUnit(TEMP_F);
  therm2.setUnit(TEMP_F);
  Serial.println("Finished therms");
  attachInterrupt(digitalPinToInterrupt(_chassis->getLEncInt()), lMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(_chassis->getREncInt()), rMotorEncInterrupt, RISING);
  delay(2000);
}
void readSensors(){//read all sensors
  _chassis->read();
  //_laser->read();  
}
void print(){
  Serial.println("--------------------");
  _chassis->print();
  _laser->print();
  Serial.println("--------------------");
}
void readTile(){//read Tile data and send to PI
  String walls = ""; //Front, Right, Back, Left (Clockwise)
  _laser->read();
  Serial.print(_laser->getDist(1));
  Serial.print(" ");
  Serial.print(_laser->getDist(3));
  Serial.print(" ");
  Serial.print(_laser->getDist(2));
  Serial.println(" ");
  if(_laser->getDist(1) < threshold) {
    walls+="1";
    Serial.println("First Sensor Seen");
  }
  else
    walls+="0";
  if(_laser->getDist(3) < threshold) {
    Serial.println("Second Sensor Seen");
    walls+="1";
  }
  else
    walls+="0";
  walls+="0";
  if(_laser->getDist(2) < threshold) {
    Serial.println("Third Sensor Seen");
    walls+="1";
  }
  else
    walls+="0";
  _comm->writeOut(walls);
}

void getPath(){//get BFS path from PI
  path = _comm->readIn();
  step = 0;
}

bool followPath(){//TODO: Add state machine for following
  /*
       * if see black, call ai blackout(rPI serial)
       * 
       */
  //readSensors();
  switch(fstate){
    case FSTATE::TURNING:{
      readSensors();
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        fstate  = FORWARD;
        _chassis->reset();
      }
      break;
    }
    case FSTATE::FORWARD:{
      _chassis->updateEnc();
      if(therm1.read()) {
        Serial.print("Temp 1: ");
        Serial.print(String(therm1.object(), 2));
      }
      if(therm2.read()) {
        Serial.print(" Temp 2: ");
        Serial.println(String(therm2.object(), 2));
      }
      if(_chassis->goMm(330)){
        step++;
        fstate = TURNING;
        if(step == path.length())
          return true;
      }
      break;
    }
//    case FSTATE::BLACKTILE{
//      chassis.goto(0);
//    }
  }
  return false;
}
