"""EXP 08b - Raspberry Pi receives Arduino data through XBee
WIRING
  XBee USB adapter -> any Pi USB port (shows up as /dev/ttyUSB0)
STEPS
  1. pip3 install pyserial
  2. Both XBees set up in XCTU: same PAN ID, 9600 baud, transparent mode.
  3. Run:  python3 xbee_rx_pi.py   (check the port with:  ls /dev/ttyUSB*)
  4. Output: 'Arduino -> Pi: ADC=xxx' every second.
"""
import serial

PORT, BAUD = "/dev/ttyUSB0", 9600

with serial.Serial(PORT, BAUD, timeout=2) as port:
    try:
        while True:
            line = port.readline().decode("utf-8", errors="replace").strip()
            if line:
                print("Arduino -> Pi:", line)
    except KeyboardInterrupt:
        pass
