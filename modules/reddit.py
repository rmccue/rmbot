#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web
import json

def query(bits, n=1): 
   """Search using SearchMash, return its JSON."""
   q = web.urllib.quote(bits.encode('utf-8'))
   uri = 'http://www.reddit.com/' + q + '.json'
   bytes = web.get(uri)
   try:
      result = json.loads(bytes)
   except:
      result = "An error occurred. Maybe reddit is down?"
   return result

def top(subreddit): 
   results = query('r/' + subreddit)
   if results['data']['children'][0]: 
      top = results['data']['children'][0]['data']
      if subreddit != 'all':
         return "'%s' - +%d/-%d - http://redd.it/%s" % (top['title'], top['ups'], top['downs'], top['id'])
      else:
         return "'%s' - +%d/-%d in %s - http://redd.it/%s" % (top['title'], top['ups'], top['downs'], top['subreddit'], top['id'])
   return None

def link(id):
   results = query('comments/' + id)
   if results[0]['data']['children'][0]: 
      post = results[0]['data']['children'][0]['data']
      return "'%s' - +%d/-%d - http://redd.it/%s" % (post['title'], post['ups'], post['downs'], post['id'])
   return None

def reddit(phenny, input): 
   """Queries Google for the specified input."""
   query = input.group(2)
   if not query: 
      query = 'all'
   uri = top(query)
   if uri: 
      phenny.reply(uri)
      if not hasattr(phenny.bot, 'last_seen_uri'):
         phenny.bot.last_seen_uri = {}
      phenny.bot.last_seen_uri[input.sender] = uri
   else: phenny.reply("No results found for '%s'." % query)
reddit.commands = ['reddit']
reddit.priority = 'high'
reddit.example = '.reddit minecraftau'

uri_matcher = re.compile(r'http://(?:www\.)?redd(?:\.it/|it\.com/(?:tb|(?:r/\w+/)?comments)/)(\w+)')
def reddit_linkage(bot, input): 
   matches = uri_matcher.search(input.group(1))
   if not matches:
      return

   bot.say(link(matches.group(1)))
reddit_linkage.rule = r'(http://(?:www\.)?redd.*)'
reddit_linkage.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
