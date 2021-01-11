#include "LazerSystem.h"
void LazerSystem::init(){
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
    if(!lazer[i].begin(ID[i])){
      Serial.print("Failed to Boot ");
      Serial.println(i);
      while(1)
        ;
    }
    delay(10);
  }
  Serial.println("IDs set");
}
double LazerSystem::getDist(int ID){
  return dist[ID];
}

void LazerSystem::read(){
    for(int i = 0; i < NUM_OF_SENSORS; i++){
      lazer[i].rangingTest(&measure[i], false);
      dist[i] = -1;
      dist[i] = measure[i].RangeMilliMeter;
    }
}
