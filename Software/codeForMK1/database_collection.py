#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""  Run this if you want to measure known plastics to build a calibration database   """

import sys
import os
import time
import csv
import Plastic_Sense_Config as conf
from Plastic_Sense_Functions import ADS1256

##stuff for oled
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
WIDTH = 128
HEIGHT = 64 # Change to 64 if needed
BORDER = 0
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3D)
#stuff for button
button = digitalio.DigitalInOut(board.D13)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")

ads = ADS1256()


#take a measurement
def do_measurement():

    for led in range(conf.number_of_leds):    
        ads.set_led_on(led)                     #choose which pin to light up
        time.sleep(0.2)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        all_measurementsactual.append(raw_value)
        time.sleep(0.2)
        ads.set_led_off()                       #all lights off
        time.sleep(0.2)    
        print("turning on LED", led+1, "Measured value:",raw_value)
        update_screen(".", (2*led+94), 0)

def do_measurement_light_off(type):
    for led in range(conf.number_of_leds):    
        ads.set_led_off()                     #choose which pin to light up
        time.sleep(0.05)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        if type == "pre":
            all_measurementspre.append(raw_value)
            update_screen(".", (2*led+78), 0)
        if type == "post":
            all_measurementspost.append(raw_value)
            update_screen(".", (2*led+110), 0)
        time.sleep(0.05)
        ads.set_led_off()                       #all lights off
        time.sleep(0.05)    
        print("turning on LED", led+1, "Measured value:",raw_value)
        

def wait_for_button_press():
    while True:
        first = button.value
        time.sleep(0.01)
        second = button.value
        if first and not second:
            print('Button released!')
            return
        elif not first and second:
            print('Button pressed!')
            return

def update_screen(text,x,y):
    draw.text((x,y),text,font=font,fill=255,)
    oled.image(image)
    oled.show()


##############start of the program

print("starting, welcome to the database collection script for the plastic scanner")
# do a self calibration and read chip ID
ads.cal_self()
id = ads.chip_ID
print("ID value of: ",id)
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()




################ loop
while True:
    oled.fill(0) #clear screen
    oled.show()
    update_screen("welcome", 0, 0)
    print("do you want to take a measurement? fill in type of plastic 'PE,PP,PS,PET,PVC,other,unknown'")
    plastic_type = input()
    update_screen("Press ---->", 0, 10)
    print("press button to continue")
    wait_for_button_press()
    update_screen("starting", 0, 20)
    update_screen(".", (78), -3)
    update_screen(".", (94), -3)
    update_screen(".", (110), -3)
    update_screen(".", (126), -3)

    all_measurementspre = [plastic_type,"pre", time.strftime("%Y-%m-%d-%H:%M:%S")]
    do_measurement_light_off("pre")
    all_measurementsactual = [plastic_type,"actual", time.strftime("%Y-%m-%d-%H:%M:%S")]
    do_measurement()
    all_measurementspost = [plastic_type,"post", time.strftime("%Y-%m-%d-%H:%M:%S")]
    do_measurement_light_off("post")
    update_screen("finished", 0, 30)
    with open('testresults.csv', mode='a') as test_results:
        test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_results.writerow(all_measurementspre)
        test_results.writerow(all_measurementsactual)
        test_results.writerow(all_measurementspost)
    print("Measure again? y/n")
    again = input()
    if again == "n":
        oled.fill(0) #clear screen
        oled.show()
        exit()



