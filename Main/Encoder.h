#pragma once
#include <Arduino.h>
class Encoder {
  private:
    volatile uint8_t intPin;
    volatile uint8_t NEPin;
  public:
    volatile int8_t multi;
    volatile int16_t count;
    Encoder();
    Encoder(uint8_t i, uint8_t n, int reversed);   // constructor
    void read();
    void reset();
    int getCount();
    uint8_t getIntPin();
    uint8_t getNEPin();
};
