#!/usr/bin/env python
#
# IRC Bot to moderate a game of "Werewolf".
#
#    by Ben Collins-Sussman <sussman@red-bean.com>
#       http://www.red-bean.com/sussman
#
# Werewolf is a traditional party game, sometimes known as 'Mafia',
# with dozens of variants.  This bot is following Andrew Plotkin's rules:
# http://www.eblong.com/zarf/werewolf.html
#
# Code originally based on example bot and irc-bot class from
# Joel Rosdahl <joel@rosdahl.net>, author of included python-irclib.
#


"""An IRC bot to moderate a game of "Werewolf".

This is an example bot that uses the SingleServerIRCBot class from
ircbot.py.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.

The known commands are:

    die -- Let the bot cease to exist.

    start game -- start a new werewolf game.

    end game -- quit the current werewolf game.

    stats -- print information about living/dead people.
    
"""

import sys, string, random
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower

#---------------------------------------------------------------------

# General texts for narrating the game.  Change these global strings
# however you wish.


# Printed when a game first starts.

new_game_text = "This is a game of paranoia and psychological intrigue.  Everyone in this group appears to be a common villager, but three of you are 'special'.  Two people are actually evil werewolves, seeking to kill everyone while concealing their identity.  And one of you is also a 'seer'; you have the ability to learn whether a specific person is or is not a werewolf.  The seer might not want to reveal his/her identify, as s/he becomes a prime werewolf target.  As a community, your group objective is to weed out the werewolves and lynch them both, before you're all killed in your sleep."


# Printed when night begins.

# Printed when day begins.

# Printed when the wolves kill somebody (night ends).

# Printed when a lynching happens.

# Printed when the wolves win.

# Printed when the villagers win.


#---------------------------------------------------------------------

class WolfBot(SingleServerIRCBot):
  def __init__(self, channel, nickname, server, port=6667):
    SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
    self.channel = channel
    self.game_in_progress = 0
    self.start()

    
  def on_nicknameinuse(self, c, e):
    c.nick(c.get_nickname() + "_")

      
  def on_welcome(self, c, e):
    c.join(self.channel)


  def on_privmsg(self, c, e):
    self.do_command(e, e.arguments()[0])


  def on_pubmsg(self, c, e):
    a = string.split(e.arguments()[0], ":", 1)
    if len(a) > 1 \
           and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
      self.do_command(e, string.strip(a[1]))
    return


  def _reset_gamedata(self):
    self.live_players = []
    self.dead_players = []
    self.wolves = []
    self.villagers = []
    self.seer = None


  def say_public(self, text):
    "Print TEXT into public channel, for all to see."

    self.connection.privmsg(self.channel, text)


  def say_private(self, nicklist, text):
    "Send private messages of TEXT to every nick in NICKLIST."

    self.connection.privmsg_many(nicklist, text)


  def start_game(self, e):
    "Initialize a werewolf game -- assign roles and notify all players."

    if self.game_in_progress:
      self.say_public(\
        "A game is already in progress.  Use 'end game' to end it.")

    else:
      chname, chobj = self.channels.items()[0]
      users = chobj.users()
      users.remove(self._nickname)

      if len(users) < 5:
        self.say_public("Sorry, you need at least 5 players in the channel.")

      else:
        # Randomly select two wolves and a seer.  Everyone else is a villager.
        self._reset_gamedata()
        self.wolves.append(users.pop(random.randrange(len(users))))
        self.wolves.append(users.pop(random.randrange(len(users))))
        self.seer = users.pop(random.randrange(len(users)))
        for user in users:
          self.villagers.append(user)

        # Private message each user, tell them their role.
        # ### TODO.
        self.say_public("Wolves are " + `self.wolves`)
        self.say_public("Seer is " + `self.seer`)
        self.say_public("Villagers are " + `self.villagers`)
        
        self.say_public("A new game has begun!")
        self.say_public(new_game_text)
        self.game_in_progress = 1


  def end_game(self, e):
    "Quit a game in progress."

    if not self.game_in_progress:
      self.say_public(\
               "No game is in progress.  Use 'start game' to begin a game.")
    else:
      self.say_public("The game has ended.")
      self.game_in_progress = 0


  def do_command(self, e, cmd):
    "Parse CMD and if recognized, execute it."

    nick = nm_to_n(e.source())
    c = self.connection
    
    if cmd == "die":
      self.say_public("Ciao!")
      self.die()

    elif cmd == "start game":
      self.start_game(e)
          
    elif cmd == "end game":
      self.end_game(e)
                
    elif cmd == "stats":
      chname, chobj = self.channels.items()[0]
      users = chobj.users()
      
      self.say_public("There are " + `len(users)` + \
                      " players in this channel.")

    else:
      self.say_public("I don't understand.")



def main():
  
  if len(sys.argv) != 4:
    print "argv is ", sys.argv
    print "len is ", len(sys.argv)
    print "Usage: wolfbot.py <server[:port]> <channel> <nickname>"
    sys.exit(1)

  s = string.split(sys.argv[1], ":", 1)
  server = s[0]
  if len(s) == 2:
    try:
      port = int(s[1])
    except ValueError:
      print "Error: Erroneous port."
      sys.exit(1)
  else:
    port = 6667
  channel = sys.argv[2]
  nickname = sys.argv[3]

  bot = WolfBot(channel, nickname, server, port)
  bot.start()

if __name__ == "__main__":
  main()
