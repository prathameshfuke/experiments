"""EXP 03c - HC-SR04 on Raspberry Pi 3B
WIRING
  HC-SR04 VCC -> pin 2 (5V) ; GND -> pin 6 (GND) ; TRIG -> pin 16 (GPIO23)
  HC-SR04 ECHO -> 1k -> junction ; junction -> pin 18 (GPIO24) ; junction -> 2k -> GND   (5V to 3.3V divider)
STEPS
  1. Power the Pi off, wire as above, power on.
  2. Run:  python3 ultrasonic_pi.py
  3. Distance in cm prints every ~3 s. Ctrl+C to stop.
"""
import time
import RPi.GPIO as GPIO

TRIG, ECHO = 23, 24
CALIBRATION_CM = 0.5

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_cm():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    start = end = time.time()
    timeout = start + 0.05
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start = time.time()
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        end = time.time()
    return (end - start) * 17150                 # 343 m/s, round trip halved

try:
    GPIO.output(TRIG, False)
    time.sleep(2)                                # let the sensor settle
    while True:
        d = round(measure_cm(), 2)
        print(f"Distance: {d - CALIBRATION_CM} cm" if 2 < d < 400 else "Out of range")
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
