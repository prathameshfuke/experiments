/*  EXP 02a - LED blink (Arduino Uno)
    WIRING
      D13 -> 330R -> LED(+) ; LED(-) -> GND   (D13 also drives the on-board LED 'L', so the LED is optional)
    STEPS
      1. Wire as above, plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload (right-arrow).
      4. LED turns on 1 s, off 1 s.
*/
void setup() { pinMode(LED_BUILTIN, OUTPUT); }

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}
