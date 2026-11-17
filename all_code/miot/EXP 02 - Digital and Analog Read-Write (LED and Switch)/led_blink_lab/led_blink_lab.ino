/*  EXP 02a - LED blink with the internal LED (Arduino Uno)
    Source: lab code PDF 'MIOT all codes'.
    WIRING
      Nothing to wire: LED_BUILTIN is pin 13 (on-board LED 'L').
    STEPS
      1. Plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload.
      4. The on-board LED blinks 1 s on, 1 s off.
*/

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);              // pin 13
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);           // LED on
  delay(1000);
  digitalWrite(LED_BUILTIN, LOW);            // LED off
  delay(1000);
}
