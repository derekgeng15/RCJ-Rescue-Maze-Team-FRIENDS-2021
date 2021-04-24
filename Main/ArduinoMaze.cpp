#include "ArduinoMaze.h"

FSTATE fstate = CALC;
DIRECTION currDir;

Chassis *_chassis;
LaserSystem *_laser;
SA *_comm;

double threshold = 200;
double forward, angAdj;
String path;
int step, skip;
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
      skip = step + 1;
//      while(skip < path.length() && path[skip] == 'U')
//        skip++;
      fstate = TURNING;
      break;
    }
    case FSTATE::TURNING:{
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        _laser->read();
        angAdj = 0;
        double fe = TILE_SIZE;
        if(min(_laser->getDist(0), _laser->getDist(1)) < 8000)
            fe = fmod((min(_laser->getDist(0), _laser->getDist(1))), TILE_SIZE) + (TILE_SIZE)/2 + 82;
        if(_laser->getDist(2) < TILE_SIZE)
            angAdj =  -atan2(_laser->getDist(2) - TILE_SIZE/2 + 44, (skip - step - 1) * (TILE_SIZE) + fe) * 180 / PI;
        if(_laser->getDist(3) < TILE_SIZE)
            angAdj =  atan2(_laser->getDist(3) - TILE_SIZE/2 + 7, (skip - step - 1) * (TILE_SIZE) + fe) * 180 / PI;
        forward = ((skip - step - 1) * (TILE_SIZE) + fe) / cos(PI / 180 * angAdj) ;
        _laser->print();
        Serial.println(forward);
        Serial.println(angAdj);
        fstate  = TURNADJ;
      }
      break;
    }
    case FSTATE::TURNADJ:{
      if(_chassis->turnTo(ang[currDir] + angAdj)){
        _chassis->reset();
        fstate = FORWARD;
      }
      break;
    }
    case FSTATE::FORWARD:{
      if(_chassis->goMm(forward)){
        fstate = FORADJ;
      }
      break;
    }
    case FSTATE::FORADJ:{
      if(_chassis->turnTo(ang[currDir])){
        fstate = CALC;
        step = skip;
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
