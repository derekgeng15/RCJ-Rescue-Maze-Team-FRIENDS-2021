#include "ArduinoMaze.h"

FSTATE fstate = TURNING;
DIRECTION currDir;

Chassis *_chassis;
LaserSystem *_laser;
SA *_comm;

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
  attachInterrupt(digitalPinToInterrupt(_chassis->getLEncInt()), lMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(_chassis->getREncInt()), rMotorEncInterrupt, RISING);
  delay(2000);
}
void readSensors(){//read all sensors
  _chassis->read();
  _laser->read();  
}
void print(){
  Serial.println("--------------------");
  _chassis->print();
  _laser->print();
  Serial.println("--------------------");
}
void readTile(){//read Tile data and send to PI
  String walls = ""; //Front, Right, Back, Left (Clockwise)
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
  switch(fstate){
    case FSTATE::TURNING:{
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        fstate  = FORWARD;
        _chassis->reset();
      }
      break;
    }
    case FSTATE::FORWARD:{
      
      if(_chassis->goMm(300)){
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
