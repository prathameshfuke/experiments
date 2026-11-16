#!/bin/sh
# needs NVC (brew install nvc); waveform in fifo.vcd
nvc --std=08 -a fifo.vhd fifo_tb.vhd -e fifo_tb -r --format=vcd --wave=fifo.vcd
