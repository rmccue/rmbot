# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log as twistedlog

# system imports
import sys
import imp
import os
import re
import traceback
import logging
import inspect


home = os.getcwd()

class Origin(object):
	user = ''
	host = ''
	channel = ''

	def __init__(self, user=None, channel=None): 
		if user:
			try:
				self.user, self.host = user.split('!')
			except ValueError:
				self.user = user
		if channel:
			self.channel = channel

	def __getattr__(self, name):
		deprecated = {'nick': 'user', 'sender': 'channel'}
		if name in deprecated:
			try:
				stack = inspect.stack()[1]
				source = '{0}() ({1}:{2})'.format(stack[3], stack[1], stack[2])
			except Exception, e:
				print e
				source = 'unknown'
			logging.warning("Using deprecated origin.{0} in {1}".format(name, source))
			return getattr(self, deprecated[name])
		else:
			raise AttributeError

class rmbot(irc.IRCClient):
	"""An awesome IRC bot."""

	nickname = "rmbot_v2"

	def __init__(self, factory):
		self.factory = factory
		self.nickname = self.factory.config.nick
		self.realname = self.factory.config.name
		self.password = self.factory.config.password
		self.sourceURL = 'https://github.com/rmccue/rmbot'

		self.doc = {}
		self.stats = {}
		self.commands = {'high': {}, 'medium': {}, 'low': {}}
		self.setup()

	def __getattr__(self, name):
		if name == 'config':
			return self.factory.config

		deprecated = {'nick': 'nickname'}
		if name in deprecated:
			try:
				stack = inspect.stack()[1]
				if stack[3] == '__getattr__':
					stack = inspect.stack()[2]
				source = '{0}() ({1}:{2})'.format(stack[3], stack[1], stack[2])
			except Exception, e:
				print e
				source = 'unknown'
			logging.warning("Using deprecated rmbot.{0} in {1}".format(name, source))
			return getattr(self, deprecated[name])
		else:
			raise AttributeError

	def setup(self): 
		self.variables = {}

		filenames = []
		for fn in self.factory.config.enable: 
			filenames.append(os.path.join(home, 'modules', fn + '.py'))

		modules = []
		for filename in filenames: 
			name = os.path.basename(filename)[:-3]
			try: module = imp.load_source(name, filename)
			except Exception, e: 
				logging.error("Error loading %s: %s (in bot.py)" % (name, e))
			else: 
				if hasattr(module, 'setup'): 
					module.setup(self)
				self.register_module(vars(module))
				modules.append(name)

		if modules: 
			logging.info("Registered modules: {0}".format(', '.join(modules)))
		else:
			logging.warning("Couldn't find any modules")

		self.bind_commands()

	def register_module(self, variables): 
		# This is used by reload.py, hence it being methodised
		for name, obj in variables.iteritems():
			if hasattr(obj, 'commands') or hasattr(obj, 'rule') or hasattr(obj, 'event'):
				self.variables[name] = obj

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)

	# Observer pattern

	def bind_commands(self):
		self.commands = {'high': {}, 'medium': {}, 'low': {}}
		
		def bind(self, func): 
			if not hasattr(func, 'regexp'):
				func.regexp = []
			if not hasattr(func, 'name'):
				func.name = func.__name__

			# register documentation
			if func.__doc__:
				if hasattr(func, 'example'): 
					example = sub(func.example)
				else: example = None
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

		def sub(pattern, self=self): 
			# These replacements have significant order
			pattern = pattern.replace('$nickname', self.nickname)
			return pattern.replace('$nick', r'%s[,:] +' % self.nickname)

		for name, func in self.variables.iteritems(): 
			# print name, func
			if not hasattr(func, 'priority'): 
				func.priority = 'medium'

			if not hasattr(func, 'thread'): 
				func.thread = True

			if not hasattr(func, 'event'): 
				func.event = 'privmsg'
			elif isinstance(func.event, str):
				func.event = func.event.lower()

			if not hasattr(func, 'regexp'):
				func.regexp = []

			if hasattr(func, 'rule'):
				if isinstance(func.rule, str): 
					pattern = sub(func.rule)
					func.regexp.append(re.compile(pattern))
					bind(self, func)

				if isinstance(func.rule, tuple): 
					# 1) e.g. ('$nick', '(.*)')
					if len(func.rule) == 2 and isinstance(func.rule[0], str): 
						prefix, pattern = func.rule
						prefix = sub(prefix)
						func.regexp.append(re.compile(prefix + pattern))
						bind(self, func)

					# 2) e.g. (['p', 'q'], '(.*)')
					elif len(func.rule) == 2 and isinstance(func.rule[0], list): 
						prefix = re.escape(self.config.prefix)
						commands, pattern = func.rule
						for command in commands: 
							command = r'(%s)\b(?: +(?:%s))?' % (command, pattern)
							func.regexp.append(re.compile(prefix + command))
						bind(self, func)

					# 3) e.g. ('$nick', ['p', 'q'], '(.*)')
					elif len(func.rule) == 3: 
						prefix, commands, pattern = func.rule
						prefix = sub(prefix)
						for command in commands: 
							command = r'(%s) +' % command
							func.regexp.append(re.compile(prefix + command + pattern))
						bind(self, func)

			if hasattr(func, 'commands'): 
				for command in func.commands: 
					template = r'^%s(%s)(?: +(.*))?$'
					pattern = template % (re.escape(self.config.prefix), command)
					func.regexp.append(re.compile(pattern))
				bind(self, func)

			if not hasattr(func, 'rule') and not hasattr(func, 'commands'):
				bind(self, func)

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
						match = match or regex.match(text)
						logging.debug('Checking {1}: {2}'.format(text.encode('utf-8'), regex.pattern, bool(match)))
				else:
					match = True

				if match:
					#if self.limit(origin, func): continue

					bot = self.wrapped(origin, args)
					input = self.input(origin, text, match, event, args)

					if func.thread and False: # TODO: reenable threading here
						targs = (func, origin, bot, input)
						reactor.callInThread(self.call, targs)
					else:
						self.call(func, origin, bot, input)

					for source in [origin.channel, origin.user]:
						try: self.stats[(func.name, source)] += 1
						except KeyError:
							self.stats[(func.name, source)] = 1

	def call(self, func, origin, bot, input):
		try:
			func(bot, input)
		except Exception:
			self.error(origin)

	def error(self, origin):
		print >> sys.stderr, 'error!'
		try:
			trace = traceback.format_exc()
			print trace
			lines = list(reversed(trace.splitlines()))

			report = [lines[0].strip()]
			for line in lines: 
				line = line.strip()
				if line.startswith('File "/'): 
					report.append(line[0].lower() + line[1:])
					break
			else: report.append('source unknown')

			self.msg(origin.channel, report[0] + ' (' + report[1] + ')')
		except: self.msg(origin.channel, "Got an error.")

	def wrapped(self, origin, args):
		class BotWrapper(object):
			def __init__(self, bot):
				self.bot = bot

			def __getattr__(self, attr):
				if attr == 'reply':
					return (lambda msg:
						self.bot.msg(origin.channel, origin.user + ': ' + msg))
				elif attr == 'say':
					return lambda msg: self.bot.msg(origin.channel, msg)
				return getattr(self.bot, attr)

		return BotWrapper(self)

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
					s.group = None
					s.groups = None
				s.args = args
				s.admin = origin.user in self.config.admins
				s.owner = origin.user == self.config.owner
				return s

		return CommandInput(text, origin, match, event, args)


	# Abilities

	action = irc.IRCClient.describe
	def msg(self, user, message, length=None):
		irc.IRCClient.msg(self, user, message.encode('utf-8'), length)

	def join(self, channel, key=None):
		irc.IRCClient.join(self, channel.encode('utf-8'), key)


	## Events

	### Methods involving me directly

	def privmsg(self, user, channel, message):
		"""
		Called when I have a message from a user to me or a channel.
		"""
		self.notify('privmsg', Origin(user, channel), [message])

	def joined(self, channel):
		"""
		Called when I finish joining a channel.

		channel has the starting character (C{'#'}, C{'&'}, C{'!'}, or C{'+'})
		intact.
		"""
		self.notify('joined', Origin(channel=channel))

	def left(self, channel):
		"""
		Called when I have left a channel.

		channel has the starting character (C{'#'}, C{'&'}, C{'!'}, or C{'+'})
		intact.
		"""
		self.notify('left', Origin(channel=channel))

	def noticed(self, user, channel, message):
		"""
		Called when I have a notice from a user to me or a channel.

		If the client makes any automated replies, it must not do so in
		response to a NOTICE message, per the RFC::

			The difference between NOTICE and PRIVMSG is that
			automatic replies MUST NEVER be sent in response to a
			NOTICE message. [...] The object of this rule is to avoid
			loops between clients automatically sending something in
			response to something it received.
		"""
		self.notify('noticed', Origin(user, channel), [message])

	def modeChanged(self, user, channel, set, modes, args):
		"""
		Called when users or channel's modes are changed.

		@type user: C{str}
		@param user: The user and hostmask which instigated this change.

		@type channel: C{str}
		@param channel: The channel where the modes are changed. If args is
		empty the channel for which the modes are changing. If the changes are
		at server level it could be equal to C{user}.

		@type set: C{bool} or C{int}
		@param set: True if the mode(s) is being added, False if it is being
		removed. If some modes are added and others removed at the same time
		this function will be called twice, the first time with all the added
		modes, the second with the removed ones. (To change this behaviour
		override the irc_MODE method)

		@type modes: C{str}
		@param modes: The mode or modes which are being changed.

		@type args: C{tuple}
		@param args: Any additional information required for the mode
		change.
		"""
		self.notify('modeChanged', Origin(user, channel), [set, modes, args])

	def pong(self, user, secs):
		"""
		Called with the results of a CTCP PING query.
		"""
		self.notify('pong', Origin(user=user), [secs])

	def signedOn(self):
		"""
		Called after sucessfully signing on to the server.
		"""
		for channel in self.factory.config.channels:
			self.join(channel)
		self.notify('signedOn')

	def kickedFrom(self, channel, kicker, message):
		"""
		Called when I am kicked from a channel.
		"""
		self.notify('kickedFrom')

	def nickChanged(self, nick):
		"""
		Called when my nick has been changed.
		"""
		self.nickname = nick
		self.notify('nickChanged')


	### Things I observe other people doing in a channel.

	def userJoined(self, user, channel):
		"""
		Called when I see another user joining a channel.
		"""
		self.notify('userJoined', Origin(user, channel))

	def userLeft(self, user, channel):
		"""
		Called when I see another user leaving a channel.
		"""
		self.notify('userLeft', Origin(user, channel))

	def userQuit(self, user, quitMessage):
		"""
		Called when I see another user disconnect from the network.
		"""
		self.notify('userQuit', Origin(user), [quitMessage])

	def userKicked(self, kickee, channel, kicker, message):
		"""
		Called when I observe someone else being kicked from a channel.
		"""
		self.notify('userKicked', Origin(channel=channel), [kickee, kicker, message])

	def action(self, user, channel, data):
		"""
		Called when I see a user perform an ACTION on a channel.
		"""
		self.notify('action', Origin(user, channel), [data])

	def topicUpdated(self, user, channel, newTopic):
		"""
		In channel, user changed the topic to newTopic.

		Also called when first joining a channel.
		"""
		self.notify('topicUpdated', Origin(user, channel), [newTopic])

	def userRenamed(self, oldname, newname):
		"""
		A user changed their name from oldname to newname.
		"""
		self.notify('userRenamed', Origin(oldname), [newname])

	### Information from the server.

	def receivedMOTD(self, motd):
		"""
		I received a message-of-the-day banner from the server.

		motd is a list of strings, where each string was sent as a seperate
		message from the server. To display, you might want to use::

			'\\n'.join(motd)

		to get a nicely formatted string.
		"""
		self.notify('receivedMOTD', args=[motd])


class BotFactory(protocol.ClientFactory):
	"""A factory for LogBots.

	A new protocol instance will be created each time we connect to the server.
	"""

	def __init__(self, config):
		self.config = config

	def buildProtocol(self, addr):
		p = rmbot(self)
		return p

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		logging.warning('Disconnected. Reconnecting...')
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		logging.error('Connection failed: {0}'.format(reason))
		reactor.stop()

def main():
	#name = os.path.basename(config_name).split('.')[0] + '_config'
	config = imp.load_source('rng_config', './config.py')
	config.filename = './config.py'

	if not hasattr(config, 'prefix'): 
		config.prefix = '.'

	if not hasattr(config, 'name'): 
		config.name = 'rmbot the awesome'

	if not hasattr(config, 'port'): 
		config.port = 6667

	logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
	observer = twistedlog.PythonLoggingObserver()
	observer.start()

	# create factory protocol and application
	f = BotFactory(config)

	# connect factory to this host and port
	reactor.connectTCP(config.host, config.port, f)

	# run bot
	reactor.run()

if __name__ == '__main__':
	main()