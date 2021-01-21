#!/usr/bin/python
# -*- coding: utf-8 -*-
from Plastic_Sense_Definitions import *

######### Number of leds
number_of_leds = 8

######### SPI Settings
SPI_CHANNEL   = 1
SPI_MODE      = 1
SPI_FREQUENCY = 976563

######## GPIO settings
CS_PIN      = 8 
DRDY_PIN    = 22
RESET_PIN   = None
PDWN_PIN    = None
light       = 18
demux_A0    = 25
demux_A1    = 24
demux_A2    = 23


####### Constant config settings
DRDY_TIMEOUT    = 2
DRDY_DELAY      = 0.000001
CLKIN_FREQUENCY = 7680000

####### runtime adjustable properties
v_ref = 2.5
gain_flags = GAIN_1


####### register settings
status = BUFFER_ENABLE
mux = POS_AIN0 | NEG_AINCOM
adcon = CLKOUT_OFF | SDCS_OFF | gain_flags
drate  = DRATE_10
gpio = 0x00

