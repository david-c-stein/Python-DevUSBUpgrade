#!/usr/bin/env python

import os

# will this be multiprocessing or multithreaded
# Threaded is easier for windows - windows pickler is broken

if os.name == 'nt':
    __MULTIPROCESSING__ = False
else:
    __MULTIPROCESSING__ = True

# Enulate HW - for testing without hardware
__EMULATE_HW__ = True

# Simulate Events = for testing
__SIMULATE_EVENTS__ = True

# username and password
__USERNAME__ = 'qa'
__PASSWORD__ = 'test'
