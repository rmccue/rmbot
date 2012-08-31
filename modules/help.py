#!/usr/bin/env python

""" this is the help.py function """


def list_help(bot, input):
	bot.reply('Check your PM for help.')
	bot.msg(input.user, 'The following commands are available:')
	for name, info in bot.doc.items():
		command = name
		if info['commands']:
			if len(info['commands']) > 1:
				command = '{0}{{{1}}}'.format(bot.config.prefix, ', '.join(info['commands']))
			else:
				command = bot.config.prefix + info['commands'][0]
		bot.msg(input.user, '  {0}: {1}'.format(command, info['doc']))

list_help.commands = ['help']
