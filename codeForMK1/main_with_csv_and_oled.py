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
button = digitalio.DigitalInOut(board.D12)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.DOWN

if not os.path.exists("/dev/spidev0.1"):
    raise IOError("Error: No SPI device. Check settings in /boot/config.txt")

ads = ADS1256()

#take a measurement
ddef do_measurement():
    
    for led in range(conf.number_of_leds):    
        ads.set_led_on(led)                     #choose which pin to light up
        time.sleep(0.05)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        all_measurements.append(raw_value)
        time.sleep(0.05)
        ads.set_led_off()                       #all lights off
        time.sleep(0.05)    
        print("turning on LED", led+1, "Measured value:",raw_value)

def do_measurement_light_off():
    for led in range(conf.number_of_leds):    
        ads.set_led_off()                     #choose which pin to light up
        time.sleep(0.05)
        raw_value = ads.read_and_next_is(1)  #for cyclic single-channel reads
        all_measurements.append(raw_value)
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


# do a self calibration and read chip ID
print("starting, welcome to the plastic scanner")
ads.cal_self()
chip_ID = ads.chip_ID()
print("ID value of: ",chip_ID)

oled.fill(0)
oled.show()
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# Start data acquisition
while True:
    print("do you want to take a measurement? fill in type of plastic 'PE,PP,PS,PET,PVC,other,unknown'")
    plastic_type = input()
    
    text = "press for pre measure"
    draw.text((0,0),text,font=font,fill=255,)
    oled.image(image)
    oled.show()
    wait_for_button_press()
    all_measurements = [plastic_type,"pre", time.strftime("%Y-%m-%d-%H:%M:%S")]
    do_measurement_light_off()
    with open('testresults.csv', mode='a') as test_results:
        test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_results.writerow(all_measurements)
    # Display info
    text = ','.join(str(e) for e in all_measurements[3:])
    draw.text((0,15),text,font=font,fill=255,)
    oled.image(image)
    oled.show()

    text = "press for actual measure"
    draw.text((0,25),text,font=font,fill=255,)
    oled.image(image)
    oled.show() 
    wait_for_button_press()
    all_measurements = [plastic_type,"actual", time.strftime("%Y-%m-%d-%H:%M:%S")]
    do_measurement()
    with open('testresults.csv', mode='a') as test_results:
        test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_results.writerow(all_measurements)
    text = ','.join(str(e) for e in all_measurements[3:])
    draw.text((0,35),text,font=font,fill=255,)
    oled.image(image)
    oled.show()

    text = "press for post measure"
    draw.text((0,45),text,font=font,fill=255,)
    oled.image(image)
    oled.show()     
    wait_for_button_press()
    all_measurements = [plastic_type,"post", time.strftime("%Y-%m-%d-%H:%M:%S")]
    do_measurement_light_off()
    with open('testresults.csv', mode='a') as test_results:
        test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_results.writerow(all_measurements)
    text = ','.join(str(e) for e in all_measurements[3:])
    draw.text((0,55),text,font=font,fill=255,)
    oled.image(image)
    oled.show()



