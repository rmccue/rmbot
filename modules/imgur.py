import re
import web
import json
from datetime import datetime

#uri_matcher = re.compile(r'http://(?:i\.)?imgur\.com/(\w+)\.?(?:.*)')
uri_matcher = re.compile(r'http://(?:i\.)?imgur\.com/(?:(a)(?:/(\w+))?|(\w+\b(?!/))\.?\w?)')

def group(number):
	s = '%d' % int(number)
	groups = []
	while s and s[-1].isdigit():
		groups.append(s[-3:])
		s = s[:-3]
	return s + ','.join(reversed(groups))


def pretty_date(time=False):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""
	now = datetime.utcnow()
	if type(time) is int:
		diff = now - datetime.fromtimestamp(time)
	elif isinstance(time, datetime):
		diff = now - time
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(second_diff) + " seconds ago"
		if second_diff < 120:
			return  "a minute ago"
		if second_diff < 3600:
			return str(second_diff / 60) + " minutes ago"
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return str(second_diff / 3600) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		return str(day_diff / 7) + " weeks ago"
	if day_diff < 365:
		return str(day_diff / 30) + " months ago"
	return str(day_diff / 365) + " years ago"


def query(bits, n=1):
	"""Search using SearchMash, return its JSON."""
	q = web.urllib.quote(bits.encode('utf-8'))
	uri = 'http://api.imgur.com/2/image/{0}.json'.format(q)
	bytes = web.get(uri)
	try:
		result = json.loads(bytes)
	except:
		return None
	return result

def album_query(bits, n=1):
        """Search using SearchMash, return its JSON."""
        q = web.urllib.quote(bits.encode('utf-8'))
        uri = 'http://api.imgur.com/2/album/{0}.json'.format(q)
        bytes = web.get(uri)
        try:
                result = json.loads(bytes)
        except:
                return None
        return result


def get_reddit_url(url):
	q = web.urllib.quote(url.encode('utf-8'))
	uri = 'http://api.reddit.com/api/info?url={0}&limit=1'.format(q)
	print uri
	bytes = web.get(uri)
	try:
		result = json.loads(bytes)
		post = result['data']['children'][0]['data']
		if post['over_18'] == True:
			return "'%s' - +%d/-%d - http://redd.it/%s [NSFW]" % (post['title'], post['ups'], post['downs'], post['id'])
		else:
			return "'%s' - +%d/-%d - http://redd.it/%s" % (post['title'], post['ups'], post['downs'], post['id'])
	except:
		return ''


def imgur_linkage(bot, input):
	matches = uri_matcher.search(input.group(1))
	print matches
	print input.group(1)
	if not matches:
		return

	if matches.group(1) == 'a':
		result = album_query(matches.group(2))
		guess = get_reddit_url(input.group(1))
	elif matches.group(3) is not None:
		result = query(matches.group(3))
		guess = get_reddit_url(input.group(1))

	else:
		return

	if not result:
		return bot.say("I think imgur is down...")

	if "image" in result:
		image = result['image']['image']
		title = ''
		if image['title']:
			title = image['title']

		if image['animated'] == 'true':
			title += '[GIF]'

		time = datetime.strptime(image['datetime'], '%Y-%m-%d %H:%M:%S')

		if title == '':
			text = 'Posted {0}, {1} views'.format(pretty_date(time), group(image['views']))
		else:
			text = '{0} - Posted {1}, {2} views'.format(title, pretty_date(time), group(image['views']))
	elif "album" in result:
		album = result['album']
	
		title=''
		if album['title']:
			title=album['title']
	
		imagetimes = list()
		for image in album['images']:
			imagetimes.append(datetime.strptime(image['image']['datetime'], '%Y-%m-%d %H:%M:%S'))
	
		time = max(imagetimes)
		
		if title == '':
			text = 'Posted {0}'.format(pretty_date(time))
		else:
			text = '{0} - Posted {1}'.format(title, pretty_date(time))
	else:
		return
		
	bot.say(text)
	if guess:
		bot.say(guess)

imgur_linkage.rule = r'.*(http://(?:i\.)?imgur\.com/.*)'
imgur_linkage.priority = 'low'
