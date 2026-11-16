/*  EXP 03a - DHT11 temperature and humidity (Arduino Uno)
    WIRING
      DHT11 VCC -> 5V ; DHT11 GND -> GND ; DHT11 DATA -> D2
      (bare 4-pin DHT11: also 10k between DATA and 5V)
    STEPS
      1. Tools > Manage Libraries > install 'SimpleDHT'.
      2. Wire as above, plug the Uno into the PC with USB.
      3. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      4. Click Upload (right-arrow).
      5. Tools > Serial Monitor (9600): temperature and humidity every 1.5 s.
*/
#include <SimpleDHT.h>

const int DHT_PIN = 2;
SimpleDHT11 dht11(DHT_PIN);

void setup() { Serial.begin(9600); }

void loop() {
  byte t = 0, h = 0;
  int err = dht11.read(&t, &h, NULL);
  if (err != SimpleDHTErrSuccess) {
    Serial.print("DHT11 read failed, err=");
    Serial.println(err);
  } else {
    Serial.print((int)t); Serial.print(" *C, ");
    Serial.print((int)h); Serial.println(" %RH");
  }
  delay(1500);                                   // DHT11 max rate 1 Hz
}
