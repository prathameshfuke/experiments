"""EXP 04a - 28BYJ-48 stepper with ULN2003 board on Raspberry Pi 3B
WIRING
  ULN2003 IN1 -> pin 7 ; IN2 -> pin 11 ; IN3 -> pin 13 ; IN4 -> pin 15
  ULN2003 '+' -> pin 2 (5V) ; '-' -> pin 6 (GND)
  Motor plug -> ULN2003 white socket
STEPS
  1. Power the Pi off, wire as above, power on.
  2. Run:  python3 stepper_pi.py
  3. The motor makes one full turn, then the script ends.
"""
import time
import RPi.GPIO as GPIO

PINS = [7, 11, 13, 15]
HALFSTEP = [[1,0,0,0], [1,1,0,0], [0,1,0,0], [0,1,1,0],
            [0,0,1,0], [0,0,1,1], [0,0,0,1], [1,0,0,1]]

GPIO.setmode(GPIO.BOARD)
for p in PINS:
    GPIO.setup(p, GPIO.OUT)
    GPIO.output(p, 0)

try:
    for _ in range(512):                         # one full revolution
        for step in HALFSTEP:
            for p, v in zip(PINS, step):
                GPIO.output(p, v)
            time.sleep(0.001)
finally:
    GPIO.cleanup()
