import users
import rewards
import externals

def check_permissions(userinfo, requirements):
	if "admin" in userinfo and userinfo["admin"]:
		return True

	if "allowed" in userinfo and not userinfo["allowed"]:
		return False

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

def get_permissions(entry):
	if entry["reason"] not in externals.settings["permissions"]:
		if "default_permissions" in entry:
			externals.settings["permissions"][entry["reason"]] = entry["default_permissions"]
		else:
			externals.settings["permissions"][entry["reason"]] = {}

	return externals.settings["permissions"][entry["reason"]]

def check_cmd(userinfo, entry):
	if "reason" not in entry:
		return True

	return is_allowed(userinfo, get_permissions(entry), entry["reason"])
