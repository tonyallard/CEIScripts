#! /usr/bin/python
#Author: Tony Allard
#Date: 23 Jan 2018
#Description: A script to check states files are the same

import sys
import re

def getInitState(state):
	fluents = []
	match = re.search(r"\(:init\s*([\(\)\w\-\s=])*\)", state)
	initState = match.group(0)
	
	matches = re.findall(r"(\([\w\-\s=\(]+\))", initState)
	for m in matches:
		m = re.sub(r"[\s]\)", ")", m)
		fluents.append(''.join(m.splitlines()))
	return fluents

def getGoalState(state):
	goalFluents = []
	match = re.search(r"\(:goal\s*([\(\)\w\-\s=])*\)", state)
	initState = match.group(0)
		
	matches = re.findall(r"(\([\w\-\s=]+\))", initState)
	for m in matches:
		m = re.sub(r"[\s]\)", ")", m)
		goalFluents.append(''.join(m.splitlines()))
	return goalFluents

def compareFluents(fluents1, fluents2, file1, file2):
	for fluent1 in fluents1:
		found = False
		for fluent2 in fluents2:
			if fluent1.lower() == fluent2.lower():
				found = True
				break
		if not found:
			print "%s in %s, does not have a partner in %s"%(fluent1, file1, file2)

def bufferFile(file):
	buffer = ""
	for line in file:
		buffer = buffer + line
	return buffer

def main(args):
	file1 = args[0]
	file2 = args[1]

	print file1, file2

	f1 = open(file1)
	f1Buf = bufferFile(f1)
	f1_fluents = getInitState(f1Buf)
	f1_goalFluents = getGoalState(f1Buf)

	f2 = open(file2)
	f2Buf = bufferFile(f2)
	f2_fluents = getInitState(f2Buf)
	f2_goalFluents = getGoalState(f2Buf)

	#compare fluents
	compareFluents(f1_fluents, f2_fluents, file1, file2)
	compareFluents(f2_fluents, f1_fluents, file2, file1)
	compareFluents(f1_goalFluents, f2_goalFluents, file1, file2)
	compareFluents(f2_goalFluents, f1_goalFluents, file2, file1)






#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])