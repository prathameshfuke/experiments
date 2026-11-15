"""EXP 04b - 2-channel relay module on Raspberry Pi 3B
WIRING
  Relay VCC -> pin 2 (5V) ; GND -> pin 6 (GND) ; IN1 -> pin 16 (GPIO23) ; IN2 -> pin 18 (GPIO24)
  Lamp supply -> relay COM ; relay NO -> lamp   (low-voltage lamp only)
STEPS
  1. Power the Pi off, wire as above, power on.
  2. Run:  python3 relay_pi.py
  3. Relays click in a pattern. Ctrl+C to stop.
NOTE
  Most modules are active LOW on a 3.3V GPIO: if on/off looks swapped, use GPIO.output(pin, not value).
"""
import time
import RPi.GPIO as GPIO

IN1, IN2 = 16, 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup([IN1, IN2], GPIO.OUT, initial=False)

try:
    while True:
        for _ in range(5):                       # alternate
            GPIO.output(IN1, True);  time.sleep(0.1)
            GPIO.output(IN1, False); GPIO.output(IN2, True); time.sleep(0.1)
            GPIO.output(IN2, False)
        GPIO.output([IN1, IN2], True)            # both on
        for _ in range(4):                       # relay 1 flashes
            GPIO.output(IN1, True);  time.sleep(0.05)
            GPIO.output(IN1, False); time.sleep(0.05)
        GPIO.output(IN1, True)
        for _ in range(4):                       # relay 2 flashes
            GPIO.output(IN2, True);  time.sleep(0.05)
            GPIO.output(IN2, False); time.sleep(0.05)
        GPIO.output(IN2, True)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
