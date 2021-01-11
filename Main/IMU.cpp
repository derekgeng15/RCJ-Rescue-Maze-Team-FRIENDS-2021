#include "IMU.h"

IMU::IMU(int8_t id, int8_t add):Adafruit_BNO055(ID, add),ID(id),address(add){

}
int IMU::init(){
    if(!begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS)){
    Serial.println("Cannot find BNO");
    while(1);
  }
}
double IMU::getYaw(){
  sensors_event_t imuData;
  getEvent(&imuData, Adafruit_BNO055::VECTOR_EULER);
  return imuData.orientation.x * PI / 180;
}
