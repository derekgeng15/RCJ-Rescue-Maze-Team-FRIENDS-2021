#include "ArduinoMaze.h"


enum STATE{
  READING, FOLLOWING
}state;

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
