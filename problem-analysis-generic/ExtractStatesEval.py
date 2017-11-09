#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the states evaluated from a log file.
#Extracts states evaluated to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import re
import gzip
import collections
import AnalysisCommon

HEURISTIC_STATE_DELIM = "#; Heuristic States Evaluated: "
STATE_DELIM = "#; States evaluated: "
INITIAL_STATE_STATES_EVAL = "#; Initial State - heuristic states evaluated:"

def extractInitialStateHeuristicStatesEvaluated(logFile):
	for line in logFile:
		if INITIAL_STATE_STATES_EVAL in line:
			value = line[line.index(INITIAL_STATE_STATES_EVAL) + len(INITIAL_STATE_STATES_EVAL):]
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			return int(states[0])
	return None

def extractHeuristicStatesEvaluated(logFile):
	for line in logFile:
		if HEURISTIC_STATE_DELIM in line:
			value = line[line.index(HEURISTIC_STATE_DELIM) + len(HEURISTIC_STATE_DELIM):]
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			return int(states[0])
	return None
	
def extractSearchStatesEvaluated(logFile):
	for line in logFile:
		if STATE_DELIM in line:
			value = line[line.index(STATE_DELIM) + len(STATE_DELIM):]
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple state counts found: %s"%states)
			return int(states[0])
	return None

def extractStatesEvaluated(logFile):
	statesEvaluated = extractSearchStatesEvaluated(logFile)
	hStatesEvaluated = extractHeuristicStatesEvaluated(logFile)
	total = None
	if (statesEvaluated is not None) and (hStatesEvaluated is not None):
		total = statesEvaluated+hStatesEvaluated
	
	return statesEvaluated, hStatesEvaluated, total

def genericExtractStatesEvaluated(logBuffer):
	startIdx = -1
	i = 0
	for line in logBuffer:
		if line.find(AnalysisCommon.SEARCH_BEGIN_DELIM) >= 0:
			startIdx = i
			break
		i+=1
	if startIdx == -1:
		return None
	stateTypeCount = collections.defaultdict(int)
	for x in range(startIdx+1, len(logBuffer)):
		for c in AnalysisCommon.filterBranchString(logBuffer[x]):
			# print AnalysisCommon.filterBranchString(logBuffer[x])
			stateTypeCount[c] += 1
		if any(substring in logBuffer[x] for substring in AnalysisCommon.TERMINATE_FLAGS):
			if "Beginning the replay" in logBuffer[x]:
				stateTypeCount['g'] += 1
			break
	return 1 + stateTypeCount['.'] + stateTypeCount['b'] + stateTypeCount['d'] + stateTypeCount['g']

def main2(args):
	path = sys.argv[1]
	for filename in os.listdir(path):
		with gzip.open(os.path.join(path, filename), 'rb') as f:
			log = []
			for x in f:
				log.append(x)
			statesEval = genericExtractStatesEvaluated(log)
			print filename, statesEval

def main3(args):
	file = sys.argv[1]
	with gzip.open(file, 'rb') as f:
		log = []
		for x in f:
			log.append(x)
		statesEval = genericExtractStatesEvaluated(log)
		print file, statesEval

def main(args):
	csvFile = open('states-data.csv', 'w')
	csvFile.write("Problem, Search States, Heuristic States, Total States\n")

	path = args[0]
	
	totalEvalCount = 0

	probNoSolnCount = 0
	avgStates = 0.0
	avgHStates = 0.0
	avgTotal = 0.0
	stateCount = 0
	hStateCount = 0
	totalCount = 0

	for filename in os.listdir(path):
		fullQialified = os.path.join(path, filename)
		f = open(fullQialified, 'r')
		fileBuffer = AnalysisCommon.bufferFile(f)

		#Check if this is a problem log
		if not AnalysisCommon.isProblemLog(filename, fileBuffer):
			continue

		totalEvalCount += 1

		states, hStates, total = extractStatesEvaluated(fileBuffer)
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
			if (AnalysisCommon.checkArgs("-f", args)):
				#Include Fails in CSV
				csvFile.write("%s, , , \n"%(filename))

	print "%i problems evaluated (%i were valid)."%(totalEvalCount, stateCount)
	print "Average of %f states evaluated (%f search and %f heuristic on average. %i were not solved)"%(avgTotal, avgStates, avgHStates, probNoSolnCount)
	csvFile.write(",,,\n")
	csvFile.write("%i, %f, %f, %f\n"%(stateCount, avgTotal, avgStates, avgHStates))
	csvFile.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
