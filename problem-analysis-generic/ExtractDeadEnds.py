#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for extracting the number of dead ends encountered by the planner.
#Extracts data to CSV file, including averages.

import sys
import os
import re
import AnalysisCommon

DEAD_END_COUNT_DELIM = "#; Search encountered"
DEAD_END_COUNT_TERM_DELIM = " dead ends"
EHC_SEARCH_STARTING = "Initial heuristic = "
BFS_SEARCH_STARTING = "Resorting to best-first search"

def extractDeadEnds(log):
	for line in log:
		if DEAD_END_COUNT_DELIM in line:
			deadEndCount = re.findall(r'\d+', line)
			return int(deadEndCount[0])
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
	return deadEnds

def main(args):
	inputPath = args[0]
	for filename in os.listdir(inputPath):
		fullQialified = os.path.join(inputPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)
		deadEndCount = extractDeadEndsManually(buffer)
		print filename, deadEndCount

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])