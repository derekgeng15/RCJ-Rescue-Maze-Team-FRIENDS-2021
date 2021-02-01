#include "Encoder.h"
Encoder::Encoder(){};
Encoder::Encoder(uint8_t i, uint8_t n, int reversed):intPin(i),NEPin(n){multi=((reversed)?-1:1);}
void Encoder::reset(){count=0;}
void Encoder::read(){digitalRead(NEPin) ? (count -= multi) : (count += multi);}
int Encoder::getCount(){return count;}
uint8_t Encoder::getIntPin(){return intPin;}
uint8_t Encoder::getNEPin(){return NEPin;}
