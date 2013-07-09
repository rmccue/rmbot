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
		bot.msg(input.user, 'The following commands are available:')
		for name, info in bot.dispatcher.doc.items():
			command = get_command_string(info, bot.config.prefix, name)
			doc = info['doc']
			if "\n" in doc:
				doc, _ = doc.split("\n", 1)
				doc = "{0} [...]".format(doc)
			bot.msg(input.user, '  {0}: {1}'.format(command, doc))
		bot.msg(input.user, 'For more information, try "!help <command>"')
	else:
		name = input.group(2)
		pos = name.find(bot.config.prefix)
		logging.info(pos)
		if pos == 0:
			name = name[pos + 1:]
		logging.info(name)
		if not name in bot.dispatcher.doc:
			for _name, info in bot.dispatcher.doc.items():
				logging.info(_name)
				if name in info['commands']:
					name = _name
				if name in bot.dispatcher.doc:
					break
			if not name in bot.dispatcher.doc:
				bot.reply("Sorry, I can't help with that")
				return
		info = bot.dispatcher.doc[name]
		command = get_command_string(info, bot.config.prefix, name)
		if "\n" in info['doc'] or info['example']:
			bot.reply('Check your PM for help.')
			bot.msg(input.user, '{0}: {1}'.format(command, info['doc']))
			if info['example']:
				bot.msg(input.user, 'e.g: {0}'.format(info['example']))
		else:
			bot.reply('{0}: {1}'.format(command, info['doc']))

list_help.commands = ['help']
