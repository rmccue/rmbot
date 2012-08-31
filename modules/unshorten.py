#!/usr/bin/env python
"""
"""

import re
import web
import json
import sys
import head
import urllib, urllib2, urlparse, httplib

#yoink! http://the.taoofmac.com/space/blog/2009/08/10/2205

shorteners = ['tr.im','is.gd','tinyurl.com','bit.ly','snipurl.com','cli.gs',
                'feedproxy.google.com','feeds.arstechnica.com', 'g.co', 't.co',
                'fb.me', 'wp.me']
twofers = [u'\u272Adf.ws']
# learned hosts

def unshorten(bot, input):
  parsed = urlparse.urlparse(input.group(1))
  if parsed.netloc not in shorteners:
    return
  h = httplib.HTTPConnection(parsed.netloc)
  h.request('HEAD',parsed.path)
  response = h.getresponse()
  if response.status/100 == 3 and response.getheader('Location'):
    bot.say('Unshortened: %s' % response.getheader('Location'))

unshorten.rule = r'.*?((?:http|https)(?::\/{2}[\w]+)(?:[\/|\.]?)(?:[^\s"]*))'
unshorten.priority = 'low'

if __name__ == '__main__':
   print __doc__.strip()

