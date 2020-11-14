
import time
import random
import externals
import users
import mc_objectives
import random
import hashlib
import rewards

# Positive value means happy, negative means angry
mood = 0

objective_criteria = {
	"teamkill.": {
		"description": "kill player in",
		"target_type": "team"
	},
	"killedByTeam.": {
		"description": "get killed by player in",
		"target_type": "team"
	},
	"minecraft.picked_up:": {
		"description": "pick up",
		"target_type": "item"
	},
	"minecraft.dropped:": {
		"description": "drop",
		"target_type": "item"
	},
	"minecraft.used:": {
		"description": "use",
		"target_type": "item"
	},
	"minecraft.broken:": {
		"description": "break",
		"target_type": "item"
	},
	"minecraft.crafted:": {
		"description": "craft",
		"target_type": "item"
	},
	"minecraft.mined:": {
		"description": "mine",
		"target_type": "block"
	},
	"minecraft.killed:": {
		"description": "kill",
		"target_type": "entity"
	},
	"minecraft.killed_by:": {
		"description": "get killed by",
		"target_type": "entity"
	}
}

objective_targets = {
	"team": [
		{
			"description": "team Red",
			"id": "red",
			"level": 0
		},
		{
			"description": "team Blue",
			"id": "blue",
			"level": 0
		}
	],
	"item": [
		{
			"description": "a stone sword",
			"id": "minecraft.stone_sword",
			"level": 20,
			"occurrence": 80
		},
		{
			"description": "a glowstone",
			"id": "minecraft.glowstone",
			"level": 30,
			"occurrence": 10
		}
	],
	"block": [
		{
			"description": "a stone block",
			"id": "minecraft.stone",
			"level": 5,
			"occurrence": 100
		},
		{
			"description": "a dirt block",
			"id": "minecraft.dirt",
			"level": 5,
			"occurrence": 100
		},
		{
			"description": "a grass block",
			"id": "minecraft.grass",
			"level": 20,
			"occurrence": 1
		}
	],
	"entity": [
		{
			"description": "a chicken",
			"id": "minecraft.chicken",
			"level": 5,
			"occurrence": 60
		},
		{
			"description": "a zombie",
			"id": "minecraft.zombie",
			"level": -10,
			"occurrence": 100
		},
		{
			"description": "a cow",
			"id": "minecraft.cow",
			"level": 20,
			"occurrence": 60
		},
		{
			"description": "a skeleton",
			"id": "minecraft.skeleton",
			"level": -50,
			"occurrence": 100
		},
		{
			"description": "an enderman",
			"id": "minecraft.enderman",
			"level": -5,
			"occurrence": 40
		},
		{
			"description": "a pig",
			"id": "minecraft.pig",
			"level": 10,
			"occurrence": 60
		},
		{
			"description": "a sheep",
			"id": "minecraft.sheep",
			"level": 20,
			"occurrence": 60
		},
		{
			"description": "a squid",
			"id": "minecraft.squid",
			"level": 1,
			"occurrence": 10
		},
		{
			"description": "a bat",
			"id": "minecraft.bat",
			"level": 1,
			"occurrence": 50
		}
	]
}

world_actions = {
}

def spawn_mob(userinfo, award, remaining_level):
  externals.minecraft.send("execute at " + userinfo["username"] + " run summon " + award["id"] + "\r\n")
  return award["level"]

def summon_lightning(userinfo, award, remaining_level):
  externals.minecraft.send("execute at " + userinfo["username"] + " run summon minecraft:lightning_bolt ~ ~ ~ {display:{color:red}}\r\n")
  return award["level"]

def give_item(userinfo, award, remaining_level):
  externals.minecraft.send("give " + userinfo["username"] + " " + award["id"] + " " + str(award["amount"]) + "\r\n")
  return award["level"]

def randomize_awards():
	rewards.awards.append({
		"description": "strike with a lightning bolt",
		"handler": summon_lightning,
		"level": -50,
		"occurrence": 100,
	})
	for entity in objective_targets["entity"]:
		rewards.awards.append({
			"description": "spawn " + entity["description"],
			"handler": spawn_mob,
			"id": entity["id"].replace(".", ":"),
			"level": entity["level"],
			"occurrence": entity["occurrence"]
		})
	for entity in objective_targets["item"]:
		rewards.awards.append({
			"description": "give " + entity["description"],
			"handler": give_item,
			"id": entity["id"].replace(".", ":"),
			"amount": 1,
			"level": entity["level"],
			"occurrence": entity["occurrence"]
		})
	for entity in objective_targets["block"]:
		rewards.awards.append({
			"description": "give " + entity["description"],
			"handler": give_item,
			"id": entity["id"].replace(".", ":"),
			"amount": 1,
			"level": entity["level"],
			"occurrence": entity["occurrence"]
		})

def list_world_actions(userinfo):
	for world_action_id,world_action in world_actions.items():
		users.message(userinfo, "God opinion on \"" + world_action["description"] + "\": " + str(world_action["opinion"]))

def update_world_actions():
	global world_actions

	for world_action_id,world_action in world_actions.items():
		mc_objectives.objectives["gods_" + world_action_id] = world_action["trigger"]

	to_delete = []
	for objective in mc_objectives.objectives:
		if not objective.startswith("gods_"):
			continue
		world_action_id = objective[5:]

		if world_action_id not in world_actions:
			to_delete.append(objective)

	for objective in to_delete:
		del mc_objectives.objectives[objective]

	mc_objectives.update_objectives()

def randomize_world_actions():
	global world_actions

	world_actions = {}
	hashes_used = []
	while len(hashes_used) < externals.settings["number_of_world_actions"]:
		criterium = random.choice(list(objective_criteria.keys()))
		criterium_description = objective_criteria[criterium]["description"]
		target_type = objective_criteria[criterium]["target_type"]
		target = random.choice(objective_targets[target_type])
		target_id = target["id"]
		target_description = target["description"]
		trigger = criterium + target_id
		trigger_description = criterium_description + " " + target_description
		hash = hashlib.md5(bytes(trigger, "utf-8")).hexdigest()[:10]
		if hash in hashes_used:
			continue
		hashes_used.append(hash)
		world_actions[hash] = {
			"trigger": trigger,
			"description": trigger_description,
			"opinion": random.randrange(1, 25) * random.randrange(-1, 3, 2)
		}

	update_world_actions()

def generate_pantheon():
	randomize_awards()
	randomize_world_actions()

last_effects_timestamp = time.monotonic()
next_ominous = time.monotonic() + 60
next_checkup = time.monotonic() + 15
next_award = time.monotonic() + 300 / externals.settings["timescale"]

previous_moodstring = "unknown"

def describe_mood(mood):
	if mood >= 500:
		return "in nirvana"
	if mood <= -500:
		return "incandescent"
	if mood >= 100:
		return "ecstatic"
	if mood <= -100:
		return "furious"
	if mood >= 15:
		return "happy"
	if mood <= -15:
		return "angry"
	if mood >= 2:
		return "pleased"
	if mood <= -2:
		return "annoyed"
	return "nonplussed"

def describe_opinion(opinion):
	if opinion >= 100:
		return "love"
	if opinion <= -100:
		return "hate"
	if opinion >= 10:
		return "like"
	if opinion <= -10:
		return "dislike"
	if opinion >= 1:
		return "favor"
	if opinion <= -1:
		return "disvafor"
	return "ignore"

# entity.ghast.scream
moodinfo = {
	"in nirvana": {
		"announce_sound": "ui.toast.challenge_complete",
		"announce_color": "green",
	},
	"ecstatic": {
		"announce_sound": "ui.toast.challenge_complete",
		"announce_color": "green",
	},
	"happy": {
		"announce_sound": "entity.villager.ambient",
		"announce_color": "green",
	},
	"pleased": {
		"announce_sound": "entity.evoker.celebrate",
		"announce_color": "green",
	},
	"nonplussed": {
		"announce_sound": "entity.donkey.angry",
		"announce_color": "gray",
	},
	"annoyed": {
		"announce_sound": "entity.horse.death",
		"announce_color": "red",
	},
	"angry": {
		"announce_sound": "entity.wither.spawn",
		"announce_color": "red",
	},
	"furious": {
		"announce_sound": "item.totem.use",
		"announce_color": "red",
	},
	"incandescent": {
		"announce_sound": "item.totem.use",
		"announce_color": "red",
	},
}

def effects_happyside():
	global next_ominous
	#print("happyside effects")
	externals.minecraft.set_weather("clear")
	next_ominous = time.monotonic() + 10

def effects_neutral():
	global next_ominous
	#print("neutral effects")
	next_ominous = time.monotonic() + 10
	pass

def effects_angryside():
	#print("angryside effects")
	pass

def restrict_daytime(lower, upper):
	if externals.minecraft.daytime > upper or externals.minecraft.daytime < lower:
		externals.minecraft.daytime = lower
		externals.minecraft.send("time set " + str(lower) + "\r\n")

####### current time of day #######

def server_the_time_is(match, entry, unused):
  externals.minecraft.daytime = int(match.group(1))

externals.server_rlist = externals.server_rlist + [
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: The time is ([0-9]+)$",
    "handler": server_the_time_is,
  }
]

####### keep track of player scores #######

def set_score(username, objective, score):
	global world_actions

	if not objective.startswith("gods_"):
		return
	world_action_id = objective[5:]

	if world_action_id not in world_actions:
		return

	world_action = world_actions[world_action_id]

	userinfo = users.getuser_byname(username)

	if "objectives" not in userinfo:
		userinfo["objectives"] = {}

	userinfo["objectives"][objective] = score
	print("Current " + objective + " score for " + username + ": " + str(score))

def server_player_score(match, entry, unused):
	username = match.group(1)
	score = int(match.group(2))
	objective = match.group(3)

	set_score(username, objective, score)

def server_player_score_notset(match, entry, unused):
	objective = match.group(1)
	username = match.group(2)

	set_score(username, objective, 0)

externals.server_rlist = externals.server_rlist + [
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: (.*) has ([0-9]+) \\[([^[]+)\\]$",
    "handler": server_player_score,
  },
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: Can't get value of ([^[]+) for (.*); none is set$",
    "handler": server_player_score_notset,
  }
]

####### run at startup #######

def server_startup(match, entry, unused):
	global world_actions

	generate_pantheon()

	print("Server has started")

externals.server_rlist = externals.server_rlist + [
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: Done ",
    "handler": server_startup,
  }
]


# Various effects to indicate player standing, etc.
def effects():
	global last_effects_timestamp
	global next_ominous
	global next_checkup
	global next_award
	global mood
	global previous_moodstring
	global world_actions

	time_diff = time.monotonic() - last_effects_timestamp
	mood = mood * (0.99 ** time_diff)

	doing_checkup = False
	if time.monotonic() > next_checkup:
		next_checkup = time.monotonic() + 15
		externals.minecraft.send("time query daytime\r\n")
		for world_action_id,world_action in world_actions.items():
			objective = "gods_" + world_action_id
			externals.minecraft.send("scoreboard players get @p " + objective + "\r\n")
		doing_checkup = True

	if time.monotonic() > next_award:
		next_award = time.monotonic() + random.randint(120, 600) / externals.settings["timescale"]
		playing_users = { id: userinfo for id, userinfo in users.users.items() if "playing" in userinfo and userinfo["playing"] }
		if len(playing_users):
			userinfo = users.users[random.choice(list(playing_users.keys()))]
			print("Award will go to: " + str(userinfo))
			if "opinion" in userinfo:
				level = users.getuservalue(userinfo, "opinion")
				rewards.award(userinfo, {
					"reason": "Just awards from the gods",
					"level": level
				})
				users.adduservalue(userinfo, "opinion", level / -2)

	moodstring = describe_mood(mood)
	if moodstring != previous_moodstring:
		previous_moodstring = moodstring
		externals.minecraft.announcement("Gods are " + moodstring + "!")
		externals.minecraft.send("execute at @p run playsound " + moodinfo[moodstring]["announce_sound"] + " ambient @p[" + ("limit" if externals.minecraft.type == "java" else "c") + "=1]\r\n")

	if moodstring == "in nirvana":
		effects_happyside()
		restrict_daytime(2000, 10000) # Force eternal daytime
	elif moodstring == "ecstatic":
		effects_happyside()
		restrict_daytime(2000, 10000) # Force eternal daytime
	elif moodstring == "pleased":
		effects_happyside()
	elif moodstring == "happy":
		effects_happyside()
	elif moodstring == "nonplussed":
		effects_neutral()
	elif moodstring == "annoyed":
		effects_angryside()
		externals.minecraft.set_weather("rain")
	elif moodstring == "angry":
		effects_angryside()
		externals.minecraft.set_weather("thunder")
	elif moodstring == "furious":
		effects_angryside()
		externals.minecraft.set_weather("thunder")
		restrict_daytime(14000, 22000) # Force eternal nighttime
	elif moodstring == "incandescent":
		effects_angryside()
		externals.minecraft.set_weather("thunder")
		restrict_daytime(14000, 22000) # Force eternal nighttime
		if doing_checkup:
			externals.minecraft.send("execute at @r run summon phantom ~ ~50 ~\r\n")

	# Automatically do ominous lightning
	if time.monotonic() > next_ominous:
		next_ominous = time.monotonic() + random.randrange(30, 100) / 10
		distance = mood + 500
		distance = distance + random.randint(0, 50)
		if distance < 0:
			distance = 0
		elif distance > 768:
			distance = 768
		externals.minecraft.send("execute at @r run summon lightning_bolt ~ ~" + str(distance) + " ~\r\n")

	for id,userinfo in users.users.items():
		if "objectives" not in userinfo:
			continue

		user_objectives = userinfo["objectives"]

		for world_action_id,world_action in world_actions.items():
			objective = "gods_" + world_action_id
			if objective not in user_objectives:
				continue

			score = user_objectives[objective]
			if score == 0:
				continue

			externals.minecraft.send("scoreboard players set " + userinfo["username"] + " " + objective + " 0\r\n")

			print(userinfo["username"] + " has score " + str(score) + " on " + objective + " (" + world_action["description"] + ")")
			react(userinfo, world_action["opinion"] * score * 0.1 * externals.settings["moodscale"])

			user_objectives[objective] = 0
			users.saveconfig()

	last_effects_timestamp = time.monotonic()


def react(userinfo, opinion):
	global mood
	print("Reacting to " + userinfo["username"] + " with " + str(opinion))
	users.adduservalue(userinfo, "opinion", opinion)
	mood = mood + opinion

def react_byname(username, opinion):
	global mood
	print("Reacting to " + username + " with " + str(opinion))
	users.adduservalue_byname(username, "opinion", opinion)
	mood = mood + opinion
