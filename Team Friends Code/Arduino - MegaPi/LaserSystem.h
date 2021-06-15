#pragma once

#include <Wire.h>
#include <VL53L0X.h>

//address we will assign if dual sensor is present
#define FRONT_LEFT_ADD 0x41
#define FRONT_RIGHT_ADD 0x40
#define MIDDLE_RIGHT_ADD 0x43
#define BACK_RIGHT_ADD 0x45
#define BACK_LEFT_ADD 0x44
#define MIDDLE_LEFT_ADD 0x42

//set the pins to shutdown
#define FRONTLEFT 28
#define FRONTRIGHT 29
#define RIGHTMID 27
#define RIGHTBACK 27
#define LEFTBACK 39
#define LEFTMID 26

#define NUM_OF_SENSORS 4

class LaserSystem{
  private:
    VL53L0X laser[NUM_OF_SENSORS];
    const int ID[NUM_OF_SENSORS] = {0x40, 0x43, 0x44, 0x42};
    const int shut[NUM_OF_SENSORS] = {28, 29, 26, 27};//, 39, 28};
    uint16_t dist[NUM_OF_SENSORS];
  public:
    void init();
    void readAll();
    void print();
    double getDist(int ID);
};
