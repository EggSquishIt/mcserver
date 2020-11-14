import time
import persistent
import externals

usernames = {}
loaded = False
users = persistent.restore("users.json")
loaded = True

def user_has_data(userinfo):
  for key in userinfo:
    if key == "id" or key == "username":
      continue
    return True

  return False

# Function to store the user data
def saveconfig():
  global loaded

  if not loaded:
  	return

  users_copy = users.copy()

  todelete = []
  for id,userinfo in users_copy.items():
  	if not user_has_data(userinfo):
  	  todelete.append(id)
  	if "playing" in userinfo:
  	  del userinfo["playing"]

  for id in todelete:
  	del users_copy[id]

  persistent.store("users.json", users_copy)

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

def getuservalue(userinfo, key, default = 0):
  if key in userinfo:
    return userinfo[key]

  return default

def getuservalue_byname(username, key):
  return getuservalue(getuser_byname(username), key)

def setuservalue(userinfo, key, value):
  userinfo[key] = value
  saveconfig()

def setuservalue_byname(username, key, value):
  return setuservalue(getuser_byname(username), key, value)

def adduservalue(userinfo, key, delta):
  return setuservalue(userinfo, key, getuservalue(userinfo, key) + delta)

def adduservalue_byname(username, key, delta):
  return adduservalue(getuser_byname(username), key, delta)

def getuserstanding(userinfo):
  if "standing" in userinfo:
    return userinfo["standing"]

  # Temporary hack to allow twitch chatters to have much fun
  if getchattype(userinfo) == "twitch":
    return 10000

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

#[17:12:18] [Server thread/INFO]: Hexchild joined the game
#[17:12:35] [Server thread/INFO]: Hexchild left the game


####### run at startup #######

def user_join(match, entry, unused):
	username = match.group(1)
	userinfo = getuser_byname(username)
	userinfo["playing"] = True

def user_leave(match, entry, unused):
	username = match.group(1)
	userinfo = getuser_byname(username)
	if "playing" in userinfo:
		del userinfo["playing"]

externals.server_rlist = externals.server_rlist + [
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: (.*) joined the game",
    "handler": user_join,
  },
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: (.*) left the game",
    "handler": user_leave,
  }
]
