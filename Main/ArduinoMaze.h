#include <Wire.h>
#include <Arduino.h>

#include "Chassis.h"
#include "LazerSystem.h"
#include "IMU.h"


#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

extern String path;

extern Chassis *_chassis;
extern LazerSystem *_lazer;

void lMotorEncInterrupt();
void rMotorEncInterrupt();

void begin();
void readSensors();
void readTile();
void getPath();
bool followPath();
