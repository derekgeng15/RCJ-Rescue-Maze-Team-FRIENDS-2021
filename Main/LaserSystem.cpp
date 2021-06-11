#include "LaserSystem.h"
void LaserSystem::init(){
  for(int i = 0; i < NUM_OF_SENSORS; i++)
    pinMode(shut[i], OUTPUT);
  Serial.println("Shutdown pins inited...");
  for(int i = 0; i < NUM_OF_SENSORS; i++)
    digitalWrite(shut[i], LOW);
  delay(10);
  // all unreset
  for(int i = 0; i < NUM_OF_SENSORS; i++)
    digitalWrite(shut[i], HIGH);
  delay(10);
  
  for(int i = 1; i < NUM_OF_SENSORS; i++)
    digitalWrite(shut[i], LOW);
  for(int i = 0; i < NUM_OF_SENSORS; i++){
    digitalWrite(shut[i], HIGH);
    //ADAFRUIT
    // if(!laser[i].begin(ID[i])){
    //   Serial.print("Failed to Boot ");
    //   Serial.println(i);
    //   while(1)
    //     ;
    // }
    //POLOLU
    laser[i].setTimeout(500);
    if(!laser[i].init()){
      Serial.print("Failed to Boot ");
      Serial.println(i);
      while(1)
        ;
    }
    laser[i].setAddress(ID[i]);
    laser[i].startContinuous();
    delay(10);
  }
  Serial.println("IDs set");
}
double LaserSystem::getDist(int ID){
  return dist[ID];
}

void LaserSystem::readAll(){
//    Serial.println("READING LASERS");
    for(int i = 0; i < NUM_OF_SENSORS; i++){
      //ADAFRUIT
      // laser[i].rangingTest(&measure[i], false);
      // dist[i] = -1;
      // dist[i] = measure[i].RangeMilliMeter;
      // POLOLU
      dist[i] = laser[i].readRangeContinuousMillimeters();
      // dist[i] = laser[i].readRangeSingleMillimeters();
      if(laser[i].timeoutOccurred()){
        Serial.print("Laser timeout:");
        Serial.println(i);
        dist[i] = -1;
      }
    }
}
void LaserSystem::print(){
  for(int i = 0; i < NUM_OF_SENSORS; i++){
    Serial.print("l");
    Serial.print(i);
    Serial.print(":");
    Serial.print(dist[i]);
    Serial.print("  ");
  }
  Serial.println();
}
