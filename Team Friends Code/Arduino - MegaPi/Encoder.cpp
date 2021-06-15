#include "Encoder.h"

Encoder::Encoder(){};
Encoder::Encoder(uint8_t i, uint8_t n, int reversed):intPin(i),NEPin(n){multi=((reversed)?-1:1);pinMode(NEPin,INPUT);}
void Encoder::reset(){count=0;}
void Encoder::read(bool backwards){backwards ? (count -= multi) : (count += multi);}
int Encoder::getCount(){return count;}
void Encoder::setCount(int ct){count = ct;}
uint8_t Encoder::getIntPin(){return intPin;}
uint8_t Encoder::getNEPin(){return NEPin;}
