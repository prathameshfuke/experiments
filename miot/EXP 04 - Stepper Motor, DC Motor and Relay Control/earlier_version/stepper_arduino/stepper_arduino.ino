/*  EXP 04c - Bipolar stepper through L293D (Arduino Uno)
    WIRING
      D8 -> L293D pin 2 (IN1)    D9 -> pin 7 (IN2)
      D10 -> L293D pin 10 (IN3)  D11 -> pin 15 (IN4)
      L293D pin 16 (VCC1) -> 5V ; pin 8 (VCC2) -> motor supply (+) ; pins 4,5,12,13 -> GND (and supply GND)
      L293D pin 1 (EN1) and pin 9 (EN2) -> 5V
      Motor coil A -> pin 3 (OUT1) and pin 6 (OUT2) ; coil B -> pin 11 (OUT3) and pin 14 (OUT4)
      Uno GND and motor-supply GND must be joined.
    STEPS
      1. Wire as above, plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload (right-arrow).
      4. Motor turns 2 turns, 180 deg, 270 deg, 90 deg, repeating.
    NOTE
      CYCLES_PER_REV = 50 for a 200-step (1.8 deg) motor. 28BYJ-48 motors use 512.
      Motor only buzzes? Swap one coil's two wires.
*/
const int IN1 = 8, IN2 = 9, IN3 = 10, IN4 = 11;
const int LOW_SPEED = 6000, MEDIUM_SPEED = 3000, HIGH_SPEED = 2000;   // us per phase
const bool CLOCKWISE = true, COUNTER_CLOCKWISE = false;

const int CYCLES_PER_REV = 50;                   // 200 steps / 4 phases ; use 512 for 28BYJ-48
// L293D drives each coil as an H-bridge: the two inputs of a coil must DIFFER
const bool SEQ[4][4] = {{1,0,1,0}, {0,1,1,0}, {0,1,0,1}, {1,0,0,1}};

void phase(const bool *p) {
  digitalWrite(IN1, p[0]); digitalWrite(IN2, p[1]);
  digitalWrite(IN3, p[2]); digitalWrite(IN4, p[3]);
}

void cycles(bool dir, int us, int n) {           // n x 4 phases
  for (int i = 0; i < n; i++)
    for (int k = 0; k < 4; k++) {
      phase(SEQ[dir ? k : 3 - k]);
      delayMicroseconds(us);
    }
  delay(10);
}

void turnStepper(bool dir, int us, int angle) { cycles(dir, us, map(angle, 0, 360, 0, CYCLES_PER_REV)); }
void runStepper(bool dir, int us, int turns)   { cycles(dir, us, CYCLES_PER_REV * turns); }

void setup() {
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
}

void loop() {
  runStepper(COUNTER_CLOCKWISE, HIGH_SPEED, 2);    delay(1000);
  turnStepper(CLOCKWISE, MEDIUM_SPEED, 180);       delay(1000);
  turnStepper(COUNTER_CLOCKWISE, HIGH_SPEED, 270); delay(1000);
  turnStepper(CLOCKWISE, LOW_SPEED, 90);           delay(1000);
}
