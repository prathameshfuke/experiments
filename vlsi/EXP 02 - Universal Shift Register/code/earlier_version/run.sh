#!/bin/sh
# needs NVC (brew install nvc); waveform in usr.vcd
nvc --std=08 -a usr.vhd usr_tb.vhd -e usr_tb -r --format=vcd --wave=usr.vcd
