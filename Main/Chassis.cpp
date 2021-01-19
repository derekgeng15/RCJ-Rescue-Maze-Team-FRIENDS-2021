#include "Chassis.h"
Chassis::Chassis(): _imu(55, 0x28),_rMotor(PORT1B, 18, 31, 1),_lMotor(PORT2B, 19, 38, 0){
}

void Chassis::init(){
  if(!_imu.begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS)){
    Serial.println("Cannot find BNO");
    while(1);
  }
  Serial.println("imu set");

  Serial.println("Motors set");
}
MotorController Chassis::getLeftMotor(){
  return _lMotor;
}
MotorController Chassis::getRightMotor(){
  return _rMotor;
}
    
double Chassis::getYaw(){
  return yaw;
}
int Chassis::getlEncCt(){
  return lEncCt;
}
int Chassis::getrEncCt(){
  return rEncCt;
}

bool Chassis::turnTo(double deg){
  static double kP = 3.2;
//  double kI = 0.003;
//  double totalError = 0;
  double error = deg - yaw;
  if(error > PI)
    error = 2 * PI - error;
  else if(error < -PI)
    error += 2 * PI;
  if(error > 1){
    _rMotor.run(-error * kP);
    _lMotor.run(error * kP);
    return false;
  }
  else{
    _rMotor.run(0);
    _lMotor.run(0);
    return true;
  }
}
bool Chassis::goMm(double mm){
  static double kP = 0.2;
  static double kD = 0;
  if(lEncCt <= encPerMm * mm){
    _lMotor.run((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD);
    _rMotor.run((encPerMm * mm - rEncCt)  * kP + (rEncCt - prEncCt) * kD);
    return false;
  }
  else{
    _lMotor.run(0);
    _rMotor.run(0);
    return true;
  }
}
void Chassis::reset(){
  _lMotor.count = 0;
  _rMotor.count = 0;
  lEncCt = 0;
  rEncCt = 0;
}
void Chassis::read(){
  plEncCt = lEncCt;
  prEncCt = rEncCt;
  lEncCt = _lMotor.count;
  rEncCt = _rMotor.count;
  sensors_event_t imuData;
  _imu.getEvent(&imuData, Adafruit_BNO055::VECTOR_EULER);
  yaw =  imuData.orientation.x * PI / 180;
}
void Chassis::print(){
  Serial.print("lmm:");
  Serial.print(lEncCt * encPerMm);
  Serial.print(" rmm:");
  Serial.println(rEncCt * encPerMm);
  Serial.print("Yaw:");
  Serial.println(yaw * 180 / PI);
}
