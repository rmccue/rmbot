#!/usr/bin/env python
"""
notchwatch.py - polls notch's tweets
"""

import re
#import time
import sys
import web
import json



def setup(self):
  self.say("Loaded mystery module")
  print >> sys.stderr, "Mystery loaded: " + str(self)
  return
def query():

   """Search using SearchMash, return its JSON."""
   uri = 'http://twitter.com/statuses/user_timeline/63485337.json'
   bytes = web.get(uri)
   try:
      result = json.loads(bytes)
   except:
      result = "FAILWHALE.JPG"
   return result

def poller(phenny):
   return
def notchwatch(phenny, input):

   phenny.say('Y U NO LOAD')
   # to a global, you need to explicitly do `global var` 

notchwatch.rule = r'.notchwatch'
notchwatch.example = '.notchwatch <text>'

if __name__ == '__main__': 
   print __doc__.strip()
