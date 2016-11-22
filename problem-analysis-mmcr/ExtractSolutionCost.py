#! /usr/bin/python
#Author: Tony Allard
#Date: 04 November 2016
#Description: A Python script for extracting the solution cost

import sys
import os
import re
import AnalysisCommon

COST_DELIM = "#; Cost: "

def extractCost(log):
	for line in log:
		if COST_DELIM in line:
			cost = re.findall(r'\d+', line)
			return int(deadEndCount[0])
	return None

def extractDeadEndsManually(log):
	#See if search actually started
	started = False
	for line in log:
		if AnalysisCommon.SEARCH_STARTED in line:
			started = True
			break
	if not started:
		return None
	#Find all dead ends from EHC
	deadends = None
	startLine = 0
	for line in log:
		if EHC_SEARCH_STARTING in line:
			break
		startLine += 1
	if AnalysisCommon.SUCCESS_DELIM in log[startLine+1]:
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
		if "Prob-4-12-4-2-8-2_0-191.pddl-11" not in filename:
			continue
		fullQialified = os.path.join(inputPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)
		deadEndCount = extractDeadEndsManually(buffer)
		print filename, deadEndCount

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])