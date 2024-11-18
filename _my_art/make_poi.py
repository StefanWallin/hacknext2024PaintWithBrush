#!/usr/bin/env python


import sys
import os.path
from pyaxidraw import axidraw

ad = axidraw.AxiDraw()             # Create class instance

'''
Try a few different possible locations for our file,
so that this can be called from either the root or examples_python directory,
or if you're in the same directory with the file.
'''

ad.interactive()            # Enter interactive mode
connected = ad.connect()    # Open serial port to AxiDraw

if not connected:
    print('cannot connect to AxiDraw')
    sys.exit() # end script

# LOCATION = "_my_art/assets/looped_square_mine_1.svg"
LOCATION = "_my_art/assets/looped_square_mine_2.svg"

FILE = None

if os.path.exists(LOCATION):
    FILE = LOCATION

if FILE:
    print("Example file located at: " + FILE)
    ad.plot_setup(FILE)    # Parse the input file
else:
    print("Unable to locate example file; exiting.")
    sys.exit() # end script


ad.options.units = 0                # Set units to mm
ad.options.speed_pendown = 50       # Set maximum pen-down speed to 50%
ad.options.model = 2                # Set AxiDraw model to V3/A3

'''
See documentation for a description of additional options and their allowed values:
https://axidraw.com/doc/py_api/
'''

## Guard against ctrl-c during plotting, if detected it should abort plot and return to 0,0
try:
    try:
        ad.plot_run()   # plot the document
    except Exception as e:
        print(e)
except KeyboardInterrupt:
    ad.plot_stop()
    ad.moveto(0,0)
    ad.disconnect()
    sys.exit()