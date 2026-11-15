/*  EXP 02c - Potentiometer controls LED brightness (Arduino Uno)
    WIRING
      Pot outer legs -> 5V and GND ; pot middle leg -> A0
      D9 -> 220R -> LED(+) ; LED(-) -> GND
    STEPS
      1. Wire as above, plug the Uno into the PC with USB.
      2. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      3. Click Upload (right-arrow).
      4. Tools > Serial Monitor (9600): raw value 0-1023 prints.
      5. Turn the pot: LED dims and brightens.
*/
const int POT_PIN = A0;
const int LED_PIN = 9;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int raw = analogRead(POT_PIN);                 // 0..1023
  analogWrite(LED_PIN, raw / 4);                 // 0..255
  Serial.println(raw);
  delay(100);
}
