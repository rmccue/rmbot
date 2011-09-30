#!/usr/bin/env python

""" this is the help.py function """

def f_help(bot, input): 
   """
   syntax: .f_help 
   returns a list of the available modules.
   type .<module> for specific f_help.
   """
   bot.reply("Listing available modules...")
   for fn in bot.enable:
      bot.reply(" %s", fn)
   bot.reply("Done.")
      
#f_help.rule = ['f_help']
f_help.priority = 'low'
#f_help.rule = r'(.*)'
f_help.rule = (['help'], r'(\S+)')




if __name__ == '__main__': 
   print __doc__.strip()
