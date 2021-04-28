
#pragma once

#include <Wire.h>
#include <SparkFunMLX90614.h>

#include <Arduino.h>
#include <math.h>

#include "Chassis.h"
#include "LaserSystem.h"

#include "SerialArduino.h"


#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define TILE_SIZE 300

enum FSTATE {
  CALC, TURNING, TURNADJ, FORWARD, FORADJ
}extern fstate;

enum DIRECTION{
  UP, RIGHT, DOWN, LEFT
}extern currDir;

const double ang[] = {0, 90, 180, -90};

extern double forward, angAdj;

extern Chassis *_chassis;
extern LaserSystem *_laser;
extern SA *_comm;

extern String path;
extern int step, skip;



void lMotorEncInterrupt();
void rMotorEncInterrupt();

DIRECTION getDir(char c);

void begin();
void readSensors();
void print();
void readTile();
void getPath();
bool followPath();
