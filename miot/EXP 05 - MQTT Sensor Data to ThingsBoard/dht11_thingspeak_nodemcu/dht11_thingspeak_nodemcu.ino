/*  EXP 05 - NodeMCU (ESP8266) reads DHT11 and uploads to ThingSpeak over Wi-Fi
    Source: lab code PDF 'MIOT all codes'.
    WIRING
      DHT11 VCC -> 3V3 ; GND -> GND ; DATA -> D3 (GPIO0) + 10k pull-up to 3V3
      (use a 3-pin DHT11 module if you have one: it already has the pull-up)
    STEPS
      1. Add the ESP8266 board URL (IDE Preferences): http://arduino.esp8266.com/stable/package_esp8266com_index.json, then Board Manager > install 'esp8266'.
      2. Library Manager > install 'DHT sensor library' (Adafruit) and 'Adafruit Unified Sensor'.
      3. ThingSpeak: new channel, Field1 = Temperature, Field2 = Humidity, copy the Write API key.
      4. Fill in ssid, password and writeAPI below. Tools > Board > NodeMCU 1.0 (ESP-12E). Choose the port. Upload.
      5. Serial Monitor (115200): connects to Wi-Fi, prints readings, 'Update sent to ThingSpeak.' every 20 s. Check the channel chart.
    NOTE
      Do not publish your real Wi-Fi password or write key (the PDF example had a tutorial's values; use your own).
      GPIO0 (D3) is a boot pin: if upload fails, unplug the DHT data wire during upload.
*/

#include <ESP8266WiFi.h>
#include <DHT.h>

// -------------------- USER SETTINGS --------------------
const char* ssid     = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// ThingSpeak: Field1 = Temperature (C), Field2 = Humidity (%RH)
const char* server   = "api.thingspeak.com";
const char* writeAPI = "YOUR_THINGSPEAK_WRITE_API_KEY";

// Sensor
#define DHTPIN   0                             // GPIO0 (NodeMCU label D3)
#define DHTTYPE DHT11
// -------------------------------------------------------

DHT dht(DHTPIN, DHTTYPE);
WiFiClient client;

const unsigned long UPLOAD_INTERVAL_MS = 20000;   // ThingSpeak needs >= 15 s
unsigned long lastUpload = 0;

void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  uint8_t tries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
    if (++tries >= 60) {                       // about 30 s timeout
      Serial.println("\nWiFi connect timeout. Restarting...");
      ESP.restart();
    }
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  delay(50);
  Serial.println();
  Serial.println("DHT11 + NodeMCU -> ThingSpeak");
  dht.begin();
  connectWiFi();
}

bool postToThingSpeak(float temperatureC, float humidity) {
  String postBody = "field1=" + String(temperatureC, 1) + "&field2=" + String(humidity, 1);

  if (!client.connect(server, 80)) {
    Serial.println("Connection to ThingSpeak failed.");
    return false;
  }

  client.print(String("POST /update HTTP/1.1\r\n") +
               "Host: " + String(server) + "\r\n" +
               "Connection: close\r\n" +
               "X-THINGSPEAKAPIKEY: " + String(writeAPI) + "\r\n" +
               "Content-Type: application/x-www-form-urlencoded\r\n" +
               "Content-Length: " + String(postBody.length()) + "\r\n\r\n" +
               postBody + "\r\n");

  unsigned long start = millis();
  while (client.connected() && millis() - start < 3000) {
    while (client.available()) {
      String line = client.readStringUntil('\n');
      if (line.length() == 1 && line[0] == '\r') {   // blank line before the body
        String body = client.readString();
        Serial.print("ThingSpeak response (entry ID or 0): ");
        Serial.println(body);
        break;
      }
    }
  }
  client.stop();
  return true;
}

void loop() {
  if (millis() - lastUpload < UPLOAD_INTERVAL_MS) {
    delay(50);
    return;
  }

  float h = dht.readHumidity();
  float t = dht.readTemperature();             // Celsius

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT11. Retrying next cycle...");
    lastUpload = millis();
    return;
  }

  Serial.print("Temperature: ");
  Serial.print(t, 1);
  Serial.print(" C, Humidity: ");
  Serial.print(h, 1);
  Serial.println(" %RH");

  if (postToThingSpeak(t, h)) {
    Serial.println("Update sent to ThingSpeak.");
  } else {
    Serial.println("Update failed.");
  }
  lastUpload = millis();
}
