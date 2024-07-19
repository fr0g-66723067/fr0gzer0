import logging
import ST7789
import time

from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.DEBUG)
# 240x240 display with hardware SPI:
disp = ST7789.ST7789()

# Initialize library.
disp.Init()

# Clear display.
disp.clear()

#Set the backlight to 100
disp.bl_DutyCycle(50)

logging.info("show image")
image = Image.open('frog-logo-240x240.jpg')
im_r = image.rotate(270)
disp.ShowImage(im_r)
time.sleep(3)
