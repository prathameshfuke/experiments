/*  EXP 07 - HC-05 Bluetooth switch for an external LED (Arduino Uno)
    Source: lab code PDF 'MIOT all codes'.
    WIRING
      HC-05 VCC -> 5V ; GND -> GND ; TXD -> D0
      D1 -> 1k -> junction ; junction -> 2.2k -> GND ; junction -> HC-05 RXD   (5V to 3.3V divider)
      D5 -> 220R -> LED(+) ; LED(-) -> GND
    STEPS
      1. Unplug HC-05 TXD and RXD from D0/D1 (shared with USB).
      2. Plug the Uno into the PC with USB.
      3. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      4. Click Upload.
      5. Plug the HC-05 wires back in.
      6. Phone: pair with HC-05 (PIN 1234 or 0000), open a Bluetooth terminal / switch app.
      7. Send SWITCH1_ON: LED on. Send SWITCH1_OFF: LED off.
    NOTE
      Send the text exactly, with no newline or carriage return added by the app, or the comparison fails.
      readString() waits up to 1 s for more data, so the LED reacts after about a second.
*/

int led1 = 5;                                  // LED connected to pin 5

void setup() {
  Serial.begin(9600);                          // HC-05 serial link
  pinMode(led1, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {                // data from Bluetooth
    String command = Serial.readString();

    if (command.equals("SWITCH1_ON")) {
      Serial.print("LED 1 is ON");
      digitalWrite(led1, HIGH);
    }
    else if (command.equals("SWITCH1_OFF")) {
      Serial.print("LED 1 is OFF");
      digitalWrite(led1, LOW);
    }
  }
}
