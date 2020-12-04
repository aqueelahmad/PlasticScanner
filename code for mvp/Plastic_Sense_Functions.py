#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import struct
import wiringpi as wp
from Plastic_Sense_Definitions import *
import Plastic_Sense_Config

class ADS1255(object):

    def __init__(self, conf=Plastic_Sense_Config):
        # Set up the wiringpi object to use physical pin numbers
        wp.wiringPiSetupGpio()
        # Config and initialize the SPI and GPIO pins used by the ADC.
        # The following four entries are actively used by the code:
        self.SPI_CHANNEL  = conf.SPI_CHANNEL
        self.DRDY_PIN     = conf.DRDY_PIN
        self.CS_PIN       = conf.CS_PIN
        self.DRDY_TIMEOUT = conf.DRDY_TIMEOUT
        self.DRDY_DELAY   = conf.DRDY_DELAY
        self.demux_A0     = conf.demux_A0
        self.demux_A1     = conf.demux_A1
        self.demux_A2     = conf.demux_A2
        self.light        = conf.light
        # Only one GPIO input:
        if conf.DRDY_PIN is not None:
            self.DRDY_PIN = conf.DRDY_PIN
            wp.pinMode(conf.DRDY_PIN,  wp.INPUT)
        # GPIO Outputs. Only the CS_PIN is currently actively used. ~RESET and 
        # ~PDWN must be set to static logic HIGH level if not hardwired:
        for pin in (conf.CS_PIN,
                    conf.RESET_PIN,
                    conf.PDWN_PIN,
                    conf.demux_A0,
                    conf.demux_A1,
                    conf.demux_A2,
                    conf.light):
            if pin is not None:
                wp.pinMode(pin, wp.OUTPUT)
                wp.digitalWrite(pin, wp.HIGH)
        
        # Initialize the wiringpi SPI setup. Return value is the Linux file
        # descriptor for the SPI bus device:
        fd = wp.wiringPiSPISetupMode(
                conf.SPI_CHANNEL, conf.SPI_FREQUENCY, conf.SPI_MODE)
        if fd == -1:
            raise IOError("ERROR: Could not access SPI device file")
        
        # ADS1255/ADS1256 command timing specifications. Do not change.
        # Delay between requesting data and reading the bus for
        # RDATA, RDATAC and RREG commands (datasheet: t_6 >= 50*CLKIN period).
        self._DATA_TIMEOUT_US = int(1 + (50*1000000)/conf.CLKIN_FREQUENCY)
        # Command-to-command timeout after SYNC and RDATAC
        # commands (datasheet: t11)
        self._SYNC_TIMEOUT_US = int(1 + (24*1000000)/conf.CLKIN_FREQUENCY)
        # See datasheet ADS1256: CS needs to remain low
        # for t_10 = 8*T_CLKIN after last SCLK falling edge of a command.
        # Because this delay is longer than timeout t_11 for the
        # RREG, WREG and RDATA commands of 4*T_CLKIN, we do not need
        # the extra t_11 timeout for these commands when using software
        # chip select selection and the _CS_TIMEOUT_US.
        self._CS_TIMEOUT_US   = int(1 + (8*1000000)/conf.CLKIN_FREQUENCY)
        # When using hardware/hard-wired chip select, still a command-
        # to command timeout of t_11 is needed as a minimum for the
        # RREG, WREG and RDATA commands.
        self._T_11_TIMEOUT_US   = int(1 + (4*1000000)/conf.CLKIN_FREQUENCY)

        # Initialise class properties
        self.v_ref         = conf.v_ref

        # At hardware initialisation, a settling time for the oscillator
        # is necessary before doing any register access.
        # This is approx. 30ms, according to the datasheet.
        time.sleep(0.03)
        self.wait_DRDY()
        # Device reset for defined initial state
        self.reset()

        # Configure ADC registers:
        # Status register not yet set, only variable written to avoid multiple
        # triggering of the AUTOCAL procedure by changing other register flags
        self._status       = conf.status
        # Class properties now configure registers via their setter functions
        self.mux           = conf.mux
        self.adcon         = conf.adcon
        self.drate         = conf.drate
        self.gpio          = conf.gpio
        self.status        = conf.status        

    def _send_uint8(self, *vals):
        # Reads integers in range (0, 255), sends as uint-8 via the SPI bus
        wp.wiringPiSPIDataRW(self.SPI_CHANNEL,
                                struct.pack("{}B".format(len(vals)), *vals))
        # Python3 only:
        # wp.wiringPiSPIDataRW(self.SPI_CHANNEL, bytes(vals))

    def _chip_select(self):
        # If chip select hardware pin is connected to SPI bus hardware pin or
        # hardwired to GND, do nothing.
        if self.CS_PIN is not None:
            wp.digitalWrite(self.CS_PIN, wp.LOW)

    def _chip_release(self):
        if self.CS_PIN is not None:
            wp.delayMicroseconds(self._CS_TIMEOUT_US)
            wp.digitalWrite(self.CS_PIN, wp.HIGH)
        else:
            # The minimum t_11 timeout between commands, see datasheet Figure 1.
            wp.delayMicroseconds(self._T_11_TIMEOUT_US)

    def _read_uint8(self, n_vals=1):
        # Returns tuple containing unsigned 8-bit int interpretation of
        # n_vals bytes read via the SPI bus. n_bytes is supposed to 
        n_bytes, data = wp.wiringPiSPIDataRW(self.SPI_CHANNEL, b"\xFF"*n_vals)
        assert n_bytes == n_vals
        return struct.unpack("{}B".format(n_bytes), data)
        # Python3 only:
        # return tuple(data)

    def _read_int24(self):
        # Returns signed int interpretation of three bytes read via the SPI bus
        _, data = wp.wiringPiSPIDataRW(self.SPI_CHANNEL, b"\xFF\xFF\xFF")
        return struct.unpack(">i", data + b"\x00")[0] >> 8
        # Python3 only:
        # return int.from_bytes(data, "big", signed=True)


    def wait_DRDY(self):

        """Delays until the configured DRDY input pin is pulled to
        active logic low level by the ADS1256 hardware or until the
        DRDY_TIMEOUT in seconds has passed.

        Arguments: None
        Returns: None

        The minimum necessary DRDY_TIMEOUT when not using the hardware
        pin, can be up to approx. one and a half second, see datasheet..
        
        Manually invoking this function is necessary when using the
        automatic calibration feature (ACAL flag). Then, use wait_DRDY()
        after every access that changes the PGA gain bits in
        ADCON register, the DRATE register or the BUFFEN flag.
        """
        start = time.time()
        elapsed = time.time() - start
        # Waits for DRDY pin to go to active low or DRDY_TIMEOUT seconds to pass
        if self.DRDY_PIN is not None:
            drdy_level = wp.digitalRead(self.DRDY_PIN)
            while (drdy_level == wp.HIGH) and (elapsed < self.DRDY_TIMEOUT):
                elapsed = time.time() - start
                drdy_level = wp.digitalRead(self.DRDY_PIN)
                # Delay in order to avoid busy wait and reduce CPU load.
                time.sleep(self.DRDY_DELAY)
            if elapsed >= self.DRDY_TIMEOUT:
                print("\nWarning: Timeout while polling configured DRDY pin!\n")
        else:
            time.sleep(self.DRDY_TIMEOUT)

    def chip_ID(self):
        """Get the numeric ID from the ADS chip.
        Useful to check if hardware is connected.

        Value for the ADS1256 on the Waveshare board seems to be a 3.
        """
        self.wait_DRDY()
        return self.read_reg(REG_STATUS) >> 4

    def read_reg(self, register):
        """Returns data byte from the specified register
        
        Argument: register address
        """
        self._chip_select()
        self._send_uint8(CMD_RREG | register, 0x00)
        wp.delayMicroseconds(self._DATA_TIMEOUT_US)
        read, = self._read_uint8()
        # Release chip select and implement t_11 timeout
        self._chip_release()
        return read

    def read_and_next_is(self, diff_channel):
        """Reads ADC data of presently running or already finished
        conversion, sets and synchronises new input channel config
        for next sequential read.

        Arguments:  8-bit code value for differential input channel
                        (See definitions for the REG_MUX register)
        Returns:    Signed integer conversion result for present read
        
        This enables rapid dycling through different channels and
        implements the timing sequence outlined in the ADS1256
        datasheet (Sept.2013) on page 21, figure 19: "Cycling the
        ADS1256 Input Multiplexer".

        Note: In most cases, a fixed sequence of input channels is known
        beforehand. For that case, this module implements the function:
        
        read_sequence(ch_sequence)
            which automates the process for cyclic data acquisition.
        """
        self._chip_select()
        self.wait_DRDY()

        # Setting mux position for next cycle"
        self._send_uint8(CMD_WREG | REG_MUX, 0x00, diff_channel)
        # Restart/start next conversion cycle with new input config
        self._send_uint8(CMD_SYNC)
        wp.delayMicroseconds(self._SYNC_TIMEOUT_US)
        self._send_uint8(CMD_WAKEUP)
        # The datasheet is a bit unclear if a t_11 timeout is needed here.
        # Assuming the extra timeout is the safe choice:
        wp.delayMicroseconds(self._T_11_TIMEOUT_US)
        # Read data from ADC, which still returns the /previous/ conversion
        # result from before changing inputs
        self._send_uint8(CMD_RDATA)
        wp.delayMicroseconds(self._DATA_TIMEOUT_US)
        # The result is 24 bits little endian two's complement value by default
        int24_result = self._read_int24()
        # Release chip select and implement t_11 timeout
        self._chip_release()
        return int24_result

    def cal_self(self):
        """Perform an input zero and full-scale two-point-calibration
        using chip-internal circuitry connected to VREFP and VREFN.

        Sets the ADS1255/ADS1256 OFC and FSC registers.
        """
        self._chip_select()
        self._send_uint8(CMD_SELFCAL)
        self.wait_DRDY()
        # Release chip select and implement t_11 timeout
        self._chip_release()
        wp.delayMicroseconds(self._T_11_TIMEOUT_US)
        
    def reset(self):
        """Reset all registers except CLK0 and CLK1 bits
        to reset values and Polls for DRDY change / timeout afterwards.
        """
        self._chip_select()
        self._send_uint8(CMD_RESET)
        self.wait_DRDY()
        # Release chip select and implement t_11 timeout
        self._chip_release()

    def set_led_on(self, led):
        led_values = led_table[led+1]
        #print("Turning on led:", led+1)
        wp.digitalWrite(self.light, 1)
        wp.digitalWrite(self.demux_A0, led_values[2])
        wp.digitalWrite(self.demux_A1, led_values[1])
        wp.digitalWrite(self.demux_A2, led_values[0])

    def set_led_off(self):
        wp.digitalWrite(self.light, 0)
        wp.digitalWrite(self.demux_A0, wp.LOW)
        wp.digitalWrite(self.demux_A1, wp.LOW)
        wp.digitalWrite(self.demux_A2, wp.LOW)
