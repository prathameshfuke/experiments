/*  EXP 09C - MFRC522 RFID scan uploaded by ESP8266 to ThingSpeak (Arduino Uno)
    WIRING
      MFRC522: 3.3V -> 3.3V ; GND -> GND ; RST -> D9 ; SDA(SS) -> D10 ; MOSI -> D11 ; MISO -> D12 ; SCK -> D13 ; IRQ unused
      ESP8266-01: VCC and CH_PD -> 3.3V ; GND -> GND ; TX -> D6
      D7 -> 1k -> junction ; junction -> 2.2k -> GND ; junction -> ESP8266 RX   (5V to 3.3V divider)
    STEPS
      1. Tools > Manage Libraries > install 'MFRC522'.
      2. One time: set the ESP to 9600 baud (send AT+UART_DEF=9600,8,1,0,0 at its current baud).
      3. Fill in WIFI_SSID, WIFI_PASSWORD, THINGSPEAK_WRITE_KEY below.
      4. Wire as above, plug the Uno into the PC with USB.
      5. Arduino IDE: File > Open this .ino. Tools > Board > Arduino Uno. Tools > Port > your Uno.
      6. Click Upload (right-arrow).
      7. Serial Monitor (9600): wait for 'Scan a card...', tap a tag, see 'Card: <id>', check ThingSpeak field1.
    NOTE
      The Uno 3.3V pin gives only ~50 mA; the ESP8266 may reset. Use an AMS1117 3.3V module if it does.
*/
#include <SoftwareSerial.h>
#include <SPI.h>
#include <MFRC522.h>

const int ESP_RX = 6, ESP_TX = 7;                // Uno-side pins (ESP TX -> D6, ESP RX <- D7)
const int RST_PIN = 9, SS_PIN = 10;

const char AP[]   = "WIFI_SSID";
const char PASS[] = "WIFI_PASSWORD";
const char API[]  = "THINGSPEAK_WRITE_KEY";
const char HOST[] = "api.thingspeak.com";

SoftwareSerial esp(ESP_RX, ESP_TX);
MFRC522 rfid(SS_PIN, RST_PIN);

bool sendCommand(const String &cmd, const char *expect, int tries = 5) {
  for (int i = 0; i < tries; i++) {
    esp.println(cmd);
    if (esp.find((char *)expect)) { Serial.println(cmd + " -> OK"); return true; }
  }
  Serial.println(cmd + " -> FAIL");
  return false;
}

void upload(unsigned long tag) {
  String get = String("GET /update?api_key=") + API + "&field1=" + tag;
  sendCommand("AT+CIPMUX=1", "OK");
  if (sendCommand(String("AT+CIPSTART=0,\"TCP\",\"") + HOST + "\",80", "OK", 3)) {
    sendCommand("AT+CIPSEND=0," + String(get.length() + 2), ">", 3);
    esp.println(get);
    delay(1500);
    sendCommand("AT+CIPCLOSE=0", "OK", 2);
  }
}

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  esp.begin(9600);
  esp.setTimeout(3000);
  sendCommand("AT", "OK");
  sendCommand("AT+CWMODE=1", "OK");
  sendCommand(String("AT+CWJAP=\"") + AP + "\",\"" + PASS + "\"", "OK", 3);
  Serial.println("Scan a card...");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  unsigned long tag = 0;
  for (byte i = 0; i < rfid.uid.size && i < 4; i++) tag = (tag << 8) | rfid.uid.uidByte[i];
  Serial.print("Card: "); Serial.println(tag);
  rfid.PICC_HaltA();
  upload(tag);
  delay(1000);
}
