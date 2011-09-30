#!/usr/bin/env python
"""
digg.py - Uses digg api
"""

import re
import time

def digg(phenny, input):
   lod = "%s_%s" % (unichr(3232),unichr(3232))
   time.sleep(1.2)
   phenny.reply(lod)
   # to a global, you need to explicitly do `global var` 

digg.rule = r'.digg'
digg.example = '.digg <text>'

if __name__ == '__main__': 
   print __doc__.strip()
