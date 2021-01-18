#include <Wire.h>
#include <Arduino.h>

#include "Chassis.h"
#include "LazerSystem.h"
#include "IMU.h"

#include "SerialArduino.h"


#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

enum FSTATE {
  TURNING, FORWARD
}extern fstate;

enum DIRECTION{
  UP, RIGHT, DOWN, LEFT
}extern currDir;

const double ang[] = {0, PI/2, PI, 3 * PI/2};

extern Chassis *_chassis;
extern LazerSystem *_lazer;
extern SA *_comm;

extern String path;
extern int step;

void lMotorEncInterrupt();
void rMotorEncInterrupt();

DIRECTION getDir(char c);

void begin();
void readSensors();
void readTile();
void getPath();
bool followPath();
