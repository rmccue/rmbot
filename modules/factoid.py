import logging
import re
import random

factoids = {}
variables = {}

def setup(bot):
	global factoids

	factoids = bot.db.get('factoids.facts')
	if not factoids:
		factoids = {
			"default": {
				"MonkeyCrumpets": [ ("reply", "Strange...") ],
			},
		}
	variables = bot.db.get('factoids.variables')
	if not variables:
		variables = {}


def replace_tokens(bot, input, string):
	for name, value in variables.iteritems():
		value = random.choice(value)
		string = string.replace('$' + name, value)

	string = string.replace('$who', input.nick)
	return string


def access_variable(bot, input):
	"""Get or define a variable to substitute in facts

	In facts, $var will be replaced with the value set here if there is one.
	$who will also be substituted with the sender."""
	var = input.group(1).lower()
	if var == 'who':
		bot.reply('Cannot set $who')
		return

	if not input.group(2):
		# Get the value
		if var not in variables:
			bot.reply('{0} is not set'.format(var))
		else:
			bot.reply( '${0} = {1}'.format( var, '|'.join( variables[var] ) ) )
	elif input.group(2) == '=':
		variables.setdefault(var, []).append(input.group(3))
		bot.reply('${0} = {1}'.format(var, input.group(3)))
	elif input.group(2) == 'unset':
		if var not in variables:
			bot.reply('{0} is not set'.format(var))
			return

		try:
			index = variables[var].index( input.group(3) )
			del variables[var][index]
			if len(variables[var]) == 0:
				del variables[var]
			bot.reply('Deleted.')
		except ValueError:
			bot.reply("Couldn't find that value.")

access_variable.rule = ('$nick', '\$(\w+)(?: (=|unset) (.*))?')
access_variable.example = 'rmbot: $a = b, or rmbot: $a, or rmbot: $a unset b'


def define(bot, input):
	"""Define a fact to respond to, in the form '$nick: x <verb> y' where verb is anything

	x <action> y responds with '/me y'
	x <alias> y pretends x was y
	x <reply> y responds with '$sender: y'
	x <say> y responds with 'y'
	Anything else responds with 'x verb y'
	See also the access_variable command.
	"""

	if input.group(1):
		# a <verb> b
		fact, verb, _, _, definition = input.groups()
	else:
		_, _, fact, verb, definition = input.groups()

	try:
		chance = random.randint(0, 9999) / 100.0

		if chance <= bot.config.your_mom_chance:
			bot.reply('Your mum {0} {1}!'.format(verb, definition))
			return
	except AttributeError:
		pass

	factoids.setdefault( input.sender, {} ).setdefault( fact.strip(), [] ).append( ( verb.strip(), definition.strip() ) )
	bot.db.set('factoids.facts', factoids)

	bot.reply( "Okay.".format( fact.strip() ) )

define.rule = ('$nick', r'(?:(.*) *<([^>]+)> *|(.+?) +(is|are) +)(.+)')


def list_factoids(bot, input):
	pass

list_factoids.rule = ('$nick', )


def display(bot, input, fact = None):
	if not input.sender.startswith('#'):
		return

	channel_factoids = factoids['default'].copy()
	channel_factoids.update( factoids.setdefault( input.sender, {} ) )
	if not fact:
		fact = input.strip()

	if fact in channel_factoids:
		verb, response = random.choice(channel_factoids[fact])
		if verb == 'alias':
			return display(bot, input, response)

		response = replace_tokens(bot, input, response)

		if verb == 'reply':
			bot.reply(response)
		elif verb == 'action':
			bot.motion(response)
		elif verb == 'say':
			bot.say(response)
		else:
			bot.say("{0} {1} {2}".format(fact, verb, response))

display.rule = r'.'


def display_on_action(bot, input):
	display(bot, input)

display_on_action.event = 'action'
display_on_action.rule = r'.'