#!/usr/bin/python3

import json
import sys

with open(sys.argv[1], "r") as f:
	json.loads(f.read())
