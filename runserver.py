#!/usr/bin/python3

# Some modules we need to use
import os
import sys
import simpleprocess
import minecraft
import users
import rewards
import permissions
import regexhandling
import gods
import externals

externals.feature_id = "mc"
externals.feature_description = "Minecraft server"

if len(sys.argv) >= 2:
    externals.feature_id = sys.argv[1]

if len(sys.argv) >= 3:
    externals.feature_description = sys.argv[2]

# rlist to react to log lines from the Minecraft server
externals.server_rlist = []


# A hack to remove the session lock from any previously running server instance
try:
    os.remove("world/session.lock")
except FileNotFoundError:
    pass

externals.twitch = simpleprocess.SimpleProcess("node twitch_chat.js")
externals.minecraft = minecraft.Server("java \
                                       -Xmx1024M \
                                       -Xms1024M \
                                       -jar server.jar nogui", cwd="mc")
externals.stdin = simpleprocess.SimpleStdin()


# Function to store the python script's state


def saveconfig():
    users.saveconfig()


def cmd_wrong_params(match, entry, userinfo):
    users.message(userinfo, "Incorrect usage of command")
    return True  # No more processing from command list


def cmd_summon(match, entry, userinfo):
    entity_type = match.group(1)
    externals.minecraft.summon(entity_type)
    return True  # No more processing from command list


def cmd_summon_with_position(match, entry, userinfo):
    entity_type = match.group(1)
    position = match.group(2)
    externals.minecraft.summon(entity_type, position)
    return True  # No more processing from command list


def cmd_ominous(match, entry, userinfo):
    externals.minecraft.send("execute as @p run summon lightning_bolt ~ ~512 ~\r\n")
    return True  # No more processing from command list


def cmd_godmood_set(match, entry, userinfo):
    # if "admin" in userinfo and userinfo["admin"]:
    if permissions.is_allowed(userinfo, {"minimum_standing": 100}, "Trying to set godmood"):
        newmood = match.group(1)
        try:
            gods.mood = float(newmood)
        except Exception:
            pass

    return True  # No more processing from command list


def cmd_godmood_report(match, entry, userinfo):
    users.message(userinfo, "The gods are currently " + gods.describe_mood(gods.mood))
    return True  # No more processing from command list


def cmd_react(match, entry, userinfo):
    targetname = match.group(1)
    opinion = float(match.group(2))

    # if "admin" in userinfo and userinfo["admin"]:
    if permissions.is_allowed(userinfo, {"minimum_standing": 100}, "Trying to have gods react"):
        gods.react_byname(targetname, opinion)

    return True  # No more processing from command list


def cmd_opinion(match, entry, userinfo):
    users.message(userinfo, "The gods " + gods.describe_opinion(users.getuservalue(userinfo, "opinion")) + " you")
    return True  # No more processing from command list


def cmd_reward(match, entry, userinfo):
    targetname = match.group(1)
    if permissions.is_allowed(userinfo, {"minimum_standing": 1}, "Trying to reward " + targetname):
        rewards.reward(users.getuser_byname(targetname), {
            "reason": "Unspecified reason",
            "level": 1
        })
        return True  # No more processing from command list


def cmd_punish(match, entry, userinfo):
    targetname = match.group(1)
    if permissions.is_allowed(userinfo, {"minimum_standing": 100}, "Trying to punish " + targetname):
        rewards.punish(users.getuser_byname(targetname), {
            "reason": "Unspecified reason",
            "level": 1
        })
        return True  # No more processing from command list


def cmd_standing(match, entry, userinfo):
    if len(match.groups()) == 0:
        targetname = userinfo["username"]
    else:
        targetname = match.group(1)

    users.message(userinfo, "User " + targetname + " has standing " + str(users.getuserstanding_byname(targetname)) + "\r\n")
    return True  # No more processing from command list


def cmd_save(match, entry, userinfo):
    saveconfig()
    return True  # No more processing from command list


def cmd_server(match, entry, userinfo):
    if "admin" in userinfo and userinfo["admin"]:
        cmd = match.group(1)
        externals.minecraft.send(cmd + "\r\n")
        return True  # No more processing from command list


def cmd_announcement(match, entry, userinfo):
    if permissions.is_allowed(userinfo, {"minimum_standing": 100}, "Trying to make a title"):
        msg = match.group(1)
        externals.minecraft.announcement(msg)
        return True  # No more processing from command list


def cmd_say(match, entry, userinfo):
    if permissions.is_allowed(userinfo, {"minimum_standing": 0}, "Trying to make the server speak"):
        msg = match.group(1)
        externals.minecraft.say(msg)
        return True  # No more processing from command list


def cmd_twitch_say(match, entry, userinfo):
    if "admin" in userinfo and userinfo["admin"]:
        msg = match.group(1)
        externals.twitch.send("say EggSquishIt " + msg + "\n")
        return True  # No more processing from command list


def cmd_gs(match, entry, userinfo):
    print("Got " + str(len(match.groups())) + " groups.")
    if len(match.groups()) == 0:
        targetname = userinfo["username"]
    else:
        targetname = match.group(1)

    if permissions.is_allowed(userinfo, {"minimum_standing": 100}, "Trying to give glowstone to " + targetname):
        externals.minecraft.send("give " + targetname + " glowstone\r\n")

    return True  # No more processing from command list


def cmd_give(match, entry, userinfo):
    who = match.group(1)
    what = match.group(2)

    if not permissions.is_allowed(userinfo, {"minimum_standing": 100}, "Trying to give " + what + " to " + who):
        return True  # No more processing from command list

    externals.minecraft.send("give " + who + " " + what + "\r\n")
    return True  # No more processing from command list


def cmd_help(match, entry, userinfo):
    if len(match.groups()) == 0:
        users.message(userinfo, "Available commands: " + " ".join(help_map))
    else:
        cmd = match.group(1)
        if cmd in help_map:
            users.message(userinfo, help_map[cmd]["help"])
        else:
            users.message(userinfo, "Unknown command \"" + cmd + "\"")


def cmd_optout_arg(match, entry, userinfo):
    feature = match.group(1)
    if feature != externals.feature_id:
        return

    if "optin" in userinfo:
        del userinfo["optin"]
        saveconfig()
        users.message(userinfo, userinfo["username"] + ", you have now opted out of being part of the experiment.")


def cmd_optout_noarg(match, entry, userinfo):
    users.message(userinfo, userinfo["username"] + ", you can opt out of " + externals.feature_description + " by typing !optout " + externals.feature_id)


def runcmd(userinfo, cmd):
    print("Running command \"" + cmd + "\" by " + userinfo["username"])
    print("User info: " + str(userinfo))

    if regexhandling.handle_rlist(cmd, cmd_rlist, userinfo) == 0:
        users.message(userinfo, "Unknown command")


def twitchonly_optin_arg(match, entry, userinfo):
    feature = match.group(1)
    if feature != externals.feature_id:
        return

    userinfo["optin"] = True
    saveconfig()
    users.message(userinfo, userinfo["username"] + ", you have now opted in to being part of the experiment.")
    users.message(userinfo, "Your chat will now appear on the " + externals.feature_description + ".")
    users.message(userinfo, "You now have access to a bunch of commands. Try !help")
    users.message(userinfo, "You can opt out of this by typing !optout " + externals.feature_id)


def twitchonly_optin_noarg(match, entry, userinfo):
    users.message(userinfo, "Try \"!optin " + externals.feature_id + "\" to join the " + externals.feature_description)


def twitch_chat_message(match, entry, unused):
    # A chat message was received
    chatter = "twitch:" + match.group(1)
    chatmsg = match.group(2)

    userinfo = users.getuser_byname(chatter)

    if "optin" in userinfo and userinfo["optin"]:
        print("<" + chatter + "> " + chatmsg)

        if chatmsg.startswith("!"):
            runcmd(userinfo, chatmsg[1:])

        externals.minecraft.say("<" + chatter + "> " + chatmsg)

    else:
        regexhandling.handle_rlist(chatmsg, twitchonly_rlist, userinfo)


def server_chat_message(match, entry, unused):
    # A chat message was received
    chatter = match.group(1)
    chatmsg = match.group(2)
    print("<" + chatter + "> " + chatmsg)

    if chatmsg.startswith("!"):
        runcmd(users.getuser_byname(chatter), chatmsg[1:])


def server_uuid_map(match, entry, unused):
    username = match.group(1)
    uuid = match.group(2)

    users.setuuid_byname(username, uuid)
    users.getuser_byname(username)
    saveconfig()


cmd_rlist = []
help_map = {}

# summon command #


cmd_rlist = cmd_rlist + [
  {
    "regex": "^summon ([^ ]*)$",
    "handler": cmd_summon,
  },
  {
    "regex": "^summon ([^ ]*) (.*)$",
    "handler": cmd_summon_with_position,
  },
  {
    "regex": "^summon$",
    "handler": cmd_wrong_params,
  },
]

help_map["summon"] = {
  "help": """
!summon <entity_type>
!summon <entity_type> <position>
Summons an entity.
"""
}

# ominous command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^ominous$",
    "handler": cmd_ominous,
  },
]

help_map["ominous"] = {
  "help": """
!ominous
Just do it!
"""
}

# godmood command #


cmd_rlist = cmd_rlist + [
  {
    "regex": "^godmood (.*)$",
    "handler": cmd_godmood_set,
  },
  {
    "regex": "^godmood$",
    "handler": cmd_godmood_report,
  },
]

help_map["godmood"] = {
  "help": """
!godmood <number>
!godmood
Set or report the current mood of the gods.
"""
}

# react command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^react ([^ ]*) (.*)$",
    "handler": cmd_react,
  },
  {
    "regex": "^react$",
    "handler": cmd_wrong_params,
  },
  {
    "regex": "^react .*$",
    "handler": cmd_wrong_params,
  },
]

help_map["react"] = {
  "help": """
!react <player> <number>
Have the gods react positively or negatively to a player.
"""
}

# opinion command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^opinion$",
    "handler": cmd_opinion,
  },
  {
    "regex": "^opinion .*$",
    "handler": cmd_wrong_params,
  },
]

help_map["opinion"] = {
  "help": """
!opinion
Report how the gods feel about you.
"""
}

# reward command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^reward (.*)$",
    "handler": cmd_reward,
  },
  {
    "regex": "^reward$",
    "handler": cmd_wrong_params,
  },
]

help_map["reward"] = {
  "help": """
!reward <player>
Reward a player.
"""
}

# punish com #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^punish (.*)$",
    "handler": cmd_punish,
  },
  {
    "regex": "^punish$",
    "handler": cmd_wrong_params,
  },
]

help_map["punish"] = {
  "help": """
!punish <player>
Punish a player.
"""
}

# standing command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^standing (.*)$",
    "handler": cmd_standing,
  },
  {
    "regex": "^standing$",
    "handler": cmd_standing,
  },
]

help_map["standing"] = {
  "help": """
!standing
!standing <player>
Respond with the current standing of yourself or a given player.
"""
}

# save command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^save$",
    "handler": cmd_save,
  },
  {
    "regex": "^save ",
    "handler": cmd_wrong_params,
  },
]

help_map["save"] = {
  "help": """
!save
Save the current script state.
"""
}

# server command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^server (.*)$",
    "handler": cmd_server,
  },
  {
    "regex": "^server$",
    "handler": cmd_wrong_params,
  },
]

help_map["server"] = {
  "help": """
#!server <command>
#Run an arbitrary server command.
#"""
}

# announcement command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^announcement (.*)$",
    "handler": cmd_announcement,
  },
  {
    "regex": "^announcement$",
    "handler": cmd_wrong_params,
  },
]

help_map["announcement"] = {
  "help": """
!announcement <message>
Show a title (and possible subtitle) to all players.
"""
}

# say command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^say (.*)$",
    "handler": cmd_say,
  },
  {
    "regex": "^say$",
    "handler": cmd_wrong_params,
  },
]

help_map["say"] = {
  "help": """
!say <message>
Have the server speak.
"""
}

# twitch_say command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^twitch_say (.*)$",
    "handler": cmd_twitch_say,
  },
  {
    "regex": "^twitch_say$",
    "handler": cmd_wrong_params,
  },
]

help_map["twitch_say"] = {
  "help": """
!twitch_say <message>
Have the twitch bot speak.
"""
}

# gs command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^gs$",
    "handler": cmd_gs,
  },
  {
    "regex": "^gs (.*)$",
    "handler": cmd_gs,
  },
]

help_map["gs"] = {
  "help": """
!gs
!gs <player>
Gives glowstone to you or another player.
"""
}

# give command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^give ([^ ]+) (.*)$",
    "handler": cmd_give,
  },
  {
    "regex": "^give($| )",
    "handler": cmd_wrong_params,
  },
]

help_map["give"] = {
  "help": """
!give <player> <item>
Gives an arbitrary item to another player.
"""
}

# help command #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^help (.*)$",
    "handler": cmd_help,
  },
  {
    "regex": "^help$",
    "handler": cmd_help,
  },
]

help_map["help"] = {
  "help": """
!help
!help <command>
Provides a list of commands, or help on a specific command.
"""
}

# twitch chat but not opted in #

cmd_rlist = cmd_rlist + [
  {
    "regex": "^optout (.*)$",
    "handler": cmd_optout_arg,
  },
  {
    "regex": "^optout$",
    "handler": cmd_optout_noarg,
  }
]

###################################


twitchonly_rlist = []

# twitch chat but not opted in #

twitchonly_rlist = twitchonly_rlist + [
  {
    "regex": "^!optin (.*)$",
    "handler": twitchonly_optin_arg,
  },
  {
    "regex": "^!optin$",
    "handler": twitchonly_optin_noarg,
  }
]

###################################


twitch_rlist = []

# twitch chat #

twitch_rlist = twitch_rlist + [
  {
    "regex": "^<([^>]+)> (.*)$",
    "handler": twitch_chat_message,
  }
]

###################################


# player chat #

externals.server_rlist = externals.server_rlist + [
  {
    "regex": "^\\[[0-9:]*\\] \\[Server thread/INFO\\]: <([^>]+)> (.*)$",
    "handler": server_chat_message,
  }
]

# map between between player name and UUID #

externals.server_rlist = externals.server_rlist + [
  {
    "regex": "^\\[[0-9:]*\\] \\[User Authenticator #[0-9]*/INFO\\]: UUID of player ([^ ]*) is ([0-9a-f-]*)$",
    "handler": server_uuid_map,
  }
]

###################################

# Infinite loop
while True:

    # Direct console command stuff #

    # Get one line from text window (stdin of python program)
    line = externals.stdin.getline()

    # Check that line is not empty
    if line != "":
        print("Got cmdline from main window: " + line)
        runcmd(users.getuser_byname("server"), line)

    # Twitch chat stuff #

    # Get a single line from the Twitch chat
    line = externals.twitch.getline()

    # Get a single line from the Twitch chat
    line = externals.twitch.getline()

    # Check that line is not empty
    if line != "":
        regexhandling.handle_rlist(line, twitch_rlist, None)

    # Server log stuff #

    # Get a single line from the Minecraft server
    line = externals.minecraft.getline()

    # Check that line is not empty
    if line != "":
        if regexhandling.handle_rlist(line, externals.server_rlist, None) == 0:
            print("Server: " + line)

        # Make sure twitch messages that have been throttled get sent
        users.twitch_message_update()

    gods.effects()
