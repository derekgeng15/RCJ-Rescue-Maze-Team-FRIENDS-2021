#pragma once

#include "Encoder.h"
#include <Wire.h>
#include <Arduino.h>
#include <MeMegaPi.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

#define WHEEL_DIAMETER 65
#define tickPerRev 368.0
#define encPerMm tickPerRev/(PI * WHEEL_DIAMETER)

class Chassis{
  private:
    MeMegaPiDCMotor _lMotor;
    MeMegaPiDCMotor _rMotor;
    
    Encoder _lEnc;
    Encoder _rEnc;
    
    Adafruit_BNO055 _imu;
    
    double yaw;
    int plEncCt, lEncCt;
    int prEncCt, rEncCt;
  public:
    Chassis();
    void init();
    double getYaw();
    int getlEncCt();
    int getrEncCt();
    uint8_t getREncInt();
    uint8_t getLEncInt();
    void updLEnc();
    void updREnc();
    bool turnTo(double deg);
    bool goMm(double mm);
    void reset();
    void readChassis();
    void print();
    void updateEnc();
    void runMotors(double power);
    void resetR();
  
};
