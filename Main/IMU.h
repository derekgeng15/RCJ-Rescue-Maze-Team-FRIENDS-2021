#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>

class IMU:public Adafruit_BNO055{
    private:
      volatile int8_t ID;
      volatile int8_t address;
    public:
      IMU(int8_t id, int8_t add);
      int init();
      double getYaw();
};
