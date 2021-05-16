#include "ArduinoMaze.h"

FSTATE fstate = CALC;
DIRECTION currDir;

Chassis *_chassis;
LaserSystem *_laser;
SA *_comm;
IRTherm therm1;
IRTherm therm2;
Servo x;


double threshold = 200;
double forward, angAdj;
String path;
int step, skip;
int light;

void rightServo() {
  x.write(135);
  delay(1000);
  for (int pos = 135; pos >= 80; pos -= 4) {
    x.write(pos);              
    delay(15);                       
  }
  delay(1000);
}

void leftServo() {
  x.write(45);
  delay(1000);
  for (int pos = 45; pos <= 100; pos += 4) {
    x.write(pos);              
    delay(15);                      
  }
  
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
  _chassis = new Chassis();
  _laser = new LaserSystem();
  _comm = new SA();
  Serial.begin(115200);
  Serial2.begin(9600);
  while (!Serial)
    delay(1);
  Serial.println("Begin!");
  Wire.begin();
  _chassis->init();
  _chassis->reset();
  _laser->init();
  if (therm1.begin(0x5a) == false) {
    Serial.println("Qwiic IR thermometer 1 did not acknowledge! Running I2C scanner.");
    while(1);
  }
//  if (therm2.begin(0x5b) == false) {
//    Serial.println("Qwiic IR thermometer 2 did not acknowledge! Running I2C scanner.");
//    while(1);
//  }
  therm1.setUnit(TEMP_F);
//  therm2.setUnit(TEMP_F);
  Serial.println("Finished therms");
  pinMode(sPin, INPUT_PULLUP);
  pinMode(9, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(_chassis->getLEncInt()), lMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(_chassis->getREncInt()), rMotorEncInterrupt, RISING);
  attachInterrupt(digitalPinToInterrupt(sPin), vSerialInterrupt, FALLING);
  x.attach(servPin);
  x.write(90);
  delay(2000);
}
void readSensors(){//read all sensors
  _chassis->readChassis();
  light = analogRead(A7);
  //_laser->read();  
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
  String walls = ""; //Front, Right, Back, Left (Clockwise)
  _laser->readAll();
  _laser->print();
  if(_laser->getDist(1) < threshold) {
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
  _comm->writeOut(walls);
}

void getPath(){//get BFS path from PI
  checkVictim();
  path = _comm->readIn();
  step = 0;
}

void checkVictim() {
  String letter;
  if(victim) {
        _chassis->runMotors(0);
        Serial.println("\nRECIEVED SOMETHING\n");
        letter = _comm->readSerial();
        if(letter[0] == 't'){
          victim = false;
          return;
         }
        _laser->readAll();
        _laser->print();
        if(step >= path.length()- 1) {
          _chassis->resetR();
          if((_laser->getDist(3)<200 && letter[1] == 'R')) {
            _chassis->runMotors(0);
            Serial.println("Stopping motors");
            Serial.print("SAW LETTER: ");
            Serial.println(letter);
            //prev_victim = true;
//            for(int i = 0; i < letter[0]-'0'; i++) {
//              rightServo();
//            }
//          
            digitalWrite(9, HIGH);
            delay(3000);
            digitalWrite(9, LOW);
          }
          if((_laser->getDist(2)<200 && letter[1] == 'L')) {
            _chassis->runMotors(0);
            Serial.println("Stopping motors");
            Serial.print("SAW LETTER: ");
            Serial.println(letter);
            //prev_victim = true;
//            for(int i = 0; i < letter[0]-'0'; i++) {
//              leftServo();
//            }
            digitalWrite(9, HIGH);
            delay(3000);
            digitalWrite(9, LOW);
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
  //readSensors();
  switch(fstate){
    case FSTATE::CALC:{
      skip = step + 1;
//      while(skip < path.length() && path[skip] == 'U')
//        skip++;
      fstate = TURNING;
      break;
    }
    case FSTATE::TURNING:{
      if(therm1.read()) {
//        Serial.print(" Temp 1: ");
//        Serial.println(String(therm1.object(), 2));
        if(therm1.object()>80 && !prev_victim) {
          Serial.println(therm1.object());

          Serial.println("SAW HEAT\n");
          _chassis->resetR();
          _chassis->runMotors(0);
          
          digitalWrite(9, HIGH);
          delay(5000);
          digitalWrite(9, LOW);
          prev_victim = true;
        }
      }
      if(_chassis->turnTo(ang[(currDir + getDir(path[step]))%4])){
        currDir = (currDir + getDir(path[step]))%4;
        _laser->readAll();
        angAdj = 0;
        double fe = TILE_SIZE + 40;
        if(min(_laser->getDist(0), _laser->getDist(1)) < 450)
            fe = fmod((min(_laser->getDist(0), _laser->getDist(1))), TILE_SIZE) + (TILE_SIZE)/2 + 120;
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
          if(therm1.object()>80 && !prev_victim) {
            Serial.println(therm1.object());
            Serial.println("SAW HEAT\n");
            _chassis->resetR();
            _chassis->runMotors(0);
            digitalWrite(9, HIGH);
            delay(5000);
            digitalWrite(9, LOW);
            prev_victim = true;
          }
          
        }
      else {
       Serial.println("Failed therm 1");
      }
      if(_chassis->goMm(forward)){
        fstate = FORADJ;
      }
      break;
    }
    case FSTATE::FORADJ:{
      if(_chassis->turnTo(ang[currDir])){
        fstate = CALC;
        step = skip;
        _chassis->reset();
        if(step == path.length())
          return true;
      }
      break;
    }
//    case FSTATE::BLACKTILE{
//      chassis.goto(0);
//    }
  }
  return false;
}
