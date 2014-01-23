#!/usr/bin/env python
"""
reload.py - bot Module Reloader Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/bot/
"""


def f_reload(bot, input):
	"""Reloads a module, for use by admins only."""
	if not input.admin:
		return

	name = input.group(2)
	if (not name) or (name == '*'):
		bot.setup()
		return bot.reply('done')

	try:
		module, modified = bot.dispatcher.reload_module(name)
		if not module:
			bot.reply('Failed: The module could not be loaded.')
		else:
			bot.reply('Success: %r (version: %s)' % (module, modified))
	except ImportError:
		return bot.reply('Module not found')
f_reload.name = 'reload'
f_reload.rule = ('$nick', ['reload'], r'(\S+)?')
f_reload.priority = 'low'

if __name__ == '__main__':
	print __doc__.strip()
