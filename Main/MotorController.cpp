#include "MotorController.h"
MotorController::MotorController(uint8_t p, uint8_t i, uint8_t n, int reversed):MeMegaPiDCMotor(p),port(p),intPin(i),NEPin(n){multi=((reversed)?-1:1);}
//void MotorController::run(int16_t s){speed=s * multi;MeMegaPiDCMotor::run(speed);} 
void MotorController::resetcount(){count=0;}
uint8_t MotorController::getIntPin(){return intPin;}
uint8_t MotorController::getNEPin(){return NEPin;}
int16_t MotorController::getSpeed(){return speed;}
