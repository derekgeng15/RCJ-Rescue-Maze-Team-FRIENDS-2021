#include "ArduinoMaze.h"

FSTATE fstate;
DIRECTION currDir;

Chassis *_chassis;
LazerSystem *_lazer;
SA *_comm;

String path;
int step;
void lMotorEncInterrupt()
{
  (digitalRead(_chassis->getLeftMotor().getNEPin())) ? (_chassis->getLeftMotor().count -= _chassis->getLeftMotor().multi) : (_chassis->getLeftMotor().count += _chassis->getLeftMotor().multi);
}
void rMotorEncInterrupt()
{
  (digitalRead(_chassis->getRightMotor().getNEPin())) ? (_chassis->getRightMotor().count -= _chassis->getRightMotor().multi) : (_chassis->getRightMotor().count += _chassis->getRightMotor().multi);
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
  _lazer = new LazerSystem();
  _comm = new SA();
  Serial.begin(115200);
  Serial2.begin(9600);
  while (!Serial)
    delay(1);
  Serial.println("Begin!");
  Wire.begin();
  _chassis->init();
  _lazer->init();
  attachInterrupt(digitalPinToInterrupt(_chassis->getLeftMotor().getIntPin()), lMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(_chassis->getRightMotor().getIntPin()), rMotorEncInterrupt, RISING);
  delay(2000);
}
void readSensors(){//read all sensors
  _chassis->read();
  _lazer->read();  
}
void readTile(){//read Tile data and send to PI
  String walls = "FFFF"; //Front, Right, Back, Left (Clockwise)
  for(int i = 0; i < 4; i++){
    if(_lazer->getDist(i) < 300 && _lazer->getDist(i*2) < 300){
      i+=(i == 2);
      walls[i] = 'T';
    }
  }
  _comm->writeOut(walls);
}

void getPath(){//get BFS path from PI
  String path = _comm->readIn();
  step = 0;
}
bool followPath(){//TODO: Add state machine for following
  switch(fstate){
    case FSTATE::TURNING:{
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        fstate  = FORWARD;
      }
      break;
    }
    case FSTATE::FORWARD:{
      if(_chassis->goCm(30)){
        step++;
        fstate = TURNING;
        if(step == path.length())
          return true;
      }
      break;
    }
  }
  return false;
}
