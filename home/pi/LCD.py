#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet

# from https://www.waveshare.com/wiki/2inch_LCD_Module?Amazon

import os
import sys
import time
import logging
import spidev as SPI
#sys.path.append("..")
from lib import LCD_2inch
from PIL import Image,ImageDraw,ImageFont

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
#logging.basicConfig(level=logging.DEBUG)
try:
    # display with hardware SPI:
    disp = LCD_2inch.LCD_2inch()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()
    #Set the backlight to 100
    disp.bl_DutyCycle(100)

    # Create blank image for drawing.
    #image1 = Image.new("RGB", (disp.height, disp.width ), "WHITE")
    #draw = ImageDraw.Draw(image1)

    # the file is run with "python LCD.py filename.jpg" and this will load filename.jpg
    # based on https://realpython.com/python-command-line-arguments/#displaying-arguments
    print("Showing image " + sys.argv[1])
    #this is what it used to do
    #image = Image.open('../pic/LCD_2inch.jpg')
    image = Image.open(sys.argv[1])
#    image = image.rotate(180)
    disp.ShowImage(image)
    disp.module_exit()
#    logging.info("quit:")
except IOError as e:
    print(e)
#the image only shows after the program finishes for some reason, so this sleep makes the image show for 5 seconds before the screen goes blank
time.sleep(5)
