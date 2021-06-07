#include "Chassis.h"

double counter = 0;
double lSpeed = 0;
double rSpeed = 0;

Chassis::Chassis():_imu(55, 0x28)//, _lEnc(18, 31, 1), _rEnc(19, 38, 0)
{
  //_imu = Adafruit_BNO055(55, 0x28);
  _lMotor = MeMegaPiDCMotor(PORT1B);
  _rMotor = MeMegaPiDCMotor(PORT2B);
  _lEnc = Encoder(18, 31, 1);
  _rEnc = Encoder(19, 38, 0);
}

void Chassis::init(){
  Serial.println("Starting bno");
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
double Chassis::getPitch(){
  return pitch;
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
  if(lSpeed<0)
    _lEnc.read(true);
  else
    _lEnc.read(false);
}
void Chassis::updREnc(){
  if(rSpeed<0)
    _rEnc.read(true);
  else
    _rEnc.read(false);
}

bool Chassis::turnTo(double deg){
  static double kP = 1.0;
  static double totalErr = 0;
  double kI = 0.0075;
  double error = deg - (yaw * 180 / PI);
  //Serial.println((yaw * 180 / PI));
  if(error > 180)
    error = 360 - error;
  else if(error < -180)
    error += 360;
  if(abs(error) < 90) 
   totalErr+=error;
  if(error * kP + (totalErr*kI) < 0) {
     lSpeed = min(error * kP + (totalErr*kI), -50);
     rSpeed = min(error * kP + (totalErr*kI), -50);
  }
  else {
    lSpeed = max(error * kP + (totalErr*kI), 50);
    rSpeed = max(error * kP + (totalErr*kI), 50);
  }
  
  if(abs(error) > 1){
    _rMotor.run(lSpeed);
    _lMotor.run(rSpeed);
    counter++;
    return false;
  }
  else{
    Serial.println("Done Turning");
    Serial.print("TURN COUNT: ");
    Serial.println(counter);
    _rMotor.run(0);
    _lMotor.run(0);
    totalErr = 0;
    counter=0;
    return true;
  }
}

double lTotalErr = 0;
double rTotalErr = 0;
bool Chassis::goMm(double mm){
  static double kP = 0.25;
  static double kD = 0;
  double kI = 0.001;
  double speed;
  //Serial.println(lEncCt);
  lTotalErr+=(encPerMm * mm - lEncCt);
  //rTotalErr+=(encPerMm * mm - rEncCt);
  if(abs(lEncCt - (encPerMm * mm))>9){
    if((((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD) + (lTotalErr*kI))<0) {
      speed = min((((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD) + (lTotalErr*kI)), -30);
    }
    else {
      speed = max((((encPerMm * mm - lEncCt)  * kP + (lEncCt - plEncCt) * kD) + (lTotalErr*kI)), 30);
    }
    lSpeed = -1*speed;
    rSpeed = speed;
    _lMotor.run(lSpeed);
    _rMotor.run(rSpeed);
//    Serial.println("RUNNING");
    counter++;
    return false;
  }
  else{
    _lMotor.run(0);
    _rMotor.run(0);
    Serial.print("COUNT: ");
    Serial.println(counter);
    Serial.println("DONE");
    lTotalErr = 0;
    rTotalErr = 0;
    counter = 0;
    return true;
  }
}
void Chassis::reset(){
  _lEnc.reset();
  lEncCt = 0;
}

void Chassis::resetR() {
  _rEnc.reset();
  rEncCt = 0;
}

void Chassis::updateEnc() {
  plEncCt = lEncCt;
  prEncCt = rEncCt;
  lEncCt = _lEnc.getCount();
  rEncCt = _rEnc.getCount();
}
void Chassis::readChassis(){
  plEncCt = lEncCt;
  prEncCt = rEncCt;
  lEncCt = _lEnc.getCount();
  rEncCt = _rEnc.getCount();
  sensors_event_t imuData;
  _imu.getEvent(&imuData, Adafruit_BNO055::VECTOR_EULER);
  yaw =  imuData.orientation.x * PI / 180;
  pitch = imuData.orientation.z * PI / 180;
}
void Chassis::print(){
  Serial.print("lmm: ");
  Serial.print(lEncCt );
  Serial.print(" rmm: ");
  Serial.print(rEncCt );
  Serial.print(" Yaw: ");
  Serial.println(yaw * 180 / PI);
  Serial.print("pitch: ");
  Serial.println(pitch * 180 / PI);
}

void Chassis::runMotors(double power) {
  _lMotor.run(power);
  _rMotor.run(-1*power);
}

void Chassis::setCount(int l, int r){
  _lEnc.setCount(l);
  _rEnc.setCount(r);
}
