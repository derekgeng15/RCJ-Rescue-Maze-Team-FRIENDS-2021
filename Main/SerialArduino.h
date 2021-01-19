#pragma once
  //#ifndef SerialArduino_h
//#define SerialArduino_h
#include <Arduino.h>
#include <Wire.h>


enum Direction
{
  NORTH,
  EAST,
  SOUTH,
  WEST
};

class SA{


  private:  
    String buff;
    String readSerial();
    //Direction getDir();
    void writeConfirm();
    void writeSerial(String x);
    void readConfirm();
  public:
    //SA();
    String readIn();
    void writeOut(String x);
};
