
def startup(bot, input):
	# Cf. http://swhack.com/logs/2005-12-05#T19-32-36
	for channel in bot.channels: 
		bot.write(('JOIN', channel))

startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'