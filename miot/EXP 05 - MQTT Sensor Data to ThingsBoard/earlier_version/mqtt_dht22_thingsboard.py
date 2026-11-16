"""EXP 05 - DHT22 to ThingsBoard over MQTT (Raspberry Pi)
WIRING
  DHT22 VCC -> pin 2 (5V) ; GND -> pin 6 (GND) ; DATA -> pin 16 (GPIO23)
  DHT22 DATA -> 10k -> 5V (pull-up, not needed on a 3-pin module)
STEPS
  1. pip3 install paho-mqtt adafruit-circuitpython-dht
  2. ThingsBoard: Devices > add device 'DHT22 Demo Device' > Copy access token. Put it in ACCESS_TOKEN below.
  3. Wire as above, run:  python3 mqtt_dht22_thingsboard.py
  4. ThingsBoard: device > Latest telemetry shows temperature and humidity.
"""
import json
import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt

THINGSBOARD_HOST = "demo.thingsboard.io"          # or "localhost"
ACCESS_TOKEN = "YOUR_DEVICE_ACCESS_TOKEN"
INTERVAL = 2                                      # s, DHT22 cannot go faster

dht = adafruit_dht.DHT22(board.D23)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

try:
    while True:
        try:
            data = {"temperature": round(dht.temperature, 2), "humidity": round(dht.humidity, 2)}
        except RuntimeError as e:
            print("retry:", e)
            time.sleep(INTERVAL)
            continue
        print(data)
        client.publish("v1/devices/me/telemetry", json.dumps(data), 1)
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
