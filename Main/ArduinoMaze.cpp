#include "ArduinoMaze.h"

FSTATE fstate = CALC;
OSTATE ostate = BACKWARDS;
DIRECTION currDir;

Chassis *_chassis;
LaserSystem *_laser;
Adafruit_TCS34725 *_color;
SA *_comm;
IRTherm therm1;
IRTherm therm2;
Servo servo;

double oang;

bool lOb, rOb;
int lObCt = 0, rObCt = 0;

double threshold = 250;
double forward, angAdj;
String path;
int step, skip;
uint16_t light;
int blackcount = 0;
int silvercount = 0;
int turnStep = 0;
bool silver = false;
double startTime = 0;


int selPort(int i) { //changes port on MUX
  if (i > 7)
    return 4;
  Wire.beginTransmission(MUX);
  Wire.write(1 << i);
  Wire.endTransmission();

}
void rightServo() { //deploys kit to right side
  servo.attach(servPin);
  servo.write(135);
  delay(1000);
  servo.write(80);
  delay(1000);
  servo.write(90);
  delay(1000);
  servo.detach();
}

void leftServo() { //deploys kit to left side
  servo.attach(servPin);
  servo.write(45);
  delay(1000);
  servo.write(100);
  delay(1000);
  servo.write(90);
  delay(1000);
  servo.detach();
}

bool prev_victim = false;

volatile bool victim = false, color = false;
void lMotorEncInterrupt()
{
  _chassis->updLEnc();
}
void rMotorEncInterrupt()
{
  _chassis->updREnc();
}
void vInterrupt() {
  victim = true;
}
void cInterrupt(){
  color = true;
}
DIRECTION getDir(char c) {
  switch (c) {
    case 'U':
      return UP;
    case 'R':
      return RIGHT;
    case 'D':
      return DOWN;
    case 'L':
      return LEFT;
  }
}

void prevFunc() {
  if (prev_victim && _chassis->getrEncCt() > encPerMm * 300) {
    Serial.println("PREV RESETTING");
    prev_victim = false;
  }
}

void begin() {
  Serial.begin(115200);
  Serial2.begin(9600);
  while (!Serial)
    delay(1);
  Serial.println("Begin!");
  Wire.begin();
  selPort(1);
  _chassis = new Chassis();
  _laser = new LaserSystem();
  _comm = new SA();
  _chassis->init();
  _chassis->reset();
  _laser->init();
  selPort(0);
  _color = new Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_16X);
  
  if (_color->begin()) {
    Serial.println("Found color sensor");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
  _color->setIntLimits(silverThresh, 20000);
  _color->setInterrupt(true);
  selPort(1);
  if (!therm1.begin(0x5b)) {
    Serial.println("Qwiic IR thermometer 1 did not acknowledge! Running I2C scanner.");
    while (1);
  }
  if (!therm2.begin(0x5a)) {
    Serial.println("Qwiic IR thermometer 2 did not acknowledge! Running I2C scanner.");
    while (1);
  }
  therm1.setUnit(TEMP_F);
  therm2.setUnit(TEMP_F);
  Serial.println("Finished therms");
  pinMode(sPin, INPUT_PULLUP);
  pinMode(cIPin, INPUT_PULLUP);
  pinMode(vPinA, INPUT);
  pinMode(vPinB, INPUT);
  pinMode(vPinC, INPUT);

  pinMode(vPinD, OUTPUT);
  pinMode(9, OUTPUT);

  pinMode(lObPin, INPUT_PULLUP);
  pinMode(rObPin, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(_chassis->getLEncInt()), lMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(_chassis->getREncInt()), rMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(sPin), vInterrupt, FALLING);
//  attachInterrupt(digitalPinToInterrupt(cIPin), cInterrupt, FALLING);
  servo.attach(servPin);
  servo.write(90);
  servo.detach();
  _comm->writeSerial("RESET");
  delay(2000);
}
void readSensors() { //read all sensors
  _chassis->readChassis();
//  Serial.println(_chassis->getPitch() * 180 / PI);
//  if(color){
//    selPort(0);
//    light = _color->getC();
//      Serial.println(light);
//    selPort(1);
//    color = false;
//  }
//    else
//      light = silverThresh + 200;
  selPort(0);
  light = _color->getC();
//  Serial.println(light);
  selPort(1);
  lOb = digitalRead(lObPin);
//  Serial.print("lob:" );
//  Serial.println(lOb);
//  lOb = 0;
  rOb = digitalRead(rObPin);
  //  Serial.print(rOb);
  //  lOb = 0;
  //  rOb = 0;
  therm1.read();
  therm2.read();
  _laser->readAll();
}
void print() {
  Serial.println("--------------------");
  _chassis->print();
  _laser->print();

  Serial.print("Light: ");
  Serial.println(light);
  Serial.println("--------------------");
}
void readTile() { //read Tile data and send to PI
  digitalWrite(vPinD, LOW);
  if (fstate == BLACKTILE) {
    _comm->writeSerial("1111");
    return;
  }
  String walls = ""; //Front, Right, Back, Left (Clockwise)
  // _laser->readAll();
  // _laser->print();
  for (int i = 0; i < 4; i++) {
    Serial.print("L");
    Serial.print(i);
    Serial.print(": ");
    Serial.print(_laser->getDist(i));
    Serial.print('\t');
  }
  if (_laser->getDist(1) < threshold && _laser->getDist(0) < threshold ) {
    walls += "1";
  }
  else
    walls += "0";

  if (_laser->getDist(3) < threshold) {
    walls += "1";
  }
  else
    walls += "0";
  walls += "0";
  if (_laser->getDist(2) < threshold) {
    walls += "1";
  }
  else
    walls += "0";
  if (light > silverThresh) {
    
    walls += " CHECKPOINT";
    silver = false;
  }
  _comm->writeSerial(walls);
  delay(5);
}

void getPath() { //get BFS path from PI
  path = _comm->readSerial();
  if (path.length() == 0) {
    Serial.println("DONE WITH ALL");
    while (1);
  }
  step = 0;
  fstate = CALC;
}

bool obstacle() {
  switch (ostate) {
    case OSTATE::BACKWARDS: {
        if (_chassis->goMm(0) || (millis() - startTime) > 2000) {
          ostate = OSTATE::TURN;
          startTime = millis();
        }
        break;
      }
    case OSTATE::TURN: {
        if (_chassis->turnTo(oang) || (millis() - startTime) > 2000) {
          ostate = OSTATE::PARK;
          startTime = millis();
          _chassis->reset();
        }
        break;
      }
    case OSTATE::PARK: {
        if (_chassis->goMm(-10 / sin(15 * PI / 180)) || (millis() - startTime) > 2000) {
          ostate = ADJ;
          startTime = millis();
        }
        break;
      }
    case OSTATE::ADJ: {
        if (_chassis->turnTo(ang[currDir])) {
          _chassis->reset();
          forward = 10/tan(15 * PI / 180) + 330;
          ostate = BACKWARDS;
          return true;
        }
        break;
      }
  }

  return false;
}

void checkVictim() {
  // String letter;
  if (prev_victim && _chassis->getrEncCt() > encPerMm * 300) {
    Serial.println("PREV RESETTING");
    prev_victim = false;
  }
  if (victim) {
    _chassis->runMotors(0);
     Serial.println("\nRECIEVED SOMETHING\n");
     
     if(fstate == FORWARD){
      int curr = _chassis->getlEncCt();
      while(!_chassis->goVic(0))
        _chassis->readChassis();
     }
    // letter = _comm->readSerial();
    int num = digitalRead(vPinA) * 2 + digitalRead(vPinB);
    int side = digitalRead(vPinC);
    _laser->readAll();
    _laser->print();
    if (step >= path.length() - 1 || step == 0) {
      _chassis->resetR();
      if ((_laser->getDist(3) < 200 && side == 1)) {
        digitalWrite(vPinD, HIGH);
        _chassis->runMotors(0);
        Serial.println("Stopping motors");
        Serial.print("SAW LETTER RIGHT: ");
        Serial.println(num);

        digitalWrite(9, HIGH);
        //prev_victim = true;
        _chassis->readChassis();
        double prevAngle = _chassis->getYaw() * 180 / PI;
        double pR = _chassis->getrEncCt(), pL = _chassis->getlEncCt();
        double tang;
        if(num != 0){
          tang = prevAngle - 60;
          Serial.print("prevAngle: ");
          Serial.println(prevAngle);
          Serial.print("tang ");
          Serial.println(tang);
          double st = millis();
          while(!_chassis->turnVic(tang) && millis() - st < 2000){
            _chassis->readChassis();
          }
          _chassis->runMotors(0);
          for (int i = 0; i < num; i++) {
            rightServo();
          }
          while(!_chassis->turnVic(prevAngle)){
            _chassis->readChassis();
          }
          _chassis->setCount(pL, pR);
        }
        delay(5000 - 2000 * (num != 0));
        digitalWrite(9, LOW);

      }
      if ((_laser->getDist(2) < 200 && side == 0)) {
        _chassis->runMotors(0);
        digitalWrite(vPinD, HIGH);
        Serial.println("Stopping motors");
        Serial.print("SAW LETTER LEFT: ");
        Serial.println(num);
        //prev_victim = true;
        digitalWrite(9, HIGH);
        _chassis->readChassis();
        double prevAngle = _chassis->getYaw() * 180 / PI;
        double pR = _chassis->getrEncCt(), pL = _chassis->getlEncCt();
        double tang;
        if(num != 0){
          tang = fmod(prevAngle + 60, 360);
          Serial.print("prevAngle");
          Serial.println(prevAngle);
          Serial.print("tang");
          Serial.println(tang);
          double st = millis();
          while(!_chassis->turnVic(tang) &&  millis() - st < 2000)
            _chassis->readChassis();
           _chassis->runMotors(0);
          for (int i = 0; i < num; i++) {
            leftServo();
          }
         tang = _chassis->getYaw() * 180 / PI - 60;
     
         while(!_chassis->turnVic(tang))
           _chassis->readChassis();
          _chassis->setCount(pL, pR);
        }
        delay(5000 - 2000 * (num != 0));
        digitalWrite(9, LOW);
 
      }
    }
    victim = false;
  }
}
unsigned long myTime;

bool followPath() { //TODO: Add state machine for following
  /*
         if see black, call ai blackout(rPI serial)

  */
  if (step == path.length() - 1) {
    if (light <= blackThresh && fstate != FSTATE::BLACKTILE) {
      blackcount++;
    }
    if (blackcount >= 2) {
      fstate = FSTATE::BLACKTILE;
      _chassis->runMotors(0);
      delay(200);
      blackcount = 0;
    }
  }

  (rObCt += rOb) *= rOb;
  (lObCt += lOb) *= lOb;

  if (rObCt > 5 && fstate == FSTATE::FORWARD) {
    Serial.println("ROB");
    if (ang[currDir] + 15 < 0)
      oang = ang[currDir] + 15 + 360;
    else
      oang = fmod(ang[currDir] + 15, 360);
    ostate = OSTATE::BACKWARDS;
    fstate = FSTATE::OBSTACLE;
    startTime = millis();
  }
  if (lObCt > 5 && fstate == FSTATE::FORWARD) {
    Serial.println("LOB");
    if (ang[currDir] - 15 < 0)
      oang = ang[currDir] - 15 + 360;
    else
      oang = fmod(ang[currDir] - 15, 360);
    ostate = OSTATE::BACKWARDS;
    fstate = FSTATE::OBSTACLE;
    startTime = millis();
  }
  if (therm1.object() > 80 && !prev_victim && (step == path.length() - 1 || step == 0)) {
    digitalWrite(vPinD, HIGH);
    Serial.println(therm1.object());
    Serial.println("SAW HEAT\n");
    _chassis->resetR();
    _chassis->runMotors(0);
    digitalWrite(9, HIGH);
    _chassis->readChassis();
    double prevAngle = _chassis->getYaw() * 180 / PI;
    double pR = _chassis->getrEncCt(), pL = _chassis->getlEncCt();
    double tang;
    tang = fmod(prevAngle + 60, 360);
    Serial.print("prevAngle");
    Serial.println(prevAngle);
    Serial.print("tang");
    Serial.println(tang);
    double st = millis();
    while(!_chassis->turnVic(tang) && millis() - st < 2000)
      _chassis->readChassis();
     _chassis->runMotors(0);
    leftServo();
    tang = _chassis->getYaw() * 180 / PI - 60;

    while(!_chassis->turnVic(tang))
      _chassis->readChassis();
    _chassis->setCount(pL, pR);
    delay(3000);
    digitalWrite(9, LOW);
    prev_victim = true;
  }
  if (therm2.object() > 80 && !prev_victim && (step == path.length() - 1 || step == 0)) {
    digitalWrite(vPinD, HIGH);
    Serial.println(therm2.object());

    Serial.println("SAW HEAT\n");
    _chassis->resetR();
    _chassis->runMotors(0);

    digitalWrite(9, HIGH);
    double prevAngle = _chassis->getYaw() * 180 / PI;
    double pR = _chassis->getrEncCt(), pL = _chassis->getlEncCt();
    double tang;
    tang = fmod(prevAngle + 300, 360);
    Serial.print("prevAngle: ");
    Serial.println(prevAngle);
    Serial.print("tang ");
    Serial.println(tang);
    double st = millis();
    while(!_chassis->turnVic(tang) && millis() - st < 2000){
      _chassis->readChassis();
    }
     _chassis->runMotors(0);
      rightServo();
    while(!_chassis->turnVic(prevAngle)){
      _chassis->readChassis();
    }
    _chassis->setCount(pL, pR);
    delay(3000);
    digitalWrite(9, LOW);
    prev_victim = true;
  }
  switch (fstate) {
    case FSTATE::CALC: {
        
        skip = step + 1;
        //      while(skip < path.length() && path[skip] == 'U')
        //        skip++;
        fstate = TURNING;
        myTime = millis();
        startTime = millis();
        turnStep = 0;
        if(skip != 0)
            delay(300);
        break;
      }
    case FSTATE::TURNING: {
        //Serial.print(millis()-myTime);
        //Serial.print(" ");
        if(path[step] == 'D' && turnStep == 0){
          if(_chassis->turnTo(ang[(currDir + 3) % 4]) || (millis() - startTime) > 3000){
            turnStep++;
            delay(300);
            startTime = millis();
          }
          break;
        }
        if (_chassis->turnTo(ang[(currDir + getDir(path[step])) % 4]) || (millis() - startTime) > 3000) {
          currDir = (currDir + getDir(path[step])) % 4;
          _laser->readAll();
          angAdj = 0;
          //self-correction
          double fe = TILE_SIZE + 30 + (path[step] == 'D') * 25;
          //        Serial.println(abs(_chassis->getPitch() - 5) * 180 / PI));
          if (min(_laser->getDist(0), _laser->getDist(1)) < 500 && abs(_laser->getDist(0) - _laser->getDist(1)) < 100 && abs(_chassis->getPitch() * 180 / PI - 5)  <= 10) {
            fe = fmod((min(_laser->getDist(0), _laser->getDist(1))), TILE_SIZE);
            if (fe > 150)
              fe -= 300;
            fe += (TILE_SIZE) / 2 + 90;
          }
          if (_laser->getDist(2) < TILE_SIZE)
            angAdj =  -atan2(_laser->getDist(2) - 100, (skip - step - 1) * (TILE_SIZE) + fe) * 180 / PI;
          if (_laser->getDist(3) < TILE_SIZE)
            angAdj =  atan2(_laser->getDist(3) - 135, (skip - step - 1) * (TILE_SIZE) + fe) * 180 / PI;
          forward = ((skip - step - 1) * (TILE_SIZE) + fe) / cos(PI / 180 * angAdj) ;
          _laser->print();
          Serial.println(forward);
          Serial.println(angAdj);
          fstate  = TURNADJ;
          delay(500);
          startTime = millis();

        }
        break;
      }
    case FSTATE::TURNADJ: {
        if (_chassis->turnTo(ang[currDir] + angAdj) || (millis() - startTime) > 3000) {
          _chassis->reset();
          fstate = FORWARD;
          myTime = millis();
        }
        break;
      }
    case FSTATE::FORWARD: {
        _chassis->updateEnc();
        if (_chassis->getlEncCt() * encPerMm > 50) {
          if (light <= silverThresh && blackcount == 0)
            silvercount++;
          else
            silvercount = 0;
          if (silvercount >= 5)
            silver = true;
        }
        if (_chassis->goMm(forward) || (_laser->getDist(0) <= 65 && _laser->getDist(1) <= 65)) {
          fstate = FORADJ;

        }
        break;
      }
    case FSTATE::FORADJ: {
        if (_chassis->turnTo(ang[currDir])) {
          fstate = CALC;
          blackcount = 0;
          Serial.print("silver ct:");
          Serial.println(silver);
          silvercount = 0;
          step = skip;
          _chassis->reset();
          if (step == path.length())
            return true;
        }
        break;
      }
    case FSTATE::OBSTACLE: {
        if (obstacle())
          fstate = FORWARD;
        break;
      }
    case FSTATE::BLACKTILE: {
        Serial.println("BLACKOUT");
        if (_chassis->goMm(-0 * encPerMm)) {
          return true;
        }
        break;
      }
  }
  return false;
}
