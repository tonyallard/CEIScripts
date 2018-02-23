#!/usr/bin/python
import sys
import os
import re

TIL = "\(at [0-9]+\.?[0-9]* \([a-zA-Z0-9\-_ \(\)]+\)"
MAYBE_DECIMAL_NUMBER = "[0-9]+\.?[0-9]*"
PREDICATE = "(\(( )*not( )*)?(\([a-zA-Z0-9\-_ ]+\))(( )*\))?"
#(\(( )*(not) ( )?)?
#( ( )?\))?

def bufferFile(file):
	fileBuffer = []
	for line in file:
		fileBuffer.append(line)
	return fileBuffer

def findTILs(problem):
	tils = []
	for line in problem:
		til = re.findall(TIL, line)
		if len(til) == 1:
			tils.append(til[0])
	return tils

def main(args):
	problemPath = args[0]
	newProblemPath = args[1]

	tighten_schedule = [0.9, 0.8, 0.7, 0.6, 0.5]

	for root, dirs, files in os.walk(problemPath):
		for file in files:
			if "DOMAIN" in file:
				continue
			f = open(os.path.join(root, file), 'r')
			buffer = bufferFile(f)
			
			for t in tighten_schedule:
				tightness = ("%.1f"%t).replace(".", "_")
				w = open(os.path.join(newProblemPath, file.replace(".PDDL", "-%s.PDDL"%tightness)), 'w')
				for line in buffer:
					til = re.findall(TIL, line)
					if len(til) == 1:
						val = re.findall(MAYBE_DECIMAL_NUMBER, til[0])
						precision = 0
						if "." in val[0]:
							precision = len(val[0].split(".")[1])
						
						val = float(val[0])
						pred = re.findall(PREDICATE, til[0])
						val *= t
						w.write("(at %0.*f %s)\n"%(precision, val, "".join(pred[0])))
					else:
						w.write(line)
				w.close()
		break





#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])