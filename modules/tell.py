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

maximum = 2
lastrun = 0
people = collections.defaultdict(dict)


def loadReminders(fn):
	result = {}
	f = open(fn)
	for line in f:
		line = line.strip()
		if line:
			tellee, teller, verb, timenow, msg = line.split('\t', 4)
			result.setdefault(tellee, []).append((teller, verb, timenow, msg))
	f.close()
	return result


def dumpReminders(fn, data):
	f = open(fn, 'w')
	for tellee in data.iterkeys():
		for remindon in data[tellee]:
			line = '\t'.join((tellee,) + remindon)
			f.write(line + '\n')
	try:
		f.close()
	except IOError:
		pass
	return True


def setup(self):
	fn = ''.join(i for i in self.nickname if i not in r'\/:*?"<>|') + '-' + self.config.host + '.tell.db'
	self.tell_filename = os.path.join(os.getcwd(), fn)
	if not os.path.exists(self.tell_filename):
		try:
			f = open(self.tell_filename, 'w')
		except OSError:
			pass
		else:
			f.write('')
			f.close()
	self.reminders = loadReminders(self.tell_filename)  # @@ tell


def f_remind(phenny, input):
	"""Leave a message for another user"""
	teller = input.nick

	# @@ Multiple comma-separated tellees? Cf. Terje, #swhack, 2006-04-15
	verb, tellee, msg = input.groups()
	if not tellee or not msg:
		return phenny.reply('Syntax: .tell/.ask <nick> <msg>')
	verb = verb.encode('utf-8')
	tellee = tellee.encode('utf-8')
	msg = msg.encode('utf-8')

	tellee_original = tellee.rstrip(',:;')
	tellee = tellee_original.lower()

	if not os.path.exists(phenny.tell_filename):
		return

	if len(tellee) > 20:
		return phenny.reply('That nickname is too long.')

	if input.sender in people and tellee in people[input.sender]:
		print 'status of %s is %s' % (tellee, people[input.sender][tellee])
#   timenow = time.strftime('%d %b %H:%MZ', time.gmtime())
# alphabeat patched to local time
	timenow = time.strftime('%d %b %H:%M', time.localtime())
	if not tellee in (teller.lower(), phenny.nickname, 'me'):  # @@
		# @@ <deltab> and year, if necessary
		warn = False
		if not tellee in phenny.reminders:
			phenny.reminders[tellee] = [(teller, verb, timenow, msg)]
		else:
			if len(phenny.reminders[tellee]) >= maximum:
				warn = True
			phenny.reminders[tellee].append((teller, verb, timenow, msg))
		# @@ Stephanie's augmentation
		response = "I'll pass that on when %s is around." % tellee_original
		if warn:
			response += (" I'll have to use a pastebin, though, so " +
									"your message may get lost.")

		rand = random.random()
		if rand > 0.9999:
			response = "yeah, yeah"
		elif rand > 0.999:
			response = "yeah, sure, whatever"

		phenny.reply(response)
	elif teller.lower() == tellee:
		phenny.say('You can %s yourself that.' % verb)
	else:
		phenny.say("Hey, I'm not as stupid as Monkey you know!")

	dumpReminders(phenny.tell_filename, phenny.reminders)  # @@ tell
f_remind.example = ".tell rmccue that he's awesome"
f_remind.rule = (['tell', 'ask'], r'(\S+) (.*)')


def getReminders(phenny, channel, key, tellee):
	lines = []
	template = "%s <%s> %s %s %s"
	today = time.strftime('%d %b', time.gmtime())

	for (teller, verb, datetime, msg) in phenny.reminders[key]:
		if datetime.startswith(today):
			datetime = datetime[len(today) + 1:]
		lines.append(template % (datetime, teller, verb, tellee, msg))

	try:
		del phenny.reminders[key]
	except KeyError:
		phenny.msg(channel, 'Er...')
	return lines


def message(phenny, input):
	if not input.sender.startswith('#'):
		return

	tellee = input.nick
	channel = input.sender

	if not os.path.exists(phenny.tell_filename):
		return

	reminders = []
	remkeys = list(reversed(sorted(phenny.reminders.keys())))
	for remkey in remkeys:
		if not remkey.endswith('*') or remkey.endswith(':'):
			if tellee.lower() == remkey:
				reminders.extend(getReminders(phenny, channel, remkey, tellee))
		elif tellee.lower().startswith(remkey.rstrip('*:')):
			reminders.extend(getReminders(phenny, channel, remkey, tellee))

	if len(reminders) < maximum:
		for line in reminders:
			phenny.say(tellee + ": " + line)
	else:
		try:
			data = {
				'title': 'Messages for %s' % tellee,
				'content': '\n'.join(reminders) + '\n',
			}
			result = urllib2.urlopen('http://dpaste.com/api/v1/', urllib.urlencode(data))
			message = '%s: see %s for your messages' % (tellee, result.geturl())
			phenny.say(message)
		except Exception:
			error = '[Sorry, some messages were elided and lost...]'
			phenny.say(error)

	if len(phenny.reminders.keys()) != remkeys:
		dumpReminders(phenny.tell_filename, phenny.reminders)  # @@ tell
message.rule = r'(.*)'
message.priority = 'low'


def user_joined(bot, input):
	user = input.user
	if user in bot.reminders:
		bot.reply('You may have messages. Say something to hear them.')

user_joined.event = 'userJoined'

if __name__ == '__main__':
	print __doc__.strip()
