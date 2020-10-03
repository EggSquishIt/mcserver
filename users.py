import time
import json
import externals

usernames = {}
users = {}

try:
  with open("users.json", "r") as f:
    users = json.loads(f.read())
except:
  pass

# Function to store the user data
def saveconfig():
  with open("users.json", "w") as f:
    f.write(json.dumps(users, indent = 2) + "\n")

def setuuid_byname(username, uuid):
  usernames[username] = uuid

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
  externals.twitch.send("say EggSquishIt " + msg + "\n")

# Send message to Minecraft players
def minecraft_message(msg):
  externals.minecraft.say(msg)


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
