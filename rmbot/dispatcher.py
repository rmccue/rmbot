import re
import logging
import sys
import os
import traceback
import imp
from twisted.internet import reactor


class Dispatcher(object):
	def __init__(self, bot):
		self.bot = bot
		self.variables = {}
		self.modules = {}

	def load_modules(self):
		modules = []
		for name in self.bot.factory.config.enable:
			try:
				file, filename, data = imp.find_module(name, ['modules'])
				module = imp.load_module(name, file, filename, data)
			except Exception, e:
				logging.error("Error loading %s: %s (in bot.py)" % (name, e))
			else:
				if hasattr(module, 'setup'):
					module.setup(self.bot)
				self.register_module(module)
				modules.append(name)
				self.modules[name] = module

		if modules:
			logging.info("Registered modules: {0}".format(', '.join(modules)))
		else:
			logging.warning("Couldn't find any modules")

		self.bind_commands()

	def reload_module(self, name):
		file, filename, data = imp.find_module(name, ['modules'])
		module = imp.load_module(name, file, filename, data)

		if hasattr(module, '__file__'):
			import os.path
			import time
			mtime = os.path.getmtime(module.__file__)
			modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))
		else:
			modified = 'unknown'

		if hasattr(module, 'setup'):
			module.setup(self.bot)

		self.register_module(module)
		self.bind_commands()
		return module, modified

	def register_module(self, module):
		# This is used by reload.py, hence it being methodised
		for name, obj in vars(module).iteritems():
			if hasattr(obj, 'commands') or hasattr(obj, 'rule') or hasattr(obj, 'event'):
				self.variables[module.__name__ + ':' + name] = obj

	def sub_nick(self, pattern):
		# These replacements have significant order
		pattern = pattern.replace('$nickname', re.escape(self.bot.nickname))
		return pattern.replace('$nick', r'%s[,:] +' % re.escape(self.bot.nickname))

	def bind(self, func):
		if not hasattr(func, 'regexp'):
			func.regexp = []
		if not hasattr(func, 'name'):
			func.name = func.__name__

		# register documentation
		if func.__doc__:
			if hasattr(func, 'example'):
				example = self.sub_nick(func.example)
			else:
				example = None
			self.doc[func.name] = {
				'doc': func.__doc__,
				'example': example,
				'commands': [],
			}
			if hasattr(func, 'commands'):
				self.doc[func.name]['commands'].extend(func.commands)
			if hasattr(func, 'rule'):
				if isinstance(func.rule, tuple):
					if len(func.rule) == 2 and isinstance(func.rule[0], list):
						self.doc[func.name]['commands'].extend(func.rule[0])
					elif len(func.rule) == 3:
						self.doc[func.name]['commands'].extend(func.rule[1])

		self.commands[func.priority].setdefault(func.event, []).append(func)

	def bind_commands(self):
		self.commands = {'high': {}, 'medium': {}, 'low': {}}
		self.doc = {}

		for name, func in self.variables.iteritems():
			if not hasattr(func, 'priority'):
				func.priority = 'medium'

			if not hasattr(func, 'thread'):
				func.thread = True

			if not hasattr(func, 'event'):
				func.event = 'privmsg'
			elif isinstance(func.event, str):
				func.event = func.event.lower()

			func.regexp = []

			if hasattr(func, 'rule'):
				if isinstance(func.rule, str):
					pattern = self.sub_nick(func.rule)
					func.regexp.append(re.compile(pattern))
					self.bind(func)

				if isinstance(func.rule, tuple):
					# 1) e.g. ('$nick', '(.*)')
					if len(func.rule) == 2 and isinstance(func.rule[0], str):
						prefix, pattern = func.rule
						prefix = self.sub_nick(prefix)
						func.regexp.append(re.compile(prefix + pattern))
						self.bind(func)

					# 2) e.g. (['p', 'q'], '(.*)')
					elif len(func.rule) == 2 and isinstance(func.rule[0], list):
						prefix = re.escape(self.bot.config.prefix)
						commands, pattern = func.rule
						for command in commands:
							command = r'(%s)\b(?: +(?:%s))?' % (command, pattern)
							func.regexp.append(re.compile(prefix + command))
						self.bind(func)

					# 3) e.g. ('$nick', ['p', 'q'], '(.*)')
					elif len(func.rule) == 3:
						prefix, commands, pattern = func.rule
						prefix = self.sub_nick(prefix)
						for command in commands:
							command = r'(%s) +' % command
							func.regexp.append(re.compile(prefix + command + pattern))
						self.bind(func)

			if hasattr(func, 'commands'):
				for command in func.commands:
					template = r'^%s(%s)(?: +(.*))?$'
					pattern = template % (re.escape(self.bot.config.prefix), command)
					func.regexp.append(re.compile(pattern))
				self.bind(func)

			if not hasattr(func, 'rule') and not hasattr(func, 'commands'):
				self.bind(func)

	def notify(self, event, origin=None, args=[]):
		event = event.lower()
		logging.debug('Dispatching event {0}'.format(event))
		for priority in ('high', 'medium', 'low'):
			items = self.commands[priority]
			if not event in items:
				logging.debug('No observers for {0}'.format(event))
				continue

			for func in items.get(event):
				if event == 'privmsg':
					text = unicode(args[0], 'utf-8', errors='ignore')
				else:
					text = ','.join(args)

				match = False
				if func.regexp:
					for regex in func.regexp:
						match = regex.match(text)
						logging.debug('Checking {1}: {2}'.format(text.encode('utf-8'), regex.pattern, bool(match)))
						if match:
							break
				else:
					match = True

				if match:
					#if self.limit(origin, func): continue

					bot = self.wrapped(origin, args)
					input = self.input(origin, text, match, event, args)

					if func.thread and False:  # TODO: reenable threading here
						targs = (func, origin, bot, input)
						reactor.callInThread(self.call, targs)
					else:
						self.call(func, origin, bot, input)

	def call(self, func, origin, bot, input):
		try:
			func(bot, input)
		except Exception:
			self.error(origin)

	def error(self, origin):
		print >> sys.stderr, 'error!'
		try:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback)

			lines = traceback.extract_tb(exc_traceback)
			source = traceback.format_list(lines[-1:])[0].splitlines()[0].strip()
			self.bot.msg(origin.channel, traceback.format_exception_only(exc_type, exc_value)[0].strip() + ' (' + source + ')')
		except Exception, e:
			print e
			self.bot.msg(origin.channel, "Got an error.")

	def wrapped(self, origin, args):
		class BotWrapper(object):
			def __init__(self, bot):
				self.bot = bot

			def __getattr__(self, attr):
				if attr == 'motion':
					return (lambda msg:
						self.bot.action(origin.channel, msg))
				elif attr == 'reply':
					return (lambda msg:
						self.bot.msg(origin.channel, origin.user + ': ' + msg))
				elif attr == 'say':
					return lambda msg: self.bot.msg(origin.channel, msg)
				return getattr(self.bot, attr)

		return BotWrapper(self.bot)

	def input(self, origin, text, match, event, args):
		class CommandInput(unicode):
			def __new__(cls, text, origin, match, event, args):
				s = unicode.__new__(cls, text)
				s.sender = s.channel = origin.channel
				s.nick = s.user = origin.user
				s.event = event
				s.match = match
				if hasattr(match, 'group'):
					s.group = match.group
					s.groups = match.groups
				else:
					s.group = lambda x: None
					s.groups = lambda x: ()
				s.args = args
				s.admin = origin.user in self.bot.config.admins
				s.owner = origin.user == self.bot.config.owner
				return s

		return CommandInput(text, origin, match, event, args)
