#pragma once

#include <Wire.h>
#include <Adafruit_VL53L0X.h>
//address we will assign if dual sensor is present
#define FRONT_LEFT_ADD 0x41
#define FRONT_RIGHT_ADD 0x40
#define MIDDLE_RIGHT_ADD 0x43
#define BACK_RIGHT_ADD 0x45
#define BACK_LEFT_ADD 0x44
#define MIDDLE_LEFT_ADD 0x42

//set the pins to shutdown
#define FRONTLEFT 30
#define FRONTRIGHT 39
#define RIGHTMID 29
#define RIGHTBACK 27
#define LEFTBACK 39
#define LEFTMID 28

#define NUM_OF_SENSORS 4

class LaserSystem{
  private:
    //objects for the vl53l0x
    Adafruit_VL53L0X laser[NUM_OF_SENSORS];
    VL53L0X_RangingMeasurementData_t measure[NUM_OF_SENSORS];
    const int ID[NUM_OF_SENSORS] = {0x41, 0x40, 0x43, 0x45};//, 0x44, 0x42};
    const int shut[NUM_OF_SENSORS] = {30, 39, 29, 27};//, 39, 28};
    double dist[NUM_OF_SENSORS];
  public:
    void init();
    void read();
    void print();
    double getDist(int ID);
};
