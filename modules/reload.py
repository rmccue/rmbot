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
		try:
			module = getattr(__import__('modules.' + name), name)
		except ImportError, e:
			print e
			module = getattr(__import__('opt.' + name), name)
	except ImportError:
		return bot.reply('Module not found')
	reload(module)

	if hasattr(module, '__file__'):
		import os.path
		import time
		mtime = os.path.getmtime(module.__file__)
		modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))
	else:
		modified = 'unknown'

	bot.register_module(vars(module))
	bot.bind_commands()

	bot.reply('%r (version: %s)' % (module, modified))
f_reload.name = 'reload'
f_reload.rule = ('$nick', ['reload'], r'(\S+)?')
f_reload.priority = 'low'

if __name__ == '__main__':
	print __doc__.strip()
