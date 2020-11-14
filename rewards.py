import externals
import minecraft
import random

awards = [
  # {
  #   "description": "spawn a cow",
  #   "handler": spawn_mob,
  #   "id": "minecraft:cow",
  #   "level": 20
  # },
  # {
  #   "description": "spawn a creeper",
  #   "handler": spawn_mob,
  #   "id": "minecraft:creeper",
  #   "level": -30
  # },
  # {
  #   "description": "spawn a bat",
  #   "handler": spawn_mob,
  #   "id": "minecraft:bat",
  #   "level": -1
  # },
  # {
  #   "description": "spawn a zombie",
  #   "handler": spawn_mob,
  #   "id": "minecraft:zombie",
  #   "level": -10
  # },
  # {
  #   "description": "spawn a skeleton",
  #   "handler": spawn_mob,
  #   "id": "minecraft:skeleton",
  #   "level": -40
  # },
  # {
  #   "description": "strike with a lightning bolt",
  #   "handler": summon_lightning,
  #   "level": -50
  # },
  # {
  #   "description": "give 64 iron ingots",
  #   "handler": give_item,
  #   "id": "minecraft:iron_ingot",
  #   "amount": 64,
  #   "level": 50
  # },
  # {
  #   "description": "give a stone sword",
  #   "handler": give_item,
  #   "id": "minecraft:stone_sword",
  #   "amount": 1,
  #   "level": 10
  # },
  # {
  #   "description": "give a stick",
  #   "handler": give_item,
  #   "id": "minecraft:stick",
  #   "amount": 1,
  #   "level": 1
  # }
]

def reward(userinfo, rewardinfo):
  award(userinfo, rewardinfo)

def punish(userinfo, punishmentinfo):
  punishmentinfo["level"] = -punishmentinfo["level"]
  award(userinfo, punishmentinfo)

def award(userinfo, awardinfo):
  # How much reward or punishment to dole out
  remaining_level = awardinfo["level"]

  if remaining_level > 0:
    externals.minecraft.send("say The gods are pleased with " + userinfo["username"] + "\r\n")
  elif remaining_level < 0:
    externals.minecraft.send("say The gods are not happy with " + userinfo["username"] + "\r\n")

  while remaining_level != 0:

    # Get a list of possible awards
    if remaining_level > 0:
      applicable_awards = [ award for award in awards if award["level"] > 0 and award["level"] <= remaining_level and random.randint(0, 100) <= award["occurrence"] ]
    else:
      applicable_awards = [ award for award in awards if award["level"] < 0 and award["level"] >= remaining_level and random.randint(0, 100) <= award["occurrence"] ]

    # If list is empty, we need a different solution
    if len(applicable_awards) == 0:
      break

    # Pick an award and apply it, then "use up" that much of the punishment
    award = random.choice(applicable_awards)
    remaining_level = remaining_level - award["handler"](userinfo, award, remaining_level)
