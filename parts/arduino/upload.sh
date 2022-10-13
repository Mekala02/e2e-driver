#!/usr/bin/env bash

arduino-cli compile -b arduino:avr:diecimila:cpu=atmega168 arduino.ino --clean
if [ "$1" == "-v" ]
    then
        arduino-cli upload -b arduino:avr:diecimila:cpu=atmega168 -p /dev/ttyUSB0 arduino.ino -v
    else
        arduino-cli upload -b arduino:avr:diecimila:cpu=atmega168 -p /dev/ttyUSB0 arduino.ino
fi