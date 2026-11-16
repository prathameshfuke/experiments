#!/bin/sh
# needs NVC (brew install nvc); waveform in alu4bit.vcd
nvc --std=08 -a alu4bit.vhd alu4bit_tb.vhd -e alu4bit_tb -r --format=vcd --wave=alu4bit.vcd
