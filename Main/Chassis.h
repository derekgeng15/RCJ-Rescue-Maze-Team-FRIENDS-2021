#include "MotorController.h"
#include <Wire.h>
#include <Arduino.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

class Chassis{
  private:
    Adafruit_BNO055 _imu;
    MotorController _rMotor;
    MotorController _lMotor;
    double yaw;
    int plEncCt, lEncCt;
    int prEncCt, rEncCt;
  public:
    Chassis();
    void init();
    MotorController getLeftMotor();
    MotorController getRightMotor();
    double getYaw();
    int getlEncCt();
    int getrEncCt();
    bool turnTo(double deg);
    bool goCm(double cm);
    void resetEncoderCt();
    void read();
  
};
