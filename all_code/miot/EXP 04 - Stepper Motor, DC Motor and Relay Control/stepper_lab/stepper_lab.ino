/*  EXP 04 - Stepper motor with the Stepper library through L293D (Arduino Uno)
    Source: lab code PDF 'MIOT all codes'.
    WIRING
      D8 -> L293D pin 2 (IN1)    D9 -> pin 7 (IN2)
      D10 -> L293D pin 10 (IN3)  D11 -> pin 15 (IN4)
      L293D pin 16 (VCC1) -> 5V ; pin 8 (VCC2) -> motor supply (+) ; pins 4,5,12,13 -> GND (and supply GND)
      L293D pin 1 (EN1) and pin 9 (EN2) -> 5V
      Motor coil A -> pin 3 (OUT1) and pin 6 (OUT2) ; coil B -> pin 11 (OUT3) and pin 14 (OUT4)
      Uno GND and motor-supply GND joined.
    STEPS
      1. Plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload.
      4. Tools > Serial Monitor (9600): 'clockwise', one turn, 'counterclockwise', one turn, repeating.
    NOTE
      'Stepper' is a built-in library, nothing to install.
      stepsPerRevolution = 200 is for a 1.8 deg motor. Change it for other motors.
      Motor only buzzes? Swap the two wires of one coil.
*/

#include <Stepper.h>

const int stepsPerRevolution = 200;            // change this to fit your motor

// initialize the stepper library on pins 8 through 11
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);

void setup() {
  myStepper.setSpeed(60);                      // 60 rpm
  Serial.begin(9600);
}

void loop() {
  Serial.println("clockwise");
  myStepper.step(stepsPerRevolution);
  delay(500);

  Serial.println("counterclockwise");
  myStepper.step(-stepsPerRevolution);
  delay(500);
}
