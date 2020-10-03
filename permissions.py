import users
import rewards

def check_permissions(userinfo, requirements):
  if "admin" in userinfo:
    return True

  if "minimum_standing" in requirements:
    if users.getuserstanding(userinfo) < requirements["minimum_standing"]:
      return False

  return True

def is_allowed(userinfo, requirements, reason):
  print("Permissions check for: " + str(userinfo))
  print("Requirements: " + str(requirements))
  print("Reason: " + str(reason))

  if not check_permissions(userinfo, requirements):
    print("Punishing " + userinfo["username"] + " for " + str(reason) + " without permission")
    rewards.punish(userinfo, {
      "reason": reason,
      "level": 1
    })
    return False

  return True

