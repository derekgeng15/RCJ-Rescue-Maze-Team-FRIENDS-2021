#include "Chassis.h"

Chassis::Chassis():_imu(55, 0x28), _lEnc(18, 31, 1), _rEnc(19, 38, 0)
{
  //_imu = Adafruit_BNO055(55, 0x28);
  _lMotor = MeMegaPiDCMotor(PORT1B);
  _rMotor = MeMegaPiDCMotor(PORT2B);
  _lEnc = Encoder(18, 31, 1);
  _rEnc = Encoder(19, 38, 0);
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
double totalErr = 0;
bool Chassis::turnTo(double deg){
  static double kP = 3.2;
  double kI = 0.02;
//  double totalError = 0;
  double error = deg - (yaw * 180 / PI);
  if(error > 180)
    error = 360 - error;
  else if(error < -180)
    error += 360;
  totalErr+=error;
  Serial.print("ERROR: ");
  Serial.println(error);
  if(abs(error) > 1){
    Serial.println("Moving");
    _rMotor.run(error * kP + (totalErr*kI));
    _lMotor.run(error * kP + (totalErr*kI));
    return false;
  }
  else{
    Serial.println("Done Turning");
    _rMotor.run(0);
    _lMotor.run(0);
    totalErr = 0;
    return true;
  }
}
double lTotalErr = 0;
double rTotalErr = 0;
bool Chassis::goMm(double mm){
  static double kP = 1.2;
  static double kD = 0;
  double kI = 0.001;
  lTotalErr+=(encPerMm * mm - lEncCt);
  rTotalErr+=(encPerMm * mm - rEncCt);
  if(lEncCt <= encPerMm * mm){
//    Serial.print(" lmotor power: ");
//    Serial.println((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD);
//    Serial.print(" rmotor power: ");
//    Serial.println((encPerMm * mm - rEncCt)  * kP + (rEncCt - prEncCt) * kD);
    _lMotor.run(-1*(((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD) + (lTotalErr*kI)));
    _rMotor.run((encPerMm * mm - rEncCt)  * kP + (rEncCt - prEncCt) * kD + (rTotalErr*kI));
//    Serial.println("RUNNING");
    return false;
  }
  else{
    _lMotor.run(0);
    _rMotor.run(0);
    Serial.println("DONE");
    lTotalErr = 0;
    rTotalErr = 0;
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
