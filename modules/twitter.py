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
		return u"@{0}: {1}".format(result['user']['screen_name'], result['text'])
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
