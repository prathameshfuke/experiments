"""EXP 09B - EM-18 RFID attendance to ThingSpeak (Raspberry Pi)
WIRING
  EM-18 VCC -> pin 2 (5V) ; GND -> pin 6 (GND)
  EM-18 TX -> 1k -> junction ; junction -> pin 10 (GPIO15, RXD) ; junction -> 2k -> GND   (5V to 3.3V divider)
  (find the VCC / GND / TX pins from the labels on your EM-18 board)
STEPS
  1. pip3 install pyserial
  2. sudo raspi-config > Interface Options > Serial Port: login shell = No, serial hardware = Yes. Reboot.
  3. ThingSpeak: new channel with field1, copy the Write API key into KEY below.
  4. Run:  python3 rfid_em18_pi.py
  5. Tap a card: 12-character tag prints and field1 updates (max once per 15 s).
"""
import time
import urllib.parse
import urllib.request
import serial

KEY = "YOUR_THINGSPEAK_WRITE_KEY"
PORT, BAUD = "/dev/serial0", 9600
MIN_GAP = 15                                      # s between ThingSpeak updates

port = serial.Serial(PORT, BAUD, timeout=1.0)
last_post = 0.0

try:
    while True:
        tag = port.read(12).decode("ascii", errors="ignore").strip()   # EM-18 sends 12 ASCII chars
        if len(tag) != 12:
            continue
        print("Tag:", tag)
        if time.time() - last_post >= MIN_GAP:
            try:
                q = urllib.parse.urlencode({"api_key": KEY, "field1": tag})
                urllib.request.urlopen(f"https://api.thingspeak.com/update?{q}", timeout=10).read()
                last_post = time.time()
            except OSError as e:
                print("upload failed:", e)
except KeyboardInterrupt:
    pass
finally:
    port.close()
