apiurl = 'http://en.wikipedia.org/w/api.php?action=query&format=json' \
	'&prop=info|extracts&exsentences=1&explaintext&inprop=url|displaytitle&{0}'

singlepage = 'titles={0}'
searchquery = 'generator=search&gsrsearch={0}&gsrlimit=1'

import web
import json


class NotFound(Exception):
	def __init__(self, suggestion=u''):
		self.suggestion = suggestion


def search(term):
	uri = apiurl.format(searchquery)
	uri = uri.format(term)
	body = web.get(uri)
	result = json.loads(body)
	if result['query']['searchinfo']['totalhits'] < 1:
		if 'suggestion' in result['query']['searchinfo']:
			raise NotFound(result['query']['searchinfo']['suggestion'])
		else:
			raise NotFound()

	page = result['query']['pages'].values()[0]
	page['searchhits'] = result['query']['searchinfo']['totalhits']
	return page


def get_page(name):
	uri = apiurl.format(singlepage)
	uri = uri.format(name)
	result = json.loads(web.get(uri))
	page = result['query']['pages'].values()[0]

	if 'missing' in page:
		raise NotFound()

	return page


def wpsearch(bot, input):
	term = input.groups()[1]

	try:
		result = search(term)
		bot.reply(u'{0} - {1} ({2} results found)'.format(
			result['extract'].strip(),
			result['fullurl'],
			result['searchhits']
		))
	except NotFound, e:
		if e.suggestion:
			bot.reply(u'No results found. Maybe you meant {0}?'.format(e.suggestion))
		else:
			bot.reply('No results found, sorry!')
wpsearch.commands = ['wik']


def wplinker(bot, input):
	term = input.groups()[0]

	try:
		result = get_page(term)
		bot.reply(u'{0} - {1}'.format(
			result['extract'].strip(),
			result['fullurl']
		))
	except NotFound:
		bot.reply('Page does not appear to exist.')
wplinker.rule = r'.*http://en.wikipedia.org/wiki/([\w:-]+).*'
wplinker.priority = 'low'
