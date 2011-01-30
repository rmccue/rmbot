
import irc
import urllib2
def f_pick(bot, input): 
	min = input.group(1)
	max = input.group(2)
	url = "http://www.random.org/integers/?num=1&min=%s&max=%s&col=1&base=10&format=plain&rnd=new" % (min, max)
	try:
		result = urllib2.urlopen(url)
	except urllib2.HTTPError, e:
		response = e.read().replace('Error: ', '')
		bot.reply('Whoops! %s' % (response, ))
		return
	bot.reply('RNG is: %s' % result.read())
f_pick.rule = r'^\.pick (-?\d+)[-|,](-?\d+)?$'