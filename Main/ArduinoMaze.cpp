#include "ArduinoMaze.h"
#include "A"

Chassis * _chassis;
LazerSystem * _lazer;
SA comm;

String path;

void lMotorEncInterrupt()
{
  (digitalRead(_chassis->getLeftMotor().getNEPin())) ? (_chassis->getLeftMotor().count -= _chassis->getLeftMotor().multi) : (_chassis->getLeftMotor().count += _chassis->getLeftMotor().multi);
}
void rMotorEncInterrupt()
{
  (digitalRead(_chassis->getRightMotor().getNEPin())) ? (_chassis->getRightMotor().count -= _chassis->getRightMotor().multi) : (_chassis->getRightMotor().count += _chassis->getRightMotor().multi);
}

void begin(){
  _chassis = new Chassis();
  _lazer = new LazerSystem();
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
  int laserDistances[6];
  for(int i = 0; i < 6; i++){
    laserDistances[i] = _lazer->getDist(i);
  }
}

void getPath(){//get BFS path from PI
  path = comm.readIn();
}
bool followPath(){//TODO: Add state machine for following
  return false;
}
