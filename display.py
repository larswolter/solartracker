# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import time
import subprocess
import board
import busio
# import Adafruit_SSD1306
import adafruit_ssd1306

def setupDisplay():
    try:
        # Create the I2C interface.
        i2c = busio.I2C(board.SCL, board.SDA)

        # Create the SSD1306 OLED class.
        # The first two parameters are the pixel width and pixel height.  Change these
        # to the right size for your display!
        # disp = Adafruit_SSD1306.SSD1306_128_64(i2c)
        disp = adafruit_ssd1306.SSD1306_I2C(128,64,i2c)

        # Clear display.
        disp.fill(0)
        disp.show()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = disp.width
        height = disp.height
        return disp
    except Exception as e_all:
        print(f'Could not initilize display {e_all}')

def displayImage(image, disp):
    if disp == None:
        image.save('./output.png',bitmap_format='png')
        return
    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(0.1)

def displayOff(disp):
    if disp == None:
        return
    disp.fill(0)
    disp.show()
    time.sleep(0.1)