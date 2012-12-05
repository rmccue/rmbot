"""
This library lets you open chat session with cleverbot (www.cleverbot.com)

Example of how to use the bindings:

>>> import cleverbot
>>> cb=cleverbot.Session()
>>> print cb.Ask("Hello there")
'Hello.'

"""

import urllib
import urllib2
import re

# md5 depreciated in Python 2.5
try:
	from hashlib import md5
except ImportError:
	from md5 import md5

class ServerFullError(Exception):
	pass

class Session:
	params = {
		'stimulus': '',
		'start': 'y',
		'sessionid': '',
		'vText8': '',
		'vText7': '',
		'vText6': '',
		'vText5': '',
		'vText4': '',
		'vText3': '',
		'vText2': '',
		'icognoid': 'wsf',
		'icognocheck': '',
		'prevref': '',
		'emotionaloutput': '',
		'emotionalhistory': '',
		'asbotname': '',
		'ttsvoice': '',
		'typing': '',
		'lineref': '',
		'sub': 'Say',
		'islearning': '1',
		'cleanslate': 'false',
		'fno': '0'
	}
	headers={}
	headers['User-Agent']='Mozilla/5.0 (X11; U; Linux x86_64; it; rv:1.9.1.8) Gecko/20100214 Ubuntu/9.10 (karmic) Firefox/3.5.8'
	headers['Accept']='text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
	headers['Accept-Language']='it-it,it;q=0.8,en-us;q=0.5,en;q=0.3'
	headers['X-Moz']='prefetch'
	headers['Accept-Charset']='ISO-8859-1,utf-8;q=0.7,*;q=0.7'
	headers['Referer']='http://www.cleverbot.com'
	headers['Cache-Control']='no-cache, no-cache'
	headers['Pragma']='no-cache'

	def __init__(self):
		self.MsgList=[]

	def Send(self):
		data = urllib.urlencode(self.params)
		digest_txt = data[9:29]
		self.params['icognocheck'] = md5(digest_txt).hexdigest()
		data = urllib.urlencode(self.params)
		req = urllib2.Request("http://www.cleverbot.com/webservicemin", data, self.headers)
		f = urllib2.urlopen(req)
		reply = f.read()
		return reply

	def Ask(self,q):
		self.params['stimulus'] = q.encode('utf-8')
		if self.MsgList:
			self.params['lineref'] = '!0'+str(len(self.MsgList)/2)

		self.previous()
		asw = self.Send()
		if '<meta name="description" content="Jabberwacky server maintenance">' in asw:
			raise ServerFullError, "The Cleverbot server answered with full load error"
		self.MsgList.append(q)
		self.params['emotionaloutput']=''
		self.params['prevref'] = prevref(asw)
		text = asw.split("\r")[0]
		self.MsgList.append(text)
		return text

	def previous(self):
		latest = self.MsgList[-7:]
		for i in range(2,9):
			if len(latest) == 0:
				break
			num = 'vText{0}'.format(i)
			self.params[num] = latest.pop().encode('utf-8')

def prevref(text):
	pos = text.split('\r')
	return pos[10]
