#!/usr/bin/env bash

# If not uploading try:
# arduino-cli upload -b arduino:avr:nano -p /dev/ttyUSB0 arduino.ino -v
# arduino-cli upload -b arduino:avr:diecimila:cpu=atmega168 -p /dev/ttyUSB0 arduino.ino -v
# arduino-cli upload -b arduino:avr:diecimila:cpu=atmega328 -p /dev/ttyUSB0 arduino.ino -v

arduino-cli compile -b arduino:avr:diecimila:cpu=atmega328 arduino.ino --clean
if [ "$1" == "-v" ]
    then
        arduino-cli upload -b arduino:avr:diecimila:cpu=atmega328 -p /dev/ttyUSB0 arduino.ino -v
    else
        arduino-cli upload -b arduino:avr:diecimila:cpu=atmega328 -p /dev/ttyUSB0 arduino.ino
fi