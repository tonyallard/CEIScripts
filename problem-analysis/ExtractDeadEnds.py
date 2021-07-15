#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting the number of dead ends encountered by the planner.
#Extracts data to CSV file, including averages.

import sys
import os
import argparse
import re
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

def main(args):
	parser = argparse.ArgumentParser(description='A Python script for extracting the number of dead ends encountered by the planner.')
	parser.add_argument('path',
	                    metavar='/path/to/planner/logs/',
						type=str,
		                help='the location of the logs for a specific planner')
	args = parser.parse_args()
		                
	if not os.path.isdir(args.path):
		print("Error: %s is not a valid directory"%args.path)
		sys.exit(-1)
	
	inputPath = args.path

	logStructure = AnalysisCommon.getLogStructure(inputPath)

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
				buffer = AnalysisCommon.bufferCompressedFile(fullQualified)
				if buffer == -1:
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
