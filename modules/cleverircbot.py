#!/usr/bin/env python
"""
cleverircbot.py - Uses cleverbot api
"""

import cleverbot
import re
import random
import time

mycb = cleverbot.Session()
cleverbotnick = 'cleverbot'

def cleverircbot(phenny, input):
   """Passes the input to cleverbot and posts the response"""
   response = ""
   pattern = re.compile(phenny.nick, re.IGNORECASE)
   question = input.group(1).strip()
   question = pattern.sub(cleverbotnick, question)
   if question.startswith('reload'):
      if not input.owner:
         response = "%s_%s" % (unichr(3232),unichr(3232))
         phenny.reply(response)
      return
   response = mycb.Ask(question)
   pattern = re.compile(cleverbotnick, re.IGNORECASE)
   response = pattern.sub(phenny.nick, response)
   phenny.reply(response)

cleverircbot.rule = r'$nick(.*)'
cleverircbot.example = 'rmbot: <text>'

if __name__ == '__main__': 
   print __doc__.strip()
