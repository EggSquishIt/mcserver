import simpleprocess
import externals

mobs = [
	{
		"description": "a cow",
		"id": "minecraft:cow",
		"level": 20
	},
	{
		"description": "a creeper",
		"id": "minecraft:creeper",
		"level": -30
	},
	{
		"description": "a bat",
		"id": "minecraft:bat",
		"level": -1
	},
	{
		"description": "a zombie",
		"id": "minecraft:zombie",
		"level": -10
	},
	{
		"description": "a skeleton",
		"id": "minecraft:skeleton",
		"level": -40
	}
]

class Server(simpleprocess.SimpleProcess):
	def __init__(self, cmdline, cwd = "."):
		simpleprocess.SimpleProcess.__init__(self, cmdline, cwd)
		self.weather = "unknown"
		self.daytime = 0
		self.type = "java"

	def say(self, msg):
		msg = msg.replace("@", "\ufe6b")
		msg = msg.replace("\r", "")

		# Split multiline messages into one say command per line

		# What to add before each line
		# prefix = "tell " + userinfo["username"] + " "
		prefix = "say "
		# What to add after each line
		suffix = "\r\n"
		# What to add between lines
		midfix = suffix + prefix
		externals.minecraft.send(prefix + midfix.join(msg.split("\n")) + suffix)

	def set_weather(self, new_weather):
		if self.weather != new_weather:
			self.weather = new_weather
			self.send("weather " + new_weather + "\r\n")

	def summon(self, entity_type, position = None, options = None):
		print("Summoning entity type \"" + entity_type + "\" at " + str(position))
		if position is None:
			self.send("summon " + entity_type + "\r\n")
		else:
			self.send("summon " + entity_type + " " + position + "\r\n")

	def announcement(self, title, subtitle = None):
		if subtitle is not None:
			self.send("title @p subtitle {\"text\": \"" + subtitle + "\"}\r\n")
		self.send("title @p title {\"text\": \"" + title + "\"}\r\n")
