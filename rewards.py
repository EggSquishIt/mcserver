import externals

def reward(userinfo, rewardinfo):
  externals.minecraft.send("say The gods are pleased with " + userinfo["username"] + "\r\n")
  externals.minecraft.send("give " + userinfo["username"] + " iron_ingot 64\r\n")

def punish(userinfo, punishmentinfo):
  externals.minecraft.send("say The gods are not happy with " + userinfo["username"] + "\r\n")

  if punishmentinfo["level"] >= 100:
    externals.minecraft.send("execute as @e at @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:lightning_bolt {display:{color:#de0000}}\r\n")
    return

  if punishmentinfo["level"] >= 50:
    externals.minecraft.send("execute at @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:lightning_bolt {display:{color:#de0000}}\r\n")
    return

  externals.minecraft.send("execute as @e[name=\"" + userinfo["username"] + "\"] run summon minecraft:creeper\r\n")
