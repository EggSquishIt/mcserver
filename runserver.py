
# Some modules we need to use
import subprocess
import sys
import re
import threading
import queue
import os
import json
import time

# A hack to remove the session lock from any previously running server instance
try:
  os.remove("world/session.lock")
except:
  pass

class SimpleProcess(threading.Thread):
  def __init__(self, cmdline):
    threading.Thread.__init__(self)
    self.queue = queue.Queue()
    self.program = subprocess.Popen(cmdline, shell = True, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
    self.start()

  def run(self):
    while True:
      line = self.program.stdout.readline().decode("utf-8")[:-1]
      self.queue.put(line)

  def getline(self):
    try:
      return self.queue.get(block = False)
    except:
      return ""

  def send(self, line):
    self.program.stdin.write(bytes(line, "utf-8"))
    self.program.stdin.flush()



class SimpleStdin(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.queue = queue.Queue()
    self.start()

  def run(self):
    while True:
      line = sys.stdin.readline()[:-1]
      self.queue.put(line)

  def getline(self):
    try:
      return self.queue.get(block = False)
    except:
      return ""


twitch = SimpleProcess("node twitch_chat.js")
minecraft = SimpleProcess("java -Xmx1024M -Xms1024M -jar server.jar nogui")
stdin = SimpleStdin()

# General userinfo structure:
#
# usernames = {
#   "Hexchild": "05a96b16-9845-44b7-8af9-6e9976d81035"
# }
#
# users = {
#   "05a96b16-9845-44b7-8af9-6e9976d81035": {
#     "username": "Hexchild",
#     "standing": "good",
#     "cash": "1000000000"
#   }
# }
#
usernames = {}
users = {}

try:
  with open("users.json", "r") as f:
    users = json.loads(f.read())
except:
  pass

# Function to store the python script's state
def saveconfig():
  with open("users.json", "w") as f:
    f.write(json.dumps(users, indent = 2) + "\n")

# Obtain the userinfo structure for a user based on their ID
def getuser_byuuid(uuid):
  if uuid not in users:
    users[uuid] = {}

  users[uuid]["id"] = uuid
  return users[uuid]

# Obtain the userinfo structure for a user based on their username
def getuser_byname(username):
  if username not in usernames:
    uuid = username
  else:
    uuid = usernames[username]

  userinfo = getuser_byuuid(uuid)

  # Hack to ensure that returnname is present in userinfo
  if "username" not in userinfo:
    userinfo["username"] = username

  return userinfo

# Return the correct ID for a user
def getuuid(userinfo):
  if "id" in userinfo:
    return userinfo["id"]

  return userinfo["username"]

def getuserstanding(userinfo):
  if "standing" in userinfo:
    return userinfo["standing"]

  #if getchattype(userinfo) == "twitch":
  #  return 10000

  return 0

def getuserstanding_byname(username):
  return getuserstanding(getuser_byname(username))


def reward(userinfo, rewardinfo):
  minecraft.send("say The gods are pleased with " + userinfo["username"] + "\r\n")
  minecraft.send("give " + userinfo["username"] + " iron_ingot 64\r\n")

def punish(userinfo, punishmentinfo):
  minecraft.send("say The gods are not happy with " + userinfo["username"] + "\r\n")

  if punishmentinfo["level"] >= 100:
    minecraft.send("execute as @e at @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:lightning_bolt {display:{color:#de0000}}\r\n")
    return

  if punishmentinfo["level"] >= 50:
    minecraft.send("execute at @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:lightning_bolt {display:{color:#de0000}}\r\n")
    return

  minecraft.send("execute as @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:creeper\r\n")

def check_permissions(userinfo, requirements):
  if "admin" in userinfo:
    return True

  if "minimum_standing" in requirements:
    if getuserstanding(userinfo) < requirements["minimum_standing"]:
      return False

  return True

def is_allowed(userinfo, requirements, reason):
  print("Permissions check for: " + str(userinfo))
  print("Requirements: " + str(requirements))
  print("Reason: " + str(reason))

  if not check_permissions(userinfo, requirements):
    print("Punishing " + userinfo["username"] + " for " + str(reason) + " without permission")
    punish(userinfo, {
      "reason": reason,
      "level": 1
    })
    return False

  return True

# Check the source type (minecraft player, server input or twitch) for a userinfo
def getchattype(userinfo):
  if getuuid(userinfo) == "server":
    return "server"

  if getuuid(userinfo).startswith("twitch:"):
    return "twitch"

  return "minecraft"

# Send message to server's text output
def server_message(msg):
  print(msg)

twitch_messages = []
# Send message to Twitch chat
def twitch_message(msg):
  global twitch_messages

  for line in msg.split("\n"):
    twitch_messages.append(line)

twitch_lastmsg = time.time()
# Do twitch chat throttling
def twitch_message_update():
  global twitch_messages
  global twitch_lastmsg

  if len(twitch_messages) == 0:
    return

  if len(twitch_messages) > 10:
    twitch_messages.pop(0)
    return

  now = time.time()
  if (now - twitch_lastmsg) < 2:
    return

  twitch_lastmsg = now

  msg = twitch_messages.pop(0)
  twitch.send("say EggSquishIt " + msg + "\n")

# Send message to Minecraft players
def minecraft_message(msg):
  # What to add before each line
  # prefix = "tell " + userinfo["username"] + " "
  prefix = "say "
  # What to add after each line
  suffix = "\r\n"
  # What to add between lines
  midfix = suffix + prefix
  minecraft.send(prefix + midfix.join(msg.split("\n")) + suffix)


# Send an abritrary message to the specified user
def message(userinfo, msg):
  chattype = getchattype(userinfo)

  if chattype == "server":
    server_message(msg)
    return

  if chattype == "twitch":
    twitch_message(msg)
    return

  if chattype == "minecraft":
    minecraft_message(msg)


def cmd_reward(userinfo, args):
  if is_allowed(userinfo, { "minimum_standing": 1 }, "Trying to reward " + args):
    reward(getuser_byname(args), {
      "reason": "Unspecified reason",
      "level": 1
    })

def cmd_punish(userinfo, args):
  if is_allowed(userinfo, { "minimum_standing": 100 }, "Trying to punish " + args):
    punish(getuser_byname(args), {
      "reason": "Unspecified reason",
      "level": 1
    })

def cmd_standing(userinfo, args):
  if args == "":
    targetname = userinfo["username"]
  else:
    targetname = args

  message(userinfo, "User " + targetname + " has standing " + str(getuserstanding_byname(targetname)) + "\r\n")

def cmd_save(userinfo, args):
  saveconfig()

def cmd_server(userinfo, args):
  if "admin" in userinfo and userinfo["admin"]:
    minecraft.send(args + "\r\n")

def cmd_say(userinfo, args):
  if is_allowed(userinfo, { "minimum_standing": 0 }, "Trying to make the server speak"):
    minecraft.send("say " + args + "\r\n")

def cmd_twitch_say(userinfo, args):
  if "admin" in userinfo and userinfo["admin"]:
    print("Saying message as twitch bot: " + args)
    twitch.send("say EggSquishIt " + args + "\n")

def cmd_gs(userinfo, args):
  if args == "":
    targetname = userinfo["username"]
  else:
    targetname = args

  if is_allowed(userinfo, { "minimum_standing": 100 }, "Trying to give glowstone to " + targetname):
    minecraft.send("give " + targetname + " glowstone\r\n")

def cmd_give(userinfo, args):
  if is_allowed(userinfo, { "minimum_standing": 100 }, "Trying to give " + args + " to " + targetname):
    match = re.search("^([^ ]*) (.*)$", args)
    if match:
      who = match.group(1)
      what = match.group(2)

      minecraft.send("give " + who + " " + what + "\r\n")

def cmd_help(userinfo, args):
  if args == "":
    message(userinfo, "Available commands:" + " ".join(cmds))
  else:
    message(userinfo, cmds[args]["help"])

cmds = {
  "standing": {
    "handler": cmd_standing,
    "help": """
!standing
!standing <player>
Respond with the current standing of yourself or a given player.
"""
  },
  "reward": {
    "handler": cmd_reward,
    "help": """
!reward <player>
Reward a player.
"""
  },
  "punish": {
    "handler": cmd_punish,
    "help": """
!punish <player>
Punish a player.
"""
  },
  "save": {
    "handler": cmd_save,
    "help": """
!save
Save the current script state.
"""
  },
  "server": {
    "handler": cmd_server,
    "help": """
!server <command>
Run an arbitrary server command.
"""  },
  "say": {
    "handler": cmd_say,
    "help": """
!say <message>
Have the server speak.
"""
  },
  "twitch_say": {
    "handler": cmd_twitch_say,
    "help": """
!twitch_say <message>
Have the twitch bot speak.
"""
  },
  "gs": {
    "handler": cmd_gs,
    "help": """
!gs
!gs <player>
Gives glowstone to you or another player.
"""
  },
  "give": {
    "handler": cmd_give,
    "help": """
!give <player> <item>
Gives an arbitrary item to another player.
"""
  },
  "help": {
    "handler": cmd_help,
    "help": """
!help
!help <command>
Provides a list of commands, or help on a specific command.
"""
  }
}


# Generic function to run commands (from main window, player chat or Twitch chat)
def runcmd(userinfo, cmd):
  print("Running command \"" + cmd + "\" by " + userinfo["username"])
  print("User info: " + str(userinfo))

  match = re.search("^([^ ]*) (.*)$", cmd)
  if match:
    cmd = match.group(1)
    args = match.group(2)
  else:
    args = ""

  try:
    cmds[cmd]["handler"](userinfo, args)
  except KeyError:
    pass


# Infinite loop
while True:

  ##################### Direct console command stuff ######################

  # Get one line from text window (stdin of python program)
  line = stdin.getline()

  # Check that line is not empty
  if line != "":
    print("Got cmdline from main window: " + line)
    runcmd(getuser_byname("server"), line)


  ##################### Twitch chat stuff ######################

  # Get a single line from the Twitch chat
  line = twitch.getline()

  # Check that line is not empty
  if line != "":
    print("Got chat line from twitch: " + line)

    # Extract twitch chat info
    match = re.search("^(.*): (.*)$", line)
    if match:
      # A chat message was received
      chatter = "twitch:" + match.group(1)
      chatmsg = match.group(2)

      minecraft.send("say <" + chatter + "> " + chatmsg + "\r\n")


  ##################### Server log stuff ######################

  # Get a single line from the Minecraft server
  line = minecraft.getline()

  # Check that line is not empty
  if line != "":
    print("Server: " + line)

    # Check if it's a chat message
    match = re.search("<(.*)> (.*)$", line)
    if match:
      # A chat message was received
      chatter = match.group(1)
      chatmsg = match.group(2)

      if chatmsg.startswith("!"):
        runcmd(getuser_byname(chatter), chatmsg[1:])

    # A mapping between player name and UUID
    match = re.search("^\\[[0-9:]*\\] \\[User Authenticator #[0-9]*/INFO\\]: UUID of player ([^ ]*) is ([0-9a-f-]*)$", line)
    if match:
      username = match.group(1)
      uuid = match.group(2)

      usernames[username] = uuid
      getuser_byname(username)

  # Make sure twitch messages that have been throttled get sent
  twitch_message_update()

# [15:31:59] [User Authenticator #1/INFO]: UUID of player Hexchild is 05a96b16-9845-44b7-8af9-6e9976d81035
