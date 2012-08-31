#!/usr/bin/env python

""" this is the help.py function """


def get_command_string(info, prefix, name):
	if info['commands']:
		if len(info['commands']) > 1:
			return prefix + '{{{0}}}'.format(', '.join(info['commands']))
		else:
			return prefix + info['commands'][0]
	return name


def list_help(bot, input):
	if not input.group(2):
		# General help
		bot.reply('Check your PM for help.')
		bot.msg(input.user, 'The following commands are available:')
		for name, info in bot.doc.items():
			command = get_command_string(info, bot.config.prefix, name)
			bot.msg(input.user, '  {0}: {1}'.format(command, info['doc']))
		bot.msg(input.user, 'For more information, try "!help <command>"')
	else:
		name = input.group(2)
		print name
		if not name in bot.doc:
			for _name, info in bot.doc.items():
				if name in info['commands']:
					name = _name
			if not name in bot.doc:
				bot.reply("Sorry, I can't help with that")
				return
		info = bot.doc[name]
		command = get_command_string(info, bot.config.prefix, name)
		bot.reply('{0}: {1}'.format(command, info['doc']))
		if info['example']:
			bot.reply('e.g: {0}'.format(info['example']))

list_help.commands = ['help']
