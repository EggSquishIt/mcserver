import re

def handle_rlist(string, rlist, context):
	matchcount = 0
	for entry in rlist:
		match = re.search(entry["regex"], string)
		if match:
			matchcount = matchcount + 1
			if entry["handler"](match, entry, context):
				break
	return matchcount
