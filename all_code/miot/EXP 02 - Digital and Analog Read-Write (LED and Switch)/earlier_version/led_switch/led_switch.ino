/*  EXP 02b - LED controlled by push button (Arduino Uno)
    WIRING
      Button leg 1 -> 5V
      Button leg 2 -> D7  and  D7 -> 10k -> GND (pull-down)
      D12 -> 220R -> LED(+) ; LED(-) -> GND
    STEPS
      1. Wire as above, plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload (right-arrow).
      4. Hold the button: LED on. Release: LED off.
*/
const int SWITCH_PIN = 7;
const int LED_PIN    = 12;

void setup() {
  pinMode(SWITCH_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, digitalRead(SWITCH_PIN));   // pressed = HIGH = LED on
}
