
import externals

objectives = {}

def list_action_none(old_objectives):
	print("Current scoreboard objectives: " + str(old_objectives))

def list_action_update(old_objectives):
	global list_action
	global objectives
	list_action = list_action_none

	#retained_objectives = []
	for objective in old_objectives:
		#if objective in objectives:
		#	print("NOT removing objective: " + str(objective))
		#	retained_objectives.append(objective)
		#else:
		print("Removing objective: " + str(objective))
		externals.minecraft.send("scoreboard objectives remove " + objective + "\r\n")

	for objective,specification in objectives.items():
		#if objective not in retained_objectives:
		print("Add objective: " + str(objective) + " containing " + str(specification))
		externals.minecraft.send("scoreboard objectives add " + objective + " " + specification + "\r\n")

list_action = list_action_none

def server_objectives_list(match, entry, unused):
	list_action([s[1:-1] for s in match.group(2).split(", ")])

def server_objectives_list_empty(match, entry, unused):
	list_action([])

externals.server_rlist = externals.server_rlist + [
	{
		"regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: There are no objectives$",
		"handler": server_objectives_list_empty,
	},
	{
		"regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: There are ([0-9]+) objectives: (.*)$",
		"handler": server_objectives_list,
	}
]

def update_objectives():
	global list_action
	list_action = list_action_update
	externals.minecraft.send("scoreboard objectives list\r\n")

# [17:14:14] [Server thread/INFO]: There are no objectives
# [17:15:00] [Server thread/INFO]: There are 2 objectives: [zombiesKilled], [chickensKilled]

# server scoreboard objectives list

# server scoreboard objectives add zombiesKilled minecraft.killed:minecraft.zombie
# server scoreboard objectives remove zombiesKilled
# server scoreboard players get @p zombiesKilled
# server scoreboard players set Hexchild zombiesKilled 0

# server scoreboard objectives add chickensKilled minecraft.killed:minecraft.chicken
# server scoreboard players get @p chickensKilled


#Server: [17:28:28] [Server thread/INFO]: There are 2 objectives: [zombiesKilled], [chickensKilled]
#'[zombiesKilled], [chickensKilled]'
#['[zombiesKilled]', '[chickensKilled]']
#['zombiesKilled', 'chickensKilled']
