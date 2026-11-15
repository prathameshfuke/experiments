#!/bin/sh
# needs NVC (brew install nvc); waveform in keypad.vcd
nvc --std=08 -a keypad.vhd keypad_tb.vhd -e keypad_tb -r --format=vcd --wave=keypad.vcd
