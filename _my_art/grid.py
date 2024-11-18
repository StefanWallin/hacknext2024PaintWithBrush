#!/usr/bin/env python
import math
import random
import sys
import os.path
from pyaxidraw import axidraw

MARGIN = 5
CANVAS_HEIGHT = 297
CANVAS_WIDTH = 420
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
# ad.options.units = 1                # Set units to centimeters
ad.update()                         # Process changes to options
ad.pendown()                          # Raise pen
ad.penup()                          # Raise pen
ad.goto(0,0)

try:
  ad.goto(MARGIN,MARGIN)
  ad.pendown()
  ad.goto(MAX_X,MARGIN)
  ad.goto(MAX_X,MAX_Y)
  ad.goto(MARGIN,MAX_Y)
  ad.goto(MARGIN,MARGIN)
  ad.penup()
except Exception as e:
  print(e)
finally:
  ## Teardown
  ad.penup()
  ad.moveto(0,0)              # Pen-up return home
  ad.disconnect()             # Close serial port to AxiDraw


