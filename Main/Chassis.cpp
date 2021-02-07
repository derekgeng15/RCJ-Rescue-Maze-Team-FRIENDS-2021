#include "Chassis.h"

Chassis::Chassis():_imu(55, 0x28), _lEnc(18, 31, 1), _rEnc(19, 38, 0)
{
  //_imu = Adafruit_BNO055(55, 0x28);
  _lMotor = MeMegaPiDCMotor(PORT1B);
  _rMotor = MeMegaPiDCMotor(PORT2B);
  _lEnc = Encoder(18, 31, 0);
  _rEnc = Encoder(19, 38, 1);
}

void Chassis::init(){
  if(!_imu.begin(Adafruit_BNO055::OPERATION_MODE_IMUPLUS)){
    Serial.println("Cannot find BNO");
    while(1);
  }
  Serial.println("imu set");
  Serial.println("Motors set");

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
uint8_t Chassis::getLEncInt(){
  return _lEnc.getIntPin();
}
uint8_t Chassis::getREncInt(){
  return _rEnc.getIntPin();
}
void Chassis::updLEnc(){
  _lEnc.read();
}
void Chassis::updREnc(){
  _rEnc.read();
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
  static double kP = 0.8;
  static double kD = 0;
  if(lEncCt <= encPerMm * mm){
//    Serial.print(" lmotor power: ");
//    Serial.println((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD);
//    Serial.print(" rmotor power: ");
//    Serial.println((encPerMm * mm - rEncCt)  * kP + (rEncCt - prEncCt) * kD);
    _lMotor.run(((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD));
    _rMotor.run(-1*(encPerMm * mm - rEncCt)  * kP + (rEncCt - prEncCt) * kD);
//    Serial.println("RUNNING");
    return false;
  }
  else{
    _lMotor.run(0);
    _rMotor.run(0);
    Serial.println("DONE");
    delay(2000);
    return true;
  }
}
void Chassis::reset(){
  _lEnc.reset();
  _rEnc.reset();
  lEncCt = 0;
  rEncCt = 0;
}
void Chassis::read(){
  plEncCt = lEncCt;
  prEncCt = rEncCt;
  lEncCt = _lEnc.getCount();
  rEncCt = _rEnc.getCount();
  sensors_event_t imuData;
  _imu.getEvent(&imuData, Adafruit_BNO055::VECTOR_EULER);
  yaw =  imuData.orientation.x * PI / 180;
}
void Chassis::print(){
  Serial.print("lmm: ");
  Serial.print(lEncCt );
  Serial.print(" rmm: ");
  Serial.print(rEncCt );
  Serial.print(" Yaw: ");
  Serial.println(yaw * 180 / PI);
}
