
#include <Wire.h>
#include <SparkFunMLX90614.h>
#include <Adafruit_TCS34725.h>

#include <Arduino.h>
#include <math.h>

#include "Chassis.h"
#include "LaserSystem.h"

#include "SerialArduino.h"


#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define TILE_SIZE 300

#define MUX 0x70

enum FSTATE {
  CALC, TURNING, TURNADJ, FORWARD, FORADJ, BLACKTILE, OBSTACLE
}extern fstate;

enum OSTATE{
  BACKWARDS, TURN, PARK, ADJ
}extern ostate;

enum DIRECTION{
  UP, RIGHT, DOWN, LEFT
}extern currDir;

const double ang[] = {0, 90, 180, -90};

const int servPin = A6;

extern double forward, angAdj;

extern Chassis *_chassis;
extern LaserSystem *_laser;
extern Adafruit_TCS34725 *_color;
extern SA *_comm;

extern String path;
extern int step, skip;
extern int blackcount;

extern volatile bool victim, color;

const int sPin = 3;
const int vPinA = 5, vPinB = 49, vPinC = 4, vPinD = 6;
const int cIPin = 2;
extern bool prev_victim;

const int lObPin = 22;
const int rObPin = 23;
extern bool lOb, rOb;
extern int lObCt, rObCt;
const int blackThresh = 7000;
const int silverThresh = 19000;

void lMotorEncInterrupt();
void rMotorEncInterrupt();

DIRECTION getDir(char c);

void begin();
void readSensors();
void print();
void readTile();
void getPath();
bool followPath();
void checkVictim();
void prevFunc();
void leftServo();
void rightServo();
int selPort(int i);
