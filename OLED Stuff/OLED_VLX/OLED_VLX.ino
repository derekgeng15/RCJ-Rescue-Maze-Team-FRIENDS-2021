#include "Adafruit_VL53L0X.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

Adafruit_VL53L0X lox = Adafruit_VL53L0X();

void setup() {
  Serial.begin(9600);
  
  // wait until serial port opens for native USB devices
  while (! Serial) {
    delay(1);
  }

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  
  Serial.println("Adafruit VL53L0X test");
  if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
    while(1);
  }
  // power 
  Serial.println(F("VL53L0X API Simple Ranging example\n\n")); 
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.display(); 
  Serial.println("finished!");
}


void loop() {
  VL53L0X_RangingMeasurementData_t measure;
   
  Serial.println("Reading a measurement... ");
  lox.rangingTest(&measure, false); // pass in 'true' to get debug data printout!
  display.clearDisplay();
  display.setCursor(0, 0);
  if (measure.RangeStatus != 4) {  // phase failures have incorrect data
    display.print("Distance (mm): "); display.println(measure.RangeMilliMeter);
  } else {
    display.println(" out of range ");
  }
    display.display(); 
    
  delay(100);
}
