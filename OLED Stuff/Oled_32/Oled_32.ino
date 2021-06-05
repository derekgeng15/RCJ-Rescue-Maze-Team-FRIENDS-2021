
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  Serial.begin(9600);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.clearDisplay();
/*
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  // Display static text
  display.println("23 & Me");
  display.println("HI");
  display.setCursor(0, 20);
  display.println("24C");
  display.setCursor(0, 30);
  display.println("14 inches");
  display.display(); 
  Serial.println("finished!");
  */
  //display.invertDisplay(true);
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Hello, world!");
 /* for(int i = 0; i < SCREEN_HEIGHT; i++)
  {
    display.drawPixel(0,i, WHITE);
    display.drawPixel(1,i, WHITE);
  }*/
  display.display(); 
  Serial.println("finished!");
  delay(5000);
  display.clearDisplay();
  display.display(); 
}

void loop() {
  /*display.startscrollright(0x00, 0x0F);
  delay(2000);*/
  display.startscrollleft(0x00, 0x0F);
  delay(2000);
  display.stopscroll();
  delay(1000);
  display.startscrolldiagright(0x00, 0x07);
  delay(2000);
  display.startscrolldiagleft(0x00, 0x07);
  delay(2000);
  display.stopscroll();
  delay(1000);
  
}
