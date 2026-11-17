/*  EXP 07 - HC-05 Bluetooth relay control (Arduino Uno)
    WIRING
      HC-05 VCC -> 5V ; HC-05 GND -> GND
      HC-05 TXD -> D0
      D1 -> 1k -> junction ; junction -> 2.2k -> GND ; junction -> HC-05 RXD   (5V to 3.3V divider)
      Relay VCC -> 5V ; GND -> GND ; IN1 -> D4
      Lamp supply -> relay COM ; relay NO -> lamp -> supply return   (low-voltage lamp only)
    STEPS
      1. Unplug HC-05 TXD and RXD from D0/D1 (they share the USB serial line).
      2. Wire as above, plug the Uno into the PC with USB.
      3. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      4. Click Upload (right-arrow).
      5. Plug HC-05 TXD/RXD back in. On the phone: pair with HC-05 (PIN 1234 or 0000), open 'Arduino Bluetooth Controller'.
      6. Send 1: relay on. Send 0: relay off.
    NOTE
      Relay clicks the wrong way? Swap RELAY_ON and RELAY_OFF at the top of the file.
*/
#define RELAY_ON  LOW
#define RELAY_OFF HIGH
const int RELAY_PIN = 4;

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, RELAY_OFF);            // off after reset
  Serial.begin(9600);                            // HC-05 data mode baud
  Serial.println("Send 1 = ON, 0 = OFF");
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '1')      { digitalWrite(RELAY_PIN, RELAY_ON);  Serial.println("Bulb ON"); }
    else if (c == '0') { digitalWrite(RELAY_PIN, RELAY_OFF); Serial.println("Bulb OFF"); }
  }
}
