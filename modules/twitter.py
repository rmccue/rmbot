#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import web
import json
import urllib
from datetime import datetime


def pretty_date(time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.utcnow()
        if type(time) is int:
                diff = now - datetime.fromtimestamp(time)
        elif isinstance(time, datetime):
                diff = now - time
        elif not time:
                diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
                return ''

        if day_diff == 0:
                if second_diff < 10:
                        return "just now"
                if second_diff < 60:
                        return str(second_diff) + " seconds ago"
                if second_diff < 120:
                        return  "a minute ago"
                if second_diff < 3600:
                        return str(second_diff / 60) + " minutes ago"
                if second_diff < 7200:
                        return "an hour ago"
                if second_diff < 86400:
                        return str(second_diff / 3600) + " hours ago"
        if day_diff == 1:
                return "Yesterday"
        if day_diff < 7:
                return str(day_diff) + " days ago"
        if day_diff < 31:
                return str(day_diff / 7) + " weeks ago"
        if day_diff < 365:
                return str(day_diff / 30) + " months ago"
        return str(day_diff / 365) + " years ago"


def query(bits, query = {}):
	q = web.urllib.quote(bits.encode('utf-8'))
	uri = 'http://api.twitter.com/1/' + q + '.json'
	if query:
		uri += '?' + urllib.urlencode(query)
	bytes = web.get(uri).encode("utf-8")
	try:
		result = json.loads(bytes)
	except:
		result = "An error occurred. Maybe Twitter is down?"
	return result

def latest(user):
	result = query('statuses/user_timeline', {'screen_name': user, 'count': 1})
	if len(result) == 0 or type(result) != list:
		return None

	result = result[0]
	if 'text' in result.keys():
		return u"@{0}: {1}".format(result['user']['screen_name'], result['text'])
	return None

def content(id):
	result = query('statuses/show/' + id)

	if 'text' in result.keys():
	        time = datetime.strptime(result['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

		return u"@{0}: {1} - {2}".format(result['user']['screen_name'], result['text'], pretty_date(time))
	return None

def user(rmbot, input):
	query = input.group(2)
	uri = latest(query)
	if uri:
		rmbot.reply(uri)
	else: rmbot.reply("No results found for '%s'." % query)
user.commands = ['twitter']
user.priority = 'high'
user.example = '.twitter rmccue'

# https://twitter.com/#!/EA_Australia/status/118638795817099264
status_regex = r'.*https?://(?:www\.)?twitter\.com/(?:#!/)?\w+/status/(\w+)'
def status_link(bot, input):
	tweet = input.group(1)
	if not tweet:
		return

	text = content(tweet)
	if not text:
		return

	bot.say(text)
status_link.rule = status_regex
status_link.priority = 'low'

'''
user_regex = r'.*https?://(?:www\.)?twitter\.com/(?:#!/)?([^/]+)'
def user_link(bot, input):
	user = input.group(1)
	print user
	if not user:
		return

	text = latest(user)
	if not text:
		return

	bot.say(text)
user_link.rule = user_regex
user_link.priority = 'low'
'''

if __name__ == '__main__':
	print __doc__.strip()
