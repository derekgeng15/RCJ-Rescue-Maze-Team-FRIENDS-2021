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
  switch(state){
    case STATE::READING:{
      readTile();
      _comm->writeOut("Gib command");
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
  //print();
  //_chassis->turnTo(-90);
  //test("URL");
}
