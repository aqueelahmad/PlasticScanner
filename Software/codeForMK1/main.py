#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Plastic Sense is a project by Jerry de Vos
# written on 16 nov 2020
# it is quite shitty code i know
# it is based on the PipyADC Lib (https://github.com/ul-gh/PiPyADC)
# used to detect what type of plastic a product is made of
import sys
import os
import time
import Plastic_Sense_Config as conf
from Plastic_Sense_Functions import ADS1256

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")

ads = ADS1256()

#take a measurement
def do_measurement():
    for led in range(conf.number_of_leds):    
        ads.set_led_on(led)                     #choose which pin to light up
        time.sleep(1)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        time.sleep(0)
        ads.set_led_off()                       #all lights off
        time.sleep(0)    
        print("turning on LED", led+1, "Measured value:",raw_value)



# do a self calibration and read chip ID
print("starting, welcome to the plastic scanner")
ads.cal_self()
id = ads.chip_ID
print("ID value of: ",id)

# Start data acquisition
while True:
    print("do you want to take a measurement? type 'y'")
    answer = input()
    if answer == "y":
        do_measurement()
