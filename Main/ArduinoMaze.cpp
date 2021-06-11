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
Servo x;

double oang;

bool lOb, rOb;
int lObCt = 0, rObCt = 0;

double threshold = 200;
double forward, angAdj;
String path;
int step, skip;
uint16_t light;
int blackcount = 0;

int selPort(int i){
    if(i > 7)
      return 4;
     Wire.beginTransmission(MUX);
     Wire.write(1 << i);
     Wire.endTransmission();

}
void rightServo() {
  x.attach(servPin);
  x.write(135);
  delay(1000);
  x.write(80);
  delay(1000);
  x.write(90);
  delay(1000); 
  x.detach();
}

void leftServo() {
  x.attach(servPin);
  x.write(45);
  delay(1000);
  x.write(100);
  delay(1000);
  x.write(90);
  delay(1000);
  x.detach();
}

bool prev_victim = false;


volatile bool victim = false;
void lMotorEncInterrupt()
{
  _chassis->updLEnc();
}
void rMotorEncInterrupt()
{
  _chassis->updREnc();
}
void vSerialInterrupt(){
  victim = true;
}
DIRECTION getDir(char c){
  switch(c){
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
  if(prev_victim && _chassis->getrEncCt()>encPerMm*300) {
    Serial.println("PREV RESETTING");
    prev_victim = false;
  }
}

void begin(){
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
  _color = new Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_2_4MS, TCS34725_GAIN_16X);

  if (_color->begin()) {
    Serial.println("Found color sensor");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
  selPort(1);
  if (!therm1.begin(0x5b)) {
    Serial.println("Qwiic IR thermometer 1 did not acknowledge! Running I2C scanner.");
    while(1);
  }
  if (!therm2.begin(0x5a)) {
    Serial.println("Qwiic IR thermometer 2 did not acknowledge! Running I2C scanner.");
    while(1);
  }
  therm1.setUnit(TEMP_F);
  therm2.setUnit(TEMP_F);
  Serial.println("Finished therms");
  pinMode(sPin, INPUT_PULLUP);
  pinMode(vPinA, INPUT);
  pinMode(vPinB, INPUT);
  pinMode(vPinC, INPUT);
  pinMode(9, OUTPUT);

  pinMode(lObPin, INPUT_PULLUP);
  pinMode(rObPin, INPUT_PULLUP);

  
  
  attachInterrupt(digitalPinToInterrupt(_chassis->getLEncInt()), lMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(_chassis->getREncInt()), rMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(sPin), vSerialInterrupt, FALLING);
  x.attach(servPin);
  x.write(90);
  x.detach();
  _comm->writeSerial("RESET");
  delay(2000);
}
void readSensors(){//read all sensors
  _chassis->readChassis();

  selPort(0);
  light = 1025;
//  uint16_t r, g, b;
//  _color->getRawData(&r, &g, &b, &light);
//  Serial.print(r);
//  Serial.print(' ');
//  Serial.println(light);
  selPort(1);
  lOb = digitalRead(lObPin);
  rOb = digitalRead(rObPin);
//  Serial.println(lisght);
   _laser->readAll();  
}
void print(){
  Serial.println("--------------------");
//  _chassis->print();
  _laser->print();
  
  Serial.print("Light: ");
  Serial.println(light);
  Serial.println("--------------------");
}
void readTile(){//read Tile data and send to PI
  if(fstate == BLACKTILE){
    _comm->writeSerial("1111");
    return;
  }
  String walls = ""; //Front, Right, Back, Left (Clockwise)
  // for(int i = 0; i < 3; i++){
  //   _laser->readAll();
  //   _laser->print();
  // }
  _laser->readAll();
  _laser->print();
  if(_laser->getDist(1) < threshold && _laser->getDist(0) < threshold ) {
    walls+="1";
    Serial.println("First Sensor Seen");
  }
  else
    walls+="0";


  if(_laser->getDist(3) < threshold) {
    Serial.println("Second Sensor Seen");
    walls+="1";
  }
  else
    walls+="0";
  walls+="0";
  if(_laser->getDist(2) < threshold) {
    Serial.println("Third Sensor Seen");
    walls+="1";
  }
  else
    walls+="0";
   checkVictim();
   if(light > silverThresh)
    walls += " CHECKPOINT";
  _comm->writeSerial(walls);
   checkVictim();
   delay(5);
   //_comm->readConfirm();
}

void getPath(){//get BFS path from PI
  checkVictim();
  path = _comm->readSerial();
  String letter;
  if(path.length() == 0) {
    Serial.println("DONE WITH ALL");
    while(1);
  }
  step = 0;
  fstate = CALC;
}

bool obstacle(){
  switch(ostate){
    case OSTATE::BACKWARDS:{
      if(_chassis->goMm(0)){
        ostate = OSTATE::TURN;
      }
      break;
    }
    case OSTATE::TURN:{
      if(_chassis->turnTo(oang)){
        ostate = OSTATE::PARK;
        _chassis->reset();
      }
      break;
    }
    case OSTATE::PARK:{
      if(_chassis->goMm(-30 * sqrt(2))){
        ostate = ADJ;
      }
      break;
    }
    case OSTATE::ADJ:{
      if(_chassis->turnTo(ang[currDir])){
        _chassis->reset();
        forward = 400;
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
  if(victim) {
        _chassis->runMotors(0);
        // Serial.println("\nRECIEVED SOMETHING\n");
        // letter = _comm->readSerial();
        // if(letter[0] == 't'){
        //   victim = false;
        //   return;
        //  }
        int num = digitalRead(vPinA) * 2 + digitalRead(vPinB);
        int side = digitalRead(vPinC);
        _laser->readAll();
        _laser->print();
        if(step >= path.length()- 1 || step == 0) {
          _chassis->resetR();
          if((_laser->getDist(3)<200 && side == 1)) {
            _chassis->runMotors(0);
            Serial.println("Stopping motors");
            Serial.print("SAW LETTER RIGHT: ");
            Serial.println(num);
            
            digitalWrite(9, HIGH);
            //prev_victim = true;
            double prevAng = _chassis->getYaw();
            double pR = _chassis->getrEncCt(), pL = _chassis->getlEncCt();
//            while(!_chassis->turnVic(fmod(prevAng + 45, 360)))
//              _chassis->readChassis();
            for(int i = 0; i < num; i++) {
              rightServo();
            }
   
            delay(3000);
            digitalWrite(9, LOW);
//            while(!_chassis->turnVic(prevAng))
//              _chassis->readChassis();
            _chassis->setCount(pL, pR);
          }
          if((_laser->getDist(2)<200 && side == 0)) {
            _chassis->runMotors(0);
            
            Serial.println("Stopping motors");
            Serial.print("SAW LETTER LEFT: ");
            Serial.println(num);
            //prev_victim = true;
            digitalWrite(9, HIGH);
            double prevAng = _chassis->getYaw();
            double pR = _chassis->getrEncCt(), pL = _chassis->getlEncCt();
            double target = prevAng - 45;
            if(target < 0)
              target += 360;
//            while(!_chassis->turnVic(target))
//              _chassis->readChassis();
            for(int i = 0; i < num; i++) {
              leftServo();
            }
            delay(3000);
            digitalWrite(9, LOW);
//            while(!_chassis->turnVic(prevAng))
//              _chassis->readChassis();
            _chassis->setCount(pL, pR);
          }
        }
        victim = false;
      }
}
unsigned long myTime;

bool followPath(){//TODO: Add state machine for following
  /*
       * if see black, call ai blackout(rPI serial)
       * 
       */
  if(step == path.length() - 1) {
    if(light <= blackThresh && fstate != FSTATE::BLACKTILE)
        blackcount++;
    if(blackcount >= 20) {
      fstate = FSTATE::BLACKTILE;
      blackcount = 0;
    }
  }

  (rObCt += rOb) *= rOb;
  (lObCt += lOb) *= lOb;
      
  
  if(rObCt > 30 && fstate == FSTATE::FORWARD){
    if(ang[currDir] + 45 < 0)
        oang = ang[currDir] + 45 + 360;
      else 
        oang = fmod(ang[currDir] + 45, 360);
      ostate = OSTATE::BACKWARDS;
      fstate = FSTATE::OBSTACLE;
  }
  if(lObCt > 30 && fstate == FSTATE::FORWARD){
      if(ang[currDir] - 45 < 0)
        oang = ang[currDir] - 45 + 360;
      else 
        oang = fmod(ang[currDir] - 45, 360);
      ostate = OSTATE::BACKWARDS;
      fstate = FSTATE::OBSTACLE;
  }
  
  //readSensors();
  switch(fstate){
    case FSTATE::CALC:{
      skip = step + 1;
//      while(skip < path.length() && path[skip] == 'U')
//        skip++;
      fstate = TURNING;
      myTime = millis();
      break;
    }
    case FSTATE::TURNING:{
      if(therm1.read()) {
//        Serial.print(" Temp 1: ");
//        Serial.println(String(therm1.object(), 2));
        if(therm1.object()>80 && !prev_victim && (step == path.length() - 1 || step == 0)) {
          Serial.println(therm1.object());

          Serial.println("SAW HEAT\n");
          _chassis->resetR();
          _chassis->runMotors(0);
          
          digitalWrite(9, HIGH);
          leftServo();
          delay(5000);
          digitalWrite(9, LOW);
          prev_victim = true;
        }
      }
      if(therm2.read()) {
//        Serial.print(" Temp 1: ");
//        Serial.println(String(therm1.object(), 2));
        if(therm2.object()>80 && !prev_victim && (step == path.length() - 1 || step == 0)) {
          Serial.println(therm2.object());

          Serial.println("SAW HEAT\n");
          _chassis->resetR();
          _chassis->runMotors(0);
          
          digitalWrite(9, HIGH);
          rightServo();
          delay(5000);
          digitalWrite(9, LOW);
          prev_victim = true;
        }
      }
      //Serial.print(millis()-myTime);
      //Serial.print(" ");
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        _laser->readAll();
        angAdj = 0;
        //self-correction
        double fe = TILE_SIZE + 40;
//        Serial.println(abs(_chassis->getPitch() - 5) * 180 / PI));
        if(min(_laser->getDist(0), _laser->getDist(1)) < 500 && abs(_chassis->getPitch()* 180 / PI - 5)  <= 10){
            fe = fmod((min(_laser->getDist(0), _laser->getDist(1))), TILE_SIZE);
            if(fe > 150)
              fe -= 300;
            fe += (TILE_SIZE)/2 + 90;
        }
        if(_laser->getDist(2) < TILE_SIZE)
            angAdj =  -atan2(_laser->getDist(2) - TILE_SIZE/2 + 44, (skip - step - 1) * (TILE_SIZE) + fe) * 180 / PI;
        if(_laser->getDist(3) < TILE_SIZE)
            angAdj =  atan2(_laser->getDist(3) - TILE_SIZE/2 + 7, (skip - step - 1) * (TILE_SIZE) + fe) * 180 / PI;
        forward = ((skip - step - 1) * (TILE_SIZE) + fe) / cos(PI / 180 * angAdj) ;
        _laser->print();
        Serial.println(forward);
        Serial.println(angAdj);
        fstate  = TURNADJ;
      }
      break;
    }
    case FSTATE::TURNADJ:{
      if(_chassis->turnTo(ang[currDir] + angAdj)){
        _chassis->reset();
        fstate = FORWARD;
        myTime = millis();
      }
      break;
    }
    case FSTATE::FORWARD:{
      _chassis->updateEnc();
//      if(therm2.read()) {
//        Serial.print(" Temp 2: ");
//        Serial.println(String(therm2.object(), 2));
//      }
//      else {
//        Serial.println("Failed therm");
//      }
        if(therm1.read()) {
          if(therm1.object()>80 && !prev_victim && (step == path.length() - 1 || step == 0)) {
            Serial.println(therm1.object());
            Serial.println("SAW HEAT\n");
            _chassis->resetR();
            _chassis->runMotors(0);
            digitalWrite(9, HIGH);
            leftServo();
            delay(5000);
            digitalWrite(9, LOW);
            prev_victim = true;
          }
          
        }
        if(therm2.read()) {
//        Serial.print(" Temp 1: ");
//        Serial.println(String(therm1.object(), 2));
          if(therm2.object()>80 && !prev_victim && (step == path.length() - 1 || step == 0)) {
            Serial.println(therm2.object());
  
            Serial.println("SAW HEAT\n");
            _chassis->resetR();
            _chassis->runMotors(0);
            
            digitalWrite(9, HIGH);
            rightServo();
            delay(5000);
            digitalWrite(9, LOW);
            prev_victim = true;
          }
      }
     // Serial.print(millis()-myTime);
     // Serial.print(" ");
      if(_chassis->goMm(forward) || _laser->getDist(0) <= 60){
        fstate = FORADJ;
      }
      break;
    }
    case FSTATE::FORADJ:{
      if(_chassis->turnTo(ang[currDir])){
        fstate = CALC;
        blackcount = 0;
        step = skip;
        _chassis->reset();
        if(step == path.length())
          return true;
      }
      break;
    }
    case FSTATE::OBSTACLE:{
      if(obstacle())
        fstate = FORWARD;
      break;
    }
    case FSTATE::BLACKTILE:{
      Serial.println("BLACKOUT");
      if(_chassis->goMm(-10 * encPerMm)){
        return true;
      }
      break;
    }
  }
  return false;
}
