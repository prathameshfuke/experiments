/*  EXP 03 - DHT11 temperature and humidity (Arduino Uno, library 'DHT11')
    Source: lab code PDF 'MIOT all codes'.
    WIRING
      DHT11 VCC -> 5V ; GND -> GND ; DATA -> D2
      (bare 4-pin DHT11: also 10k between DATA and 5V)
    STEPS
      1. Tools > Manage Libraries > search 'DHT11' (by Dhruba Saha) > Install.
      2. Plug the Uno into the PC with USB.
      3. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      4. Click Upload.
      5. Tools > Serial Monitor (9600 baud): temperature and humidity print.
*/

#include <DHT11.h>

DHT11 dht11(2);                                // sensor on digital pin 2

void setup() {
  Serial.begin(9600);
  // dht11.setDelay(500);                      // optional: delay between readings (ms)
}

void loop() {
  int temperature = 0;
  int humidity = 0;

  int result = dht11.readTemperatureHumidity(temperature, humidity);

  if (result == 0) {
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" C\tHumidity: ");
    Serial.print(humidity);
    Serial.println(" %");
  } else {
    Serial.println(DHT11::getErrorString(result));
  }
}
