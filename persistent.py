import json

def restore(filename):
	try:
		with open(filename, "r") as f:
			return json.loads(f.read())
	except:
		pass

	return {}

def store(filename, data):
  with open(filename, "w") as f:
    f.write(json.dumps(data, indent = 2) + "\n")
