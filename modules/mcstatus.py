checkurl = 'http://xpaw.ru/mcstatus/status.json'

import web
import json
from twisted.internet import task

laststatus = {}

def getstatus():
	body = web.get(checkurl)
	result = json.loads(body)
	return result['report']


descs = {'login': 'Login server', 'session': 'Session server', 'website': 'Minecraft website', 'skins': 'Skin server', 'realms': 'Realms service'}
statuses = {'up': 'has come back up after {0} minutes', 'down': 'has gone down', 'problem': 'is experiencing problems'}

def mcstatus(bot, input):

	try:
		deadservers = []
		dyingservers = []
		results = getstatus()
		reply = u''

		for server in results:
			if results[server]['status'] == 'down':
				reply += u'{0} has been down for {1} minutes. '.format(descs[server] if server in descs else server, results[server]['downtime'])
			if results[server]['status'] == 'problem':
				reply += u'{0} has a problem: {1}. '.format(descs[server] if server in descs else server, results[server]['title'])

		if len(reply) == 0:
			reply = 'Mojang\'s servers all seem fine to me :) '

		if 'psa' in results:
			reply += results['psa'] + u' '
		bot.reply(u'{0}See more at http://xpaw.ru/mcstatus/'.format(reply))


	except Exception, e:
		bot.reply('Erm, something broke :/')
		import traceback
		traceback.print_exc(e)

mcstatus.commands = ['mcstatus']

def mcstatus_check(bot):
	verbose = True

	try:
		results = getstatus()
	except:
		return
	send = u''
	all_up = True
	for server in results:
		s = results[server]['status']
		if verbose:
			if server in laststatus and laststatus[server] != results[server]['status']:
				send += '{0} {1}. '.format(descs[server] if server in descs else server, statuses[s].format(results[server]['downtime'] if 'downtime' in results[server] else '') if s in statuses else s)
		laststatus[server] = s
		if s != 'up':
			all_up = False

	if all_up != laststatus['all_up']:
		send = 'Mojang servers are up again! Yay :D' if all_up else 'Mojang servers just went down :( ' + send
	laststatus['all_up'] = all_up
	bot.msg('#mcau', send.strip())


def mcstatus_setup(bot, input):

	try:
		results = getstatus()
	except:
		return # abandon and don't even start checking
	global laststatus
	all_up = True
	for server in results:
		laststatus[server] = results[server]['status']
		if results[server]['status'] != 'up': all_up = False
	laststatus['all_up'] = all_up

	global checktask
	checktask = task.LoopingCall(mcstatus_check, bot)
	checktask.start(60.0)

def teardown(bot, reloading):
	"Called when the module is being unloaded"
	checktask.stop()

mcstatus_setup.event = 'signedon'
mcstatus_setup.priority = 'low'
