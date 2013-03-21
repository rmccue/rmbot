checkurl = 'http://xpaw.ru/mcstatus/status.json'

import web
import json

def getstatus():
        body = web.get(checkurl)
        result = json.loads(body)
        return result['report']


def mcstatus(bot, input):

        try:
                deadservers = []

                results = getstatus()

                for server in results:

                        if results[server]['status'] != 'up':

                                deadservers.append(server)

                if len(deadservers) == 0:

                        bot.reply('Servers seem fine to me :)')

                else:   
                        deadserverlist = ', '.join(deadservers)

                        bot.reply('Looks like there could be problems with ' + deadserverlist + '. See more at http://xpaw.ru/mcstatus/')


        except e:
                bot.reply('Erm, something broke :/')

mcstatus.commands = ['mcstatus']

