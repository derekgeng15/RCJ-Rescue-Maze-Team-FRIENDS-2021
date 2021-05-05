#pragma once
  //#ifndef SerialArduino_h
//#define SerialArduino_h
#include <Arduino.h>
#include <Wire.h>



class SA{


  private:  
    String buff;
    //Direction getDir();
    void writeConfirm();
    void writeSerial(String x);
    void readConfirm();
  public:
    //SA();
    String readIn();
    String readSerial();
    void writeOut(String x);
};
