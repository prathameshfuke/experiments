/*  EXP 08a - Arduino sends ADC reading through XBee (Arduino Uno)
    WIRING
      XBee adapter VCC -> 3.3V ; GND -> GND
      XBee DOUT -> D0
      D1 -> 1k -> junction ; junction -> 2.2k -> GND ; junction -> XBee DIN   (5V to 3.3V divider)
      Pot outer legs -> 5V and GND ; pot middle leg -> A0
    STEPS
      1. Both XBees set up in XCTU: same PAN ID, 9600 baud, transparent mode.
      2. Unplug XBee from D0/D1 while uploading.
      3. Wire as above, plug the Uno into the PC with USB.
      4. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      5. Click Upload (right-arrow).
      6. Plug XBee back in. Run xbee_rx_pi.py on the Pi: 'ADC=...' appears every second.
*/
void setup() { Serial.begin(9600); }

void loop() {
  Serial.print("ADC=");
  Serial.println(analogRead(A0));
  delay(1000);
}
