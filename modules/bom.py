import re
import web
from datetime import datetime, timedelta
from collections import defaultdict

states = {
	'qld': 'qld',
	'queensland': 'qld',
	'nsw': 'nsw',
	'new south wales': 'nsw',
	'vic': 'vic',
	'victoria': 'vic',
	'tas': 'tas',
	'tasmania': 'tas',
	'sa': 'sa',
	'south australia': 'sa',
	'wa': 'wa',
	'western australia': 'wa',
	'nt': 'nt',
	'northern territory': 'nt',
	'act': 'act',
	'australian capital territory': 'act'
}

base = 'http://www.bom.gov.au/{0}/observations/{1}.shtml'
content_matcher = re.compile('<!-- Start: Content -->(.*?)<!-- End: Content -->', re.DOTALL)
region_matcher = re.compile('<tbody> <!-- abcd open product tbody -->(.*?)</tbody> <!-- abcd close product tbody for this division -->', re.DOTALL)
outer_matcher = re.compile('<tr.*?>(.*?)</tr>', re.DOTALL)
cell_matcher = re.compile('<td headers="(.*?)">(.*?)</td>', re.DOTALL)

cacheduration = timedelta(minutes=30)

weatherdata = {}
places = defaultdict(list)

def update(state):
	region = state + 'all'
	if state is 'act':
		region = 'canberra'

	data = web.get(base.format(state, region))
	table = ''.join(region_matcher.findall(data))
	rows = outer_matcher.findall(table)
	statedata = {}

	for row in rows:
		station = re.search('<a href.*?>(.*?)</a>', row, re.DOTALL)
		if not station:
			continue

		station = station.group(1)
		data = {}
		data['updated'] = datetime.now()
		data['name'] = station
		cells = cell_matcher.findall(row)
		for cell in cells:
			headers = cell[0].split(' ')
			prefix = headers[0].split('-')[0]
			celltype = headers[0].replace(prefix + '-', '')
			value = cell[1]
			if value == '-':
				value = None

			if celltype == 'tmp' or celltype == 'temp':
				data['temp'] = value
			elif celltype == 'apptmp' or celltype == 'apptemp':
				data['apparenttemp'] = value
			elif celltype == 'relhum':
				data['humidity'] = value
			elif celltype == 'pressure' or celltype == 'press':
				data['pressure'] = value
			elif celltype == 'rainsince9am':
				data['rain'] = float(value) if value and value != 'Trace' else 0.0
			elif celltype == 'wind':
				subtype = headers[1].replace(prefix + '-', '')
				if not 'wind' in data:
					data['wind'] = {}
				if subtype == 'wind-dir':
					data['wind']['dir'] = value
				elif subtype == 'wind-spd-kmh' or subtype == 'wind-spd-kph':
					data['wind']['speed'] = value
				elif subtype == 'wind-gust-kmh' or subtype == 'wind-gust-kph':
					data['wind']['gust'] = value

		statedata[station.lower()] = data
		places[state].append(station)

	weatherdata[state] = statedata


def get_weather(place, statecode):
	try:
		data = weatherdata[statecode][place]
		if (datetime.now() - data['updated']) > cacheduration:
			update(statecode)
			data = weatherdata[statecode][place]
	except KeyError:
		update(statecode)
		data = weatherdata[statecode][place]

	return data


def levenshtein(a,b):
	"Calculates the Levenshtein distance between a and b."
	n, m = len(a), len(b)
	if n > m:
		# Make sure n <= m, to use O(min(n,m)) space
		a,b = b,a
		n,m = m,n
		
	current = range(n+1)
	for i in range(1,m+1):
		previous, current = current, [i]+[0]*n
		for j in range(1,n+1):
			add, delete = previous[j]+1, current[j-1]+1
			change = previous[j-1]
			if a[j-1] != b[i-1]:
				change = change + 1
			current[j] = min(add, delete, change)
			
	return current[n]


def guess_place(place, state):
	possible = places[state]
	candidates = []
	for possible in places[state]:
		data = (possible, levenshtein(place.lower(), possible.lower()))
		candidates.append(data)
	candidates.sort(key=lambda x: x[1])
	return candidates[0][0]


def reload(bot, state):
	state = state.strip()

	try:
		statecode = states[state.lower()]
	except KeyError:
		return bot.reply('{0} is not a valid state'.format(state))

	update(statecode)
	return bot.reply('Updated {0}'.format(state))


def bom(bot, input):
	if not input.group(2):
		return bot.reply('Please specify a location (in form Place, State)')

	if input.group(2).startswith('reload') and input.admin:
		_, state = input.group(2).split(' ')
		return reload(bot, state)

	place = input.group(2)
	if ',' in place:
		place, state = place.split(',', 2)
	else:
		state = None
		for possible in states.keys():
			pos = place.lower().find(' ' + possible.lower())
			if pos == -1:
				continue

			state = possible
			place = place[:pos]
		if not state:
			return bot.reply('Please specify a state')

	state = state.strip()

	try:
		statecode = states[state.lower()]
	except KeyError:
		return bot.reply('{0} is not a valid state'.format(state))

	try:
		data = get_weather(place.lower(), statecode)
	except KeyError:
		possible = guess_place(place, statecode)
		return bot.reply('{0} is not a valid place in {1}. Maybe you meant {2}?'.format(place, state, possible))

	bits = []
	if data['temp']:
		bits.append(u'{0} C'.format(data['temp']))  # \u00B0
	if data['apparenttemp']:
		bits.append(u'({0} C apparent)'.format(data['apparenttemp']))
	if data['humidity']:
		bits.append('Humidity {0}%'.format(data['humidity']))
	if data['pressure']:
		bits.append('Pressure: {0}hPa'.format(data['pressure']))
	if data['rain'] and data['rain'] > 0:
		bits.append('Rain since 9am: {0}mm'.format(data['rain']))
	if data['wind'] and data['wind']['speed']:
		gust = ''
		if data['wind']['gust']:
			gust += ' (Gusting to {0} km/h)'.format(data['wind']['gust'])
		bits.append('Wind: {0} km/h ({1}){2}'.format(data['wind']['speed'], data['wind']['dir'], gust))

	reply = '{0}: {1}'.format(data['name'], ', '.join(bits).encode('utf-8'))
	return bot.reply(reply)

bom.rule = (['bom'], r'(.*)')
bom.example = '.bom Brisbane, QLD'

def bomb(bot, input):
	bot.reply('1. A robot may not injure a human being or, through inaction, allow a human being to come to harm.')

bomb.commands = ['bomb']