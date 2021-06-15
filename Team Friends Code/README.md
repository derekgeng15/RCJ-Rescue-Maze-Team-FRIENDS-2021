 
The following folders contain the code we used for our robot and an accompanying brief description:
 
Raspberry Pi – StereoPi:
ArduinoSerial3.py-File that contains the driver program to be executed during an actual run. Uses other files found in this folder to fulfill its duties on the Raspberry Pi side
ColorDetector.py-File that contains color-detection functions that our main program uses to detect color victims via the two cameras
commLOP.py-File that contains class definition of object that handles the Serial & GPIO communication between the Raspberry Pi SteroPi and the Arduino MegaPi on the Raspberry Pi side.
LetterDetector.py-File that contains letter-detection functions that our main program uses to detect letter victims via the two cameras
nav.py-File that contains class definition of object that handles the navigation system of our robot. Also handles file I/O to record traversed Maze should the robot lack of progress to the checkpoint

Arduino - MegaPi
Main.ino-File that contains the driver program to be executed during an actual run. Uses other files found in this folder to fulfill its duties on the Arduino side
ArduinoMaze.cpp-Contains utility functions for state machine and victim detection
Chassis.cpp-Wrapper class that contains movement and some sensor functions for robot
LaserSystem.cpp-Wrapper class for lasers
SerialArduino.cpp-Class for Serial communication with Pi

