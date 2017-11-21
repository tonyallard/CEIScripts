#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting the number of dead ends encountered by the planner.
#Extracts data to CSV file, including averages.

import sys
import os
import re
import gzip
import AnalysisCommon

DEAD_END_COUNT_DELIM = "#; Search encountered"
DEAD_END_COUNT_TERM_DELIM = " dead ends"
EHC_SEARCH_STARTING = "Initial heuristic = "
BFS_SEARCH_STARTING = "Resorting to best-first search"
INITIAL_STATE_DEADENDS = "#; Initial State - dead ends encountered:"

def extractDeadEnds(log):
	for line in log:
		if DEAD_END_COUNT_DELIM in line:
			deadEndCount = re.findall(r'\d+', line)
			return int(deadEndCount[0])
	return None

def extractInitialStateDeadEnds(log):
	for line in log:
		if INITIAL_STATE_DEADENDS in line:
			value = line[line.index(INITIAL_STATE_DEADENDS) + len(INITIAL_STATE_DEADENDS):]
			states = re.findall(r'\d+', value)
			if len(states) != 1:
				raise RuntimeError("Error! Multiple dead end counts found: %s"%states)
			return int(states[0])
	return None

def extractDeadEndsManually(logBuffer):
	startIdx = -1
	i = 0
	for line in logBuffer:
		if line.find(AnalysisCommon.SEARCH_BEGIN_DELIM) >= 0:
			startIdx = i
			break
		i+=1
	if startIdx == -1:
		return None

	deadEnds = 0
	for x in range(startIdx+1, len(logBuffer)):
		deadEnds += AnalysisCommon.filterBranchString(logBuffer[x]).count('d')
		if any(substring in logBuffer[x] for substring in AnalysisCommon.TERMINATE_FLAGS):
			break	
	return int(deadEnds)

def getLogStructure(rootDir):
	logStructure = {}
	for planner in os.listdir(rootDir):
		plannerDir = os.path.join(rootDir, planner)
		
		if (not os.path.isdir(plannerDir)):
			continue
		
		logStructure[planner] = {}

		for problem in os.listdir(plannerDir):
			#Driverlog shift is too different a format
			if problem == "driverlogshift":
				continue
			logDir = os.path.join(plannerDir, problem, AnalysisCommon.OUTPUT_DIR)
			logStructure[planner][problem] = logDir
	return logStructure

def main(args):
	inputPath = args[0]

	logStructure = getLogStructure(inputPath)

	for planner in logStructure:
		print planner
		if planner == "lpg-td":
			continue
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			deadEnds = 0
			initialState_deadEnds = 0
			probsConsidered = 0 

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				try:
					with gzip.open(fullQualified, 'rb') as f:
					
						buffer = AnalysisCommon.bufferFile(f)
				except IOError:
					continue
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				tmpDeadEnds = extractDeadEndsManually(buffer)
				if tmpDeadEnds is not None:
					deadEnds += tmpDeadEnds
				tmpInitStateDeadEnds = extractInitialStateDeadEnds(buffer)
				if tmpInitStateDeadEnds is not None:
					initialState_deadEnds += tmpInitStateDeadEnds
				
				probsConsidered += 1
				
			print "\t%s"%problemDomain
			print "\t\tAvg Dead Ends: %f"%(deadEnds/probsConsidered)
			print "\t\tAvg Initial State Dead Ends: %f"%(initialState_deadEnds/probsConsidered)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])