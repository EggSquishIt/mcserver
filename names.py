import random

vowels = [
	"a",
	"au",
	"o",
	"e",
	"i",
	"u",
]

prefixes = [
	"b",
	"c",
	"d",
	"f",
	"g",
	"gh",
	"h",
	"k",
	"l",
	"m",
	"n",
	"p",
	"qu",
	"r",
	"s",
	"t",
	"v",
	"w",
	"x",
	"y",
	"z"
]

suffixes = [
	"b",
	"c",
	"cc",
	"ck",
	"d",
	"dd",
	"f",
	"g",
	"gh",
	"h",
	"i",
	"k",
	"l",
	"ll",
	"m",
	"n",
	"p",
	"r",
	"rr",
	"s",
	"t",
	"tt",
	"v",
	"w",
	"x",
	"y",
	"z"
]

def generate_name():
	result = ""
	length = random.randint(3, 15)
	while len(result) < length:
		result = result + random.choice(prefixes) + random.choice(vowels) + random.choice(suffixes)
	return result

def proper_case(string):
	return string[:1].upper() + string[1:]
