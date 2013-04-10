#!/usr/bin/env python
"""
bitcoin.py - Get bitcoin and LTC prices
Written by Nick Perkins - No rights reserved
"""

import re
import web
import urllib2
import datetime, pytz

brisbane = pytz.timezone('Australia/Brisbane')

r_string = re.compile(r'("(\\.|[^"\\])*")')
r_json = re.compile(r'^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]+$')
env = {'__builtins__': None, 'null': None, 'true': True, 'false': False}
mtgoxcurrencies = {"BTC" :1e8, "USD" :1e5, "GBP" :1e5, "EUR" :1e5, "JPY" :1e3, "AUD" :1e5, "CAD" :1e5, "CHF" :1e5, "CNY" :1e5, "DKK" :1e5, "HKD" :1e5, "PLN" :1e5, "RUB" :1e5, "SEK" :1e3, "SGD" :1e5,"THB" :1e5 }

def json(text): 
   """Evaluate JSON text safely (we hope)."""
   if r_json.match(r_string.sub('', text)): 
      text = r_string.sub(lambda m: 'u' + m.group(1), text)
      return eval(text.strip(' \t\r\n'), env, {})
   raise ValueError('Input must be serialised JSON.')

def getltc():
   """Query LTC Exchange, return its JSON."""

   uri = 'https://btc-e.com/api/2/ltc_usd/ticker'
   request = urllib2.Request(uri)
   bytes = urllib2.urlopen(request)
   return json(bytes.fp.read())

def resultltc():
   results = getltc()
   if results['ticker']:
      return results['ticker']['high'], results['ticker']['low'], results['ticker']['avg'], results['ticker']['server_time']
   return None

def ltc(phenny, input):
   """Queries LTC Exchange for price."""
   high, low, avg, now  = resultltc()
   utcDatetime = datetime.datetime.fromtimestamp(float(now), pytz.utc)
   brisbaneDatetime = utcDatetime.astimezone(brisbane)
   if high:
      phenny.reply("LTC price at %s - High: US$%s Low: US$%s Average US$%s" % (brisbaneDatetime.strftime('%Y-%m-%d %H:%M:%S %z'), high, low, avg))
   else: phenny.reply("No data returned.")
ltc.commands = ['ltc']
ltc.priority = 'high'
ltc.example = '.ltc'


def getprice(query): 
   """Search using Mt Gox API, return its JSON."""

   uri = ("https://data.mtgox.com/api/2/BTC%s/money/ticker" % query)
   request = urllib2.Request(uri)
   bytes = urllib2.urlopen(request)
   return json(bytes.fp.read())

def result(query): 
   results = getprice(query)
   if results['result'] == "success": 
      return urllib2.unquote(results['data']['high']['display']), urllib2.unquote(results['data']['low']['display']), urllib2.unquote(results['data']['avg']['display']), urllib2.unquote(results['data']['now'])
   return None

def btc(phenny, input): 
   """Queries Mt Gox for price."""
   query = input.group(2)
   if not query:
     query = "AUD"
   query = query.upper()
   if not query in mtgoxcurrencies:
     phenny.reply("Not a valid currency: %s" % query)   
     return
   high, low, avg, now  = result(query)
   utcDatetime = datetime.datetime.fromtimestamp(float(now) / 1e6, pytz.utc)
   brisbaneDatetime = utcDatetime.astimezone(brisbane)
   if high: 
      phenny.reply("Mt Gox price at %s - High: %s Low: %s Average %s" % (brisbaneDatetime.strftime('%Y-%m-%d %H:%M:%S %z'), high, low, avg))
   else: phenny.reply("No data returned.")
btc.commands = ['btc']
btc.priority = 'high'
btc.example = '.btc'

if __name__ == '__main__': 
   print __doc__.strip()
