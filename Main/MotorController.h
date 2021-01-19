#pragma once
#include <MeMegaPi.h>
#define WHEEL_DIAMETER 65
#define tickPerRev 368.0
#define encPerMm tickPerRev/(PI * WHEEL_DIAMETER)
class MotorController: public MeMegaPiDCMotor {
  private:
    volatile uint8_t port;
    volatile uint8_t intPin;
    volatile uint8_t NEPin;
    volatile int16_t speed;
  public:
    volatile int8_t multi;
    volatile int16_t count;
    MotorController(uint8_t p, uint8_t i, uint8_t n, int reversed);   // constructor
    void init();
    void run(int16_t s);
    void resetcount();
    uint8_t getIntPin();
    uint8_t getNEPin();
    int16_t getSpeed();
};
