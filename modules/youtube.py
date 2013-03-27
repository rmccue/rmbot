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
					return u"'{0}' - {1} views - http://youtu.be/{2}".format(entry.media.title.text.decode('utf-8'), group(entry.statistics.view_count), id)
			return u"'{0}' - {1} views - http://youtu.be/{2}".format(entry.media.title.text('utf-8'), 0, id)
		return None
	except gdata.service.RequestError:
		return u"That video doesn't exist, you Monkey-esque moron. Almost as bad as alphabeat!"
uri_matcher = re.compile(r'https?://(?:www\.)?youtu(?:\.be/|be\.com/watch\?v=)([^&#\s]+)')


def yt_matcher(bot, input):
	"""Gives information on YouTube links"""

	bot.say(link(input.group(1)))
yt_matcher.name = 'YouTube Autolinker'
yt_matcher.rule = r'.*http://(?:www\.)?youtu(?:\.be/|be\.com/watch\?v=)([^&#\s]+).*'
yt_matcher.priority = 'low'


if __name__ == '__main__':
	print __doc__.strip()
