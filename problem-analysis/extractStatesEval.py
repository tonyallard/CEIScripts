#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the states evaluated from a log file.
import sys
import os
import re

HEURISTIC_STATE_DELIM = "Heuristic States Eval:"
STATE_DELIM = "#; States evaluated:"

def extractStatesEvaluatedByHeuristic(logFile):
	statesEvaluated = 0
	foundOnce = False
	for line in logFile:
		if HEURISTIC_STATE_DELIM in line:
			foundOnce = True
			states = re.findall(r'\d+', line)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			statesEvaluated += int(states[0])
	if not foundOnce:
		return -1
	return statesEvaluated

def extractStatesEvaluated(logFile):
	statesEvaluated = 0
	foundOnce = False
	for line in logFile:
		if STATE_DELIM in line:
			foundOnce = True
			states = re.findall(r'\d+', line)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			statesEvaluated += int(states[0])
	if not foundOnce:
		return -1
	return statesEvaluated

def extractAllStatesEvaluated(logFile):
	hStatesEvaluated = 0
	statesEvaluated = 0
	foundHOnce = False
	foundOnce = False
	for line in logFile:
		if STATE_DELIM in line:
			foundOnce = True
			states = re.findall(r'\d+', line)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			statesEvaluated += int(states[0])
		if HEURISTIC_STATE_DELIM in line:
			foundHOnce = True
			hStates = re.findall(r'\d+', line)
			if len(hStates) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%hStates)
			hStatesEvaluated += int(hStates[0])
	if not foundOnce:
		statesEvaluated = -1
	if not foundHOnce:
		hStatesEvaluated = -1
	return statesEvaluated, hStatesEvaluated, statesEvaluated+hStatesEvaluated

def main(args):
	csvFile = open('data.csv', 'w')
	path = "/mnt/data/logs/"
	for filename in os.listdir(path):
		f = open(path+filename, 'r')
		states, hStates, total = extractAllStatesEvaluated(f)
		csvFile.write("%s, %i, %i, %i\n"%(filename, states, hStates, total))
		print ("%s searched %i states and %i states in the heuristic (%i total)"%(filename, states, hStates, total))
	csv.close()
#Run Main Function
if __name__ == "__main__":
	main(sys.argv)