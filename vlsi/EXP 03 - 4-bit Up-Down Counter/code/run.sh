#!/bin/sh
# needs NVC (brew install nvc); waveform in updown_counter.vcd
nvc --std=08 -a updown_counter.vhd updown_counter_tb.vhd -e updown_counter_tb -r --format=vcd --wave=updown_counter.vcd
