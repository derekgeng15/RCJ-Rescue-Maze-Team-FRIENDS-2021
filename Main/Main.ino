#include "ArduinoMaze.h"

enum STATE{
  READING, FOLLOWING
}state;

void stepState(){
  switch(state){
    case STATE::READING:{
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
  //print();
  _chassis->print();
  _chassis->goMm(300);
}
