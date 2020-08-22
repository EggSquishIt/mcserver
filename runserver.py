
# Some modules we need to use
import subprocess
import sys
import re
import threading
import queue
import os
import json

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
  return users[uuid]

# Obtain the userinfo structure for a user based on their username
def getuser_byname(username):
  if username not in usernames:
    userinfo = getuser_byuuid(username)
  else:
    userinfo = getuser_byuuid(usernames[username])

  # Hack to ensure that returnname is present in userinfo
  if "username" not in userinfo:
    userinfo["username"] = username
  return userinfo

def getuserstanding(userinfo):
  if "standing" in userinfo:
    return userinfo["standing"]

  return 0

def getuserstanding_byname(username):
  return getuserstanding(getuser_byname(username))


def reward(userinfo, rewardinfo):
  minecraft.send("say Thank you, " + userinfo["username"] + "\r\n")
  minecraft.send("give " + userinfo["username"] + " iron_ingot 64\r\n")

def punish(userinfo, punishmentinfo):
  minecraft.send("say That's not very nice, " + userinfo["username"] + "\r\n")
  #minecraft.send("execute as @e at @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:lightning_bolt\r\n")
  #minecraft.send("execute as @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:lightning_bolt {display:{color:#de0000}}\r\n")
  #minecraft.send("execute as @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:creeper\r\n")

def is_allowed(userinfo, requirements, reason):
  print("Permissions check for: " + str(userinfo))
  print("Requirements: " + str(requirements))
  print("Reason: " + str(reason))

  if "minimum_standing" in requirements:
    if getuserstanding(userinfo) >= requirements["minimum_standing"]:
      return True

  punish(userinfo, {
    "reason": reason,
    "level": 1
  })
  return False

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

  minecraft.send("say User " + targetname + " has standing " + str(getuserstanding_byname(targetname)) + "\r\n")

def cmd_save(userinfo, args):
  saveconfig()

def cmd_server(userinfo, args):
  if "admin" in userinfo and userinfo["admin"]:
    minecraft.send(args + "\r\n")

def cmd_say(userinfo, args):
  minecraft.send("say " + args + "\r\n")

def cmd_gs(userinfo, args):
  if args == "":
    targetname = userinfo["username"]
  else:
    targetname = args

  if is_allowed(userinfo, { "minimum_standing": 100 }, "Trying to give glowstone to " + targetname):
    minecraft.send("give " + targetname + " glowstone\r\n")

def cmd_give(userinfo, args):
  match = re.search("^([^ ]*) (.*)$", args)
  if match:
    who = match.group(1)
    what = match.group(2)

    minecraft.send("give " + who + " " + what + "\r\n")


cmds = {
  "standing": {
    "handler": cmd_standing
  },
  "reward": {
    "handler": cmd_reward
  },
  "punish": {
    "handler": cmd_punish
  },
  "save": {
    "handler": cmd_save
  },
  "server": {
    "handler": cmd_server
  },
  "say": {
    "handler": cmd_say
  },
  "gs": {
    "handler": cmd_gs
  },
  "give": {
    "handler": cmd_give
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

# [15:31:59] [User Authenticator #1/INFO]: UUID of player Hexchild is 05a96b16-9845-44b7-8af9-6e9976d81035
