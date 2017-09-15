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

def extractDeadEndsManually(log):
	#Find all dead ends from EHC
	deadends = None
	startLine = 0
	for line in log:
		if EHC_SEARCH_STARTING in line:
			break
		startLine += 1
	if startLine+1 > len(log):
		return None
	if AnalysisCommon.COLIN_SUCCESS_DELIM in log[startLine+1]:
		return 0
	for line in log[startLine+2:]:
		deadends = line.count('d')
		break
	#Find all dead ends from BFS
	startLine = 0
	for line in log:
		if BFS_SEARCH_STARTING in line:
			break
		startLine += 1
	#Search for deadends until a termination is encountered
	for line in log[startLine+1:]:
		termination = AnalysisCommon.getTerminationIndex(line)
		if termination is -1:
			termination = len(line)
		deadends += line[:termination].count('d')
		#If we found the termination delimeter
		#then this is the last line to count
		if termination is not len(line):
			break
	return deadends

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