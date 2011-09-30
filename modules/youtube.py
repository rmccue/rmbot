#!/usr/bin/env python
"""
youtube.py - YouTube module
Copyright 2011, Ryan McCue
Licensed under the Eiffel Forum License 2.
"""

import re

import gdata.service
import gdata.youtube
import gdata.youtube.service

yt_service = gdata.youtube.service.YouTubeService()

# The YouTube API does not currently support HTTPS/SSL access.
yt_service.ssl = False

def group(number):
    s = '%d' % int(number)
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))

def link(id):
   try:
      entry = yt_service.GetYouTubeVideoEntry(video_id=id)
      if entry:
         #return "'{0}' - {1} views - {2}".format(entry.media.title.text, group(entry.statistics.view_count), entry.media.player.url.replace('&feature=youtube_gdata_player', ''))
         if entry.statistics:
            return "'{0}' - {1} views - http://youtu.be/{2}".format(entry.media.title.text, group(entry.statistics.view_count), id)
         return "'{0}' - {1} views - http://youtu.be/{2}".format(entry.media.title.text, 0, id)
      return None
   except gdata.service.RequestError:
         return "That video doesn't exist, you Monkey-esque moron. Almost as bad as alphabeat!"
uri_matcher = re.compile(r'http://(?:www\.)?youtu(?:\.be/|be\.com/watch\?v=)([^&#\s]+)')
def yt_matcher(bot, input): 
   matches = uri_matcher.search(input.group(1))
   if not matches:
      return

   bot.say(link(matches.group(1)))
yt_matcher.rule = r'.*(http://(?:www\.)?youtu(?:\.be|be\.com)/.*)'
yt_matcher.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
