"""EXP 09A - DHT11 weather data to ThingSpeak and e-mail (Raspberry Pi)
WIRING
  DHT11 VCC -> pin 2 (5V) ; GND -> pin 6 (GND) ; DATA -> pin 16 (GPIO23)
  (bare 4-pin DHT11: 5.1k between DATA and 5V)
STEPS
  1. pip3 install adafruit-circuitpython-dht
  2. ThingSpeak: new channel, field1 = Humidity, field2 = Temperature, copy the Write API key.
  3. Gmail: turn on 2-step verification, create an App Password.
  4. Run:  THINGSPEAK_KEY=... GMAIL_USER=... GMAIL_APP_PASSWORD=... MAIL_TO=... python3 weather_monitor.py
  5. Every 15 s: data appears on ThingSpeak and an e-mail arrives.
"""
import os
import smtplib
import time
import urllib.request
from email.mime.text import MIMEText
import board
import adafruit_dht

KEY = os.environ["THINGSPEAK_KEY"]
USER, APP_PASS, MAIL_TO = os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"], os.environ["MAIL_TO"]
INTERVAL = 15                                     # ThingSpeak free tier minimum
CHANNEL_URL = "https://thingspeak.com/channels/<CHANNEL_ID>"

dht = adafruit_dht.DHT11(board.D23)

def send_mail(t, h):
    msg = MIMEText(f"Temperature {t} C, Humidity {h} %\nData log: {CHANNEL_URL}")
    msg["Subject"], msg["From"], msg["To"] = "Weather report", USER, MAIL_TO
    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(USER, APP_PASS)
        s.send_message(msg)

while True:
    try:
        t, h = dht.temperature, dht.humidity
        urllib.request.urlopen(f"https://api.thingspeak.com/update?api_key={KEY}&field1={h}&field2={t}").read()
        send_mail(t, h)
        print(f"sent T={t} H={h}")
    except RuntimeError as e:                     # DHT frame error
        print("retry:", e)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print("error:", e)
    time.sleep(INTERVAL)
