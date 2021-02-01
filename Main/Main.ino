#include "ArduinoMaze.h"
#include <MeMegaPi.h>


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
  _chassis->print();
  
  //_chassis->getLeftMotor()->run(100);
  //_chassis->getRightMotor()->run(100);
  //_chassis->goMm(300);
}
