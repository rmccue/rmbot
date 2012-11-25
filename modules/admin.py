#!/usr/bin/env python
"""
admin.py - bot Admin Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/bot/
"""


def join(bot, input):
	"""Join the specified channel. This is an admin-only command."""
	# Can only be done in privmsg by an admin
	if input.sender.startswith('#') and not input.sender == bot.config.adminchan:
		return
	if input.admin:
		channel, key = input.group(2), input.group(3)
		if not key:
			bot.join(channel)
		else:
			bot.join(channel, key)
join.rule = (['join'], r'(#\S+)(?: *(\S+))?')
join.priority = 'low'
join.example = '.join #example or .join #example key'


def part(bot, input):
	"""Part the specified channel. This is an admin-only command."""
	# Can only be done in privmsg by an admin
	if input.sender.startswith('#') and not input.sender == bot.config.adminchan:
		return
	if input.admin:
		bot.part(input.group(2).encode('utf-8'))
part.commands = ['part']
part.priority = 'low'
part.example = '.part #example'


def quit(bot, input):
	"""Quit from the server. This is an owner-only command."""
	# Can only be done in privmsg by the owner
	if input.sender.startswith('#') and not input.sender == bot.config.adminchan:
		return
	if input.owner:
		bot.quit()
quit.commands = ['quit']
quit.priority = 'low'


def msg(bot, input):
	# Can only be done in privmsg by an admin
	if input.sender.startswith('#') and not input.sender == bot.config.adminchan:
		return
	if input.admin:
		bot.msg(input.group(2).encode('utf-8'), input.group(3))
msg.rule = (['msg'], r'(#?\S+) (.*)')
msg.priority = 'low'


def me(bot, input):
	# Can only be done in privmsg by an admin
	if input.sender.startswith('#') and not input.sender == bot.config.adminchan:
		return
	if input.admin:
		bot.action(input.group(2).encode('utf-8'), input.group(3))
me.rule = (['me'], r'(#?\S+) (.*)')
me.priority = 'low'

if __name__ == '__main__':
	print __doc__.strip()
