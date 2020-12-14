#!/usr/bin/python
# -*- coding: utf-8 -*-


# Plastic Sense is a project by Jerry de Vos
# written on 16 nov 2020
# it is quite shitty code i know
# it is based on the PipyADC Lib (https://github.com/ul-gh/PiPyADC)
# used to detect what type of plastic a product is made of
import sys
import os
import time
import csv
import Plastic_Sense_Config as conf
from Plastic_Sense_Functions import ADS1255

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")

ads = ADS1255()
#turn off leds on startup
for led in range(conf.number_of_leds):    
        ads.set_led_off()                     #choose which pin to light up
        time.sleep(0.05)

#take a measurement
def do_measurement_all_off(): 
    for led in range(conf.number_of_leds):    
        ads.set_led_off()                     #choose which pin to light up
        time.sleep(0.05)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        pre_measurements.append(raw_value)
        time.sleep(0.05)
        ads.set_led_off()                       #all lights off
        time.sleep(0.05)    
        print("turning on LED", led+1, "Measured value:",raw_value)
        
def do_measurement(): 
    for led in range(conf.number_of_leds):    
        ads.set_led_on(led)                     #choose which pin to light up
        time.sleep(0.05)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        all_measurements.append(raw_value)
        time.sleep(0.05)
        ads.set_led_off()                       #all lights off
        time.sleep(0.05)    
        print("turning on LED", led+1, "Measured value:",raw_value)
    
    #print(all_measurements)


# do a self calibration and read chip ID
print("starting, welcome to the plastic scanner")
ads.cal_self()
chip_ID = ads.chip_ID()
print("ID value of: ",chip_ID)

# Start data acquisition
while True:
    print("do you want to take a measurement? fill in type of plastic 'PE,PP,PS,PET,PVC,other,unknown'")
    plastic_type = input()
    print("color object")
    object_color = input()    
    print("name object")
    object_number = input()
    print("type 'y' for measurement")
    pre = input()
    if pre == "y":
        pre_measurements = [plastic_type, object_color, object_number, "pre", time.strftime("%Y-%m-%d-%H:%M:%S")]
        do_measurement_all_off()
        with open('testresults_07dec.csv', mode='a') as test_results:
            test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_results.writerow(pre_measurements)
        all_measurements = [plastic_type, object_color, object_number, "actual", time.strftime("%Y-%m-%d-%H:%M:%S")]
        do_measurement()
        with open('testresults_07dec.csv', mode='a') as test_results:
            test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_results.writerow(all_measurements)
#     
#     print("type 'y' for post measurement")
#     post = input()
#     if post == "y":
#         all_measurements = [plastic_type,"post", time.strftime("%Y-%m-%d-%H:%M:%S")]
#         do_measurement()
#         with open('testresults.csv', mode='a') as test_results:
#             test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#             test_results.writerow(all_measurements)




