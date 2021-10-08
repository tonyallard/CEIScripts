#!/usr/bin/python
import sys
import os
import re

CONNECTIVE = "\(= \(travel\-time V[0-3] L[0-9]{1,2} L[0-9]{1,2}\) [0-9]\)"
VEHICLE = "V[0-3]"
LOCATION = "L[0-9]{1,2}"

def bufferFile(file):
	fileBuffer = []
	for line in file:
		fileBuffer.append(line)
	return fileBuffer

def findConnectives(problem):
	connectives = []
	for line in problem:
		conn = re.findall(CONNECTIVE, line)
		if len(conn) == 1:
			connectives.append(conn[0])
	return connectives

def getPredicates(connectives):
	predicates = []
	for c in connectives:
		vehicle = re.findall(VEHICLE, c)
		locations = re.findall(LOCATION, c)
		predicates.append("(connected %s %s %s)"%(vehicle[0], locations[0], locations[1]))
	return predicates

def main(args):
	problemPath = args[0]
	newProblemPath = args[1]

	for root, dirs, files in os.walk(problemPath):
		for file in files:
			f = open(os.path.join(root, file), 'r')
			buffer = bufferFile(f)
			
			connectives = findConnectives(buffer)
			predicates = getPredicates(connectives)
			
			w = open(os.path.join(newProblemPath, file), 'w')
			predicatesDone = False
			for line in buffer:
				if not predicatesDone and len(re.findall(CONNECTIVE, line)) > 0:
					for pred in predicates:
						w.write("\t\t%s\n"%pred)
					predicatesDone = True
				w.write("%s"%line)
			w.close()

		break





#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])