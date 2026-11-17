/*  EXP 09D - NodeMCU relay control from the Blynk app (NodeMCU, not Uno)
    WIRING
      Relay VCC -> VIN (5V) ; GND -> GND
      Relay IN1 -> D1 ; IN2 -> D2
      Lamp supply -> relay COM ; relay NO -> lamp   (low-voltage lamp only)
    STEPS
      1. Arduino IDE: File > Preferences > add  http://arduino.esp8266.com/stable/package_esp8266com_index.json  to Additional Boards URLs.
      2. Tools > Board Manager > install 'esp8266'. Tools > Manage Libraries > install 'Blynk'.
      3. Blynk app: new project, board NodeMCU, copy the Auth Token into 'auth' below. Add 2 buttons: V1 and V2 (switch mode).
      4. Fill in ssid and pass. Tools > Board > NodeMCU 1.0 (ESP-12E). Choose the port. Upload.
      5. Tap the buttons in the app: relays click.
*/
#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

char auth[] = "YourAuthToken";
char ssid[] = "YourNetworkName";
char pass[] = "YourPassword";

const int RELAY1 = D1, RELAY2 = D2;
#define RELAY_ON  LOW
#define RELAY_OFF HIGH

BLYNK_WRITE(V1) { digitalWrite(RELAY1, param.asInt() ? RELAY_ON : RELAY_OFF); }
BLYNK_WRITE(V2) { digitalWrite(RELAY2, param.asInt() ? RELAY_ON : RELAY_OFF); }

void setup() {
  Serial.begin(9600);
  pinMode(RELAY1, OUTPUT); digitalWrite(RELAY1, RELAY_OFF);
  pinMode(RELAY2, OUTPUT); digitalWrite(RELAY2, RELAY_OFF);
  Blynk.begin(auth, ssid, pass);
}

void loop() { Blynk.run(); }                     // no delay() here
