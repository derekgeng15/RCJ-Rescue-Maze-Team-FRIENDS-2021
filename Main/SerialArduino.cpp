#include "SerialArduino.h"

/*SA::SA(){
}*/
//Direction SA::getDir()
//{
//  Serial.println("Waiting for direction:");
//  while(!Serial2.available());
//    buff = Serial2.readStringUntil('\n');
//    Serial.println(buff);
//    char res = buff[0];
//    if(res=='N')
//      return Direction::NORTH;
//    if(res=='E')
//      return Direction::EAST;
//    if(res=='S')
//      return Direction::SOUTH;
//    if(res=='W')
//      return Direction::WEST;
//}

String SA::readSerial(){
  Serial.println("Waiting for message");
  while(!Serial2.available());
  buff = Serial2.readStringUntil('\n');
  Serial.println("Recieved: " + buff);
  return buff;
}

void SA::writeConfirm(){
  Serial2.println("Confirm");
}

void SA::writeSerial(String x)
{
  Serial2.println(x);
  Serial.println(x);
}

void SA::readConfirm(){
  Serial.println("Waiting for confirmation:");
  while(!Serial2.available());
  buff = Serial2.readStringUntil('\n');
  Serial.println("Recieved: " + buff);
  if(buff=="Confirm")
    Serial.println("Confirmed");
  else
    Serial.println("Got something but recieved a confirm return");
}

String SA::readIn()
{
  String ret = readSerial();
  delay(5);
  writeConfirm();
  delay(5);
  return ret;
}

void SA::writeOut(String x)
{
 writeSerial(x);
 delay(5);
 readConfirm();
 delay(5); 
}
