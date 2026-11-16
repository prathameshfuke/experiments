/*  EXP 04d - HC-SR04 distance sensor (Arduino Uno)
    WIRING
      HC-SR04 VCC -> 5V ; GND -> GND ; TRIG -> D8 ; ECHO -> D7
    STEPS
      1. Wire as above, plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload (right-arrow).
      4. Tools > Serial Monitor (9600): distance in cm. Move your hand in front of it.
*/
const int TRIG_PIN = 8;
const int ECHO_PIN = 7;

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long us = pulseIn(ECHO_PIN, HIGH, 30000);      // 30 ms timeout
  if (us) Serial.println((us / 2) / 29.1);       // cm
  else    Serial.println("no echo");
  delay(100);
}
