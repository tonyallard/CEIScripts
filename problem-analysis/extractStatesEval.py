#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the states evaluated from a log file.
#Extracts states evaluated to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import re

HEURISTIC_STATE_DELIM = "Heuristic States Eval:"
STATE_DELIM = "#; States evaluated:"

def extractHeuristicStatesEvaluated(logFile):
	statesEvaluated = 0
	foundOnce = False
	for line in logFile:
		if HEURISTIC_STATE_DELIM in line:
			value = line[line.index(HEURISTIC_STATE_DELIM) + len(HEURISTIC_STATE_DELIM):]
			foundOnce = True
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			statesEvaluated += int(states[0])
	if not foundOnce:
		return -1
	return statesEvaluated

def extractSearchStatesEvaluated(logFile):
	statesEvaluated = 0
	foundOnce = False
	for line in logFile:
		if STATE_DELIM in line:
			value = line[line.index(STATE_DELIM) + len(STATE_DELIM):]
			foundOnce = True
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			statesEvaluated += int(states[0])
	if not foundOnce:
		return -1
	return statesEvaluated

def extractStatesEvaluated(logFile):
	hStatesEvaluated = 0
	statesEvaluated = 0
	foundHOnce = False
	foundOnce = False
	for line in logFile:
		if STATE_DELIM in line:
			value = line[line.index(STATE_DELIM) + len(STATE_DELIM):]
			foundOnce = True
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			statesEvaluated += int(states[0])
		if HEURISTIC_STATE_DELIM in line:
			value = line[line.index(HEURISTIC_STATE_DELIM) + len(HEURISTIC_STATE_DELIM):]
			foundHOnce = True
			hStates = re.findall(r'\d+', value)
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
	noSolnProbFile = open('exp-noSoln.log', 'w')
	csvFile.write("Problem, States, H-States, Total\n")
	path = "/mnt/data/logs/"
	probNoSolnCount = 0
	avgStates = 0.0
	avgHStates = 0.0
	avgTotal = 0.0
	stateCount = 0
	hStateCount = 0
	totalCount = 0
	for filename in os.listdir(path):
		f = open(path+filename, 'r')
		states, hStates, total = extractStatesEvaluated(f)
		if states != -1:
			stateCount += 1
			avgStates = (avgStates * ((stateCount - 1) / float(stateCount))) + (states / float(stateCount))
			csvFile.write("%s, %i, %i, %i\n"%(filename, states, hStates, total))
			if hStates != -1:
				hStateCount += 1
				avgHStates = (avgHStates * ((hStateCount - 1) / float(hStateCount))) + (hStates / float(hStateCount))
				totalCount += 1
				avgTotal = (avgTotal * ((totalCount - 1) / float(totalCount))) + (total / float(totalCount))
		else:
			probNoSolnCount += 1
			noSolnProbFile.write("%s\n"%filename)
		#print ("%s searched %i states and %i states in the heuristic (%i total)"%(filename, states, hStates, total))
	print ("%i problems evaluated. Average of %f states evaluated (%f search and %f heuristic on average. %i were unsolvable)"%(stateCount, avgTotal, avgStates, avgHStates, probNoSolnCount))
	csvFile.write("%i, %f, %f, %f\n"%(stateCount, avgTotal, avgStates, avgHStates))
	csvFile.close()
	noSolnProbFile.close()
#Run Main Function
if __name__ == "__main__":
	main(sys.argv)