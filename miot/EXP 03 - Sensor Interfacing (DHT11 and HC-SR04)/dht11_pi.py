"""EXP 03b - DHT11 on Raspberry Pi 3B
WIRING
  DHT11 VCC -> pin 2 (5V) ; GND -> pin 6 (GND) ; DATA -> pin 7 (GPIO4)
  (bare 4-pin DHT11: 5.1k between DATA and 5V)
STEPS
  1. pip3 install adafruit-circuitpython-dht ; sudo apt install libgpiod2
  2. Wire as above, run:  python3 dht11_pi.py
  3. Temperature and humidity print every 2 s.
"""
import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4)               # BCM GPIO4

while True:
    try:
        print(f"Temp: {dht.temperature:.1f} C  Humidity: {dht.humidity:.1f} %")
    except RuntimeError as e:                    # DHT occasionally misses a frame
        print("retry:", e)
    time.sleep(2)
