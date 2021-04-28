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
    if(!laser[i].begin(ID[i])){
      Serial.print("Failed to Boot ");
      Serial.println(i);
      while(1)
        ;
    }
    delay(10);
  }
  Serial.println("IDs set");
}
double LaserSystem::getDist(int ID){
  return dist[ID];
}

void LaserSystem::readAll(){
    Serial.println("READING LASERS");
    for(int i = 0; i < NUM_OF_SENSORS; i++){
      laser[i].rangingTest(&measure[i], false);
      dist[i] = -1;
      dist[i] = measure[i].RangeMilliMeter;
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
