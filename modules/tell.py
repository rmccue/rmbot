#!/usr/bin/env python
"""
tell.py - Phenny Tell and Ask Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import os
import time
import random
import urllib
import urllib2
import collections

import logging

maximum = 2
lastrun = 0
people = collections.defaultdict(dict)


def setup(bot):
	bot.reminders = bot.db.get('tell.reminders')
	if not bot.reminders:
		bot.reminders = {}


def tell(bot, input):
	"""Leave a message for another user"""
	teller = input.nick

	# @@ Multiple comma-separated tellees? Cf. Terje, #swhack, 2006-04-15
	verb, tellee, msg = input.groups()
	if not tellee or not msg:
		return bot.reply('Syntax: .tell/.ask <nick> <msg>')
	verb = verb.encode('utf-8')
	tellee = tellee.encode('utf-8')
	msg = msg.encode('utf-8')

	tellee_original = tellee.rstrip(',:;')
	tellee = tellee_original.lower()

	if len(tellee) > 20:
		return bot.reply('That nickname is too long.')

	if input.sender in people and tellee in people[input.sender]:
		print 'status of %s is %s' % (tellee, people[input.sender][tellee])
#   timenow = time.strftime('%d %b %H:%MZ', time.gmtime())
# alphabeat patched to local time
	timenow = time.strftime('%d %b %H:%M', time.localtime())
	if not tellee in (teller.lower(), bot.nickname, 'me'):  # @@
		# @@ <deltab> and year, if necessary
		warn = False
		if not tellee in bot.reminders:
			bot.reminders[tellee] = [(teller, verb, timenow, msg)]
		else:
			if len(bot.reminders[tellee]) >= maximum:
				warn = True
			bot.reminders[tellee].append((teller, verb, timenow, msg))
		# @@ Stephanie's augmentation
		response = "I'll pass that on when %s is around." % tellee_original

		rand = random.random()
		if rand > 0.9999:
			response = "yeah, yeah"
		elif rand > 0.999:
			response = "yeah, sure, whatever"

		bot.reply(response)

		bot.db.set('tell.reminders', bot.reminders)

	elif teller.lower() == tellee:
		bot.say('You can %s yourself that.' % verb)
	else:
		bot.say("Hey, I'm not as stupid as Monkey you know!")

tell.example = ".tell rmccue that he's awesome"
tell.rule = (['tell', 'ask'], r'(\S+) (.*)')


def getReminders(bot, channel, key, tellee):
	lines = []
	template = "%s <%s> %s %s %s"
	today = time.strftime('%d %b', time.gmtime())

	for (teller, verb, datetime, msg) in bot.reminders[key]:
		if datetime.startswith(today):
			datetime = datetime[len(today) + 1:]
		lines.append(template % (datetime, teller, verb, tellee, msg))

	try:
		del bot.reminders[key]
	except KeyError:
		bot.msg(channel, 'Er...')
	return lines


def message(bot, input):
	if not input.sender.startswith('#'):
		return

	tellee = input.nick
	channel = input.sender

	reminders = []
	remkeys = list(reversed(sorted(bot.reminders.keys())))
	for remkey in remkeys:
		if not remkey.endswith('*') or remkey.endswith(':'):
			if tellee.lower() == remkey:
				reminders.extend(getReminders(bot, channel, remkey, tellee))
		elif tellee.lower().startswith(remkey.rstrip('*:')):
			reminders.extend(getReminders(bot, channel, remkey, tellee))

	for line in reminders:
		bot.msg(tellee, tellee + ": " + line)

	if len(bot.reminders.keys()) != remkeys:
		bot.db.set('tell.reminders', bot.reminders)  # @@ tell

message.rule = r'(.*)'
message.priority = 'low'


def user_joined(bot, input):
	user = input.user
	if user in bot.reminders:
		bot.reply('You may have messages. Say something to hear them.')

user_joined.event = 'userJoined'

if __name__ == '__main__':
	print __doc__.strip()
