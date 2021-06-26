//Regular
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
// _laser->readAll();
}
void loop()
{
  

  readSensors();
//  test("FF");
  checkVictim();
  prevFunc();
  switch(state){
    case STATE::READING:{
//      readSensors();
      readTile();
      getPath();
      state = STATE::FOLLOWING;
      break;
    }
    case STATE::FOLLOWING:{
      if(followPath())
        state = STATE::READING;
      break;
    }
  }
  
}
