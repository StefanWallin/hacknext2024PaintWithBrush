#!/usr/bin/env python
import math
import random
import sys
import os.path
from pyaxidraw import axidraw

MARGIN = 5
CANVAS_HEIGHT = 300
CANVAS_WIDTH = 300
MAX_X = CANVAS_WIDTH - MARGIN
MAX_Y = CANVAS_HEIGHT - MARGIN

## CONNECT
ad = axidraw.AxiDraw() # Initialize class
ad.interactive()            # Enter interactive mode
connected = ad.connect()    # Open serial port to AxiDraw
if not connected:
  print('cannot connect to AxiDraw')
  sys.exit() # end script

# ## OPTIONS
ad.options.speed_pendown = 20       # Set maximum pen-down speed to 90%
ad.options.model = 2                # Set AxiDraw model to V3/A3
ad.options.units = 2                # Set units to millimeters
ad.options.pen_pos_up = 100          # Set pen-up position to 0%
# ad.options.units = 1                # Set units to centimeters
ad.update()                         # Process changes to options
ad.penup()                          # Raise pen

ad.disconnect()                     # Close serial port to AxiDraw