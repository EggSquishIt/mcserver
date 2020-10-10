
import time
import random
import externals
import users

# Positive value means happy, negative means angry
mood = 0

last_effects_timestamp = time.monotonic()
next_ominous = time.monotonic() + 60
next_checkup = time.monotonic() + 15

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
	if mood <= -100:
		return "hate"
	if mood >= 10:
		return "like"
	if mood <= -10:
		return "dislike"
	if mood >= 1:
		return "favor"
	if mood <= -1:
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

# Various effects to indicate player standing, etc.
def effects():
	global last_effects_timestamp
	global next_ominous
	global next_checkup
	global mood
	global previous_moodstring

	time_diff = time.monotonic() - last_effects_timestamp
	mood = mood * (0.99 ** time_diff)

	doing_checkup = False
	if time.monotonic() > next_checkup:
		next_checkup = time.monotonic() + 15
		externals.minecraft.send("time query daytime\r\n")
		doing_checkup = True
		externals.minecraft.say("Godmood value: " + str(mood))

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
		print(str(distance))
		externals.minecraft.send("execute at @r run summon lightning_bolt ~ ~" + str(distance) + " ~\r\n")

	last_effects_timestamp = time.monotonic()


def react(userinfo, opinion):
	global mood
	users.adduservalue(userinfo, "opinion", opinion)
	mood = mood + opinion

def react_byname(username, opinion):
	global mood
	users.adduservalue_byname(username, "opinion", opinion)
	mood = mood + opinion
