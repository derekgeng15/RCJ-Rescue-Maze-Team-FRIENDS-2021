#pragma once
  //#ifndef SerialArduino_h
//#define SerialArduino_h
#include <Arduino.h>
#include <Wire.h>



class SA{


  private:  
    String buff;
    //Direction getDir();
    
    
    
  public:
    void writeSerial(String x);
    //SA();
    String readIn();
    void writeConfirm();
    void readConfirm();
    String readSerial();
    void writeOut(String x);
};
