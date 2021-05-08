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
  checkVictim();
  switch(state){
    case STATE::READING:{
      readSensors();
   
      readTile();
      _comm->writeOut("Gib command");
      getPath();
      state = STATE::FOLLOWING;
      delay(500);
      break;
    }
    case STATE::FOLLOWING:{
      if(followPath())
        state = STATE::READING;
      break;
    }
  }
  //_laser->read();
  //print();
  //_chassis->turnTo(-90);
  
}
