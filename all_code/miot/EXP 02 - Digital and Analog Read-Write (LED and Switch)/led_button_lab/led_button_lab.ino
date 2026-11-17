/*  EXP 02b - External LED controlled by a push button (Arduino Uno)
    Source: lab code PDF 'MIOT all codes'.
    WIRING
      Button leg 1 -> 5V
      Button leg 2 -> D7  and  D7 -> 10k -> GND (pull-down)
      D8 -> 220R -> LED(+) ; LED(-) -> GND
    STEPS
      1. Plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload.
      4. Hold the button: LED on. Release: LED off.
*/

#define LED_PIN 8
#define BUTTON_PIN 7

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
}

void loop() {
  if (digitalRead(BUTTON_PIN) == HIGH) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
}
