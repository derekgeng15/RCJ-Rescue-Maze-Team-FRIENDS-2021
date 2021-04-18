#include "ArduinoMaze.h"

FSTATE fstate = TURNING;
DIRECTION currDir;

Chassis *_chassis;
LaserSystem *_laser;
SA *_comm;

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
  if(_laser->getDist(0) < threshold) {
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
    case FSTATE::CALC:{
      _lazer.read();
      double sE = 0, double fE = 330;
      if(_lazer.getDist(0) != -1)
        fE = fmod(_lazer.getDist(0), 300) + 150;
      if(_lazer.getDist(3) != -1 && _lazer.getDist(2) != -1)
        sE = _lazer.getDist(3) - _lazer.getDist(2);
      angAdj = atan2(sE, fE);
      forward = sqrt(fE * fE + sE * sE);
      fstate = TURNING;
      break;
    }
    case FSTATE::TURNING:{
      readSensors();
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4] + angAdj)){
        currDir = (currDir + getDir(path[step]))%4;
        fstate  = FORWARD;
        _chassis->reset();
      }
      break;
    }
    case FSTATE::FORWARD:{
      _chassis->updateEnc();
      if(_chassis->goMm(forward)){
        fstate = ADJ;
      }
      break;
    }
    case FSTATE::ADJ{
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        fstate = CALC;
        step++;
        _chassis->reset();
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
