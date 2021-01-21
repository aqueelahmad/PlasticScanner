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
import csv
import Plastic_Sense_Config as conf
from Plastic_Sense_Functions import ADS1256

################################################
############Tensorflow part
################################################
import pandas as pd
import numpy as np
import tflite_runtime.interpreter as tflite

# Load the TFLite model and allocate tensors.
interpreter = tflite.Interpreter(model_path="converted_model.tflite")
interpreter.allocate_tensors()



plastics = ["PET", "HDPE", "PCV", "LDPE", "PP", "PS","OTHER"]
################################################
############Tensorflow part
################################################


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
    update_screen("Plastic Scanner.", 0, 0)
    print("hold scanner to object and press button'")
    plastic_type = "estimate"
    update_screen("-Press ---->", 0, 10)
    wait_for_button_press()
    update_screen("-Starting", 0, 20)
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
    
    update_screen("-Finished measuring", 0, 30)
    with open('testresults.csv', mode='a') as test_results:
        test_results = csv.writer(test_results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        test_results.writerow(all_measurementspre)
        test_results.writerow(all_measurementsactual)
        test_results.writerow(all_measurementspost)
    update_screen("-Making a guess", 0, 40)
    
################################################
############Tensorflow part
################################################

    #clean data, average pre and post measurements, delete from actual measurement
    
    #input the data to tensorflow model and make prediction
    #https://www.tensorflow.org/lite/guide/inference#load_and_run_a_model_in_python

    # Get input and output tensors.
    # Test the model on random input data.
    input_shape = input_details[0]['shape']
    input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])
    print(output_data)




################################################
############Tensorflow part
################################################
    print("Measure again? y/n")
    again = input()
    if again == "n":
        oled.fill(0) #clear screen
        oled.show()
        exit()



