ARG_VOCAB = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

REQUIREMENTS = [
	":strips", 					#0
	":equality",				#1
	":typing",					#2
	":fluents",					#3
	":durative-actions",		#4
	":timed-initial-literals"	#5
	]


POLARITY = ["NEG", "POS"]
NEG = POLARITY[0]
POS = POLARITY[1]

TIME_SPEC = ["AT START", "AT END", "OVER ALL", "AT"]
AT_START = TIME_SPEC[0]
AT_END = TIME_SPEC[1]
OVER_ALL = TIME_SPEC[2]
AT = TIME_SPEC[3]

OPTIMIZATION = ["minimize", "maximize"]
MINIMIZE = OPTIMIZATION[0]
MAXIMIZE = OPTIMIZATION[1]