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
import argparse
import collections
import AnalysisCommon
import ExtractSuccess

HEURISTIC_STATE_DELIM = "#; Heuristic States Evaluated: "
STATE_DELIM = "#; States evaluated: "
INITIAL_STATE_STATES_EVAL = "#; Initial State - heuristic states evaluated:"
TPLAN_STATE_DELIM = r"[0-9]+ \| [0-9\-]+ [0-9\:]+\: \[info\][\s]+Sub\-problem iteration [0-9]+"
#000013 | 2021-06-04 14:59:03: [info]	27 conflicted constraints found.
TPLAN_HSTATE_DELIM = r"[0-9]+ \| [0-9\-]+ [0-9\:]+\: \[info\][\s]+([0-9]+) conflicted constraints found."

COLIN_LIKE_STATES = [
	"Colin-RPG", 
	"POPF-RPG", 
	"Optic-RPG", 
	"Optic-SLFRP"
]

TRH_LIKE_STATES = [
	"Colin-TRH-Colin", 
	"Popf-TRH-Popf"
]

TPLAN_LIKE_STATES = [
	"tplan",
	"tplanS0T0", 
	"tplanS0T1",
	"tplanS1T0",
	"tplanS1T1",
	"tplanS2T0",
	"tplanS2T1",
	"tplanS3T0",
	"tplanS3T1",
	"tplanS4T0",
	"tplanS4T1",
	"tplanS5T0",
	"tplanS5T1",
	"tplanS6T0",
	"tplanS6T1",
	"tplanS7T0",
	"tplanS7T1"
]

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

def getTRHStatesEvaluated(logFile):
	statesEvaluated = extractSearchStatesEvaluated(logFile)
	hStatesEvaluated = extractHeuristicStatesEvaluated(logFile)
	total = None
	if (statesEvaluated is not None) and (hStatesEvaluated is not None):
		total = statesEvaluated+hStatesEvaluated
	
	return statesEvaluated, hStatesEvaluated, total

def getColinLikeStatesEvaluated(logBuffer):
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

def getTPlanStatesEvaluated(logfile):
	statesEval = 0
	hStatesEval = 0
	for line in logfile:
		if re.match(TPLAN_STATE_DELIM, line):
			statesEval += 1
		hStatesMatch = re.match(TPLAN_HSTATE_DELIM, line)
		if hStatesMatch:
			hStatesEval += int(hStatesMatch.group(1))
	return statesEval, hStatesEval, hStatesEval + statesEval

def getStatesEvaluated(planner, logfile):
	if planner in COLIN_LIKE_STATES:
		states = getColinLikeStatesEvaluated(logfile) 
		return states, 0, states #Currently we do not detect heuristic states
	elif planner in TRH_LIKE_STATES:
		return getTRHStatesEvaluated(logfile)
	elif planner in TPLAN_LIKE_STATES:
		return getTPlanStatesEvaluated(logfile) #Note heuristic states is the total length of no-goods
	else:
		raise RuntimeError("Error! Unrecognised planner: %s"%planner)

def main(args):
	parser = argparse.ArgumentParser(description='A Python script for extracting the coverage of a problem domain from experimentation logs.')
	parser.add_argument('path',
	                    metavar='/path/to/planner/logs/',
						type=str,
		                help='the location of the logs for a specific planner')
	parser.add_argument('-v',
						'--verbose',
						action='store_true',
						help='Show individual problem stats')
	args = parser.parse_args()
		                
	if not os.path.isdir(args.path):
		print("Error: %s is not a valid directory"%args.path)
		sys.exit(-1)
	
	inputPath = args.path

	logStructure = AnalysisCommon.getLogStructure(inputPath)

	for planner in logStructure:
		print(planner)
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			totalEvalCount = 0
			successful = 0
			avgStates = 0.0
			avgHStates = 0.0
			avgTotal = 0.0
			stateCount = 0
			hStateCount = 0
			totalCount = 0

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				buffer = AnalysisCommon.bufferCompressedFile(fullQualified)
				if buffer == -1:
					continue
			
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue

				totalEvalCount += 1
				if ExtractSuccess.extractValidatorSuccess(buffer, planner, fullQualified):
					successful += 1
					sCount, hCount, tCount = getStatesEvaluated(planner, buffer)
					if (args.verbose):
						print("\t\t\t%s:%s/%s/%s"%(filename,sCount,hCount,tCount))

					if sCount != -1:
						stateCount += sCount
					if hCount != -1:
						hStateCount += hCount
					if tCount != -1:
						totalCount += tCount

			if (successful > 0):
				avgStates = stateCount / float(successful)
				avgHStates = hStateCount / float(successful)
				avgTotal = totalCount / float(successful)
	
			print("\t%s"%problemDomain)
			print("\t\tSuccess/Failure/Total: %i/%i/%i"%(successful, totalEvalCount-successful, totalEvalCount))
			print("\t\tStates Eval / Average: %i/%f"%(stateCount, avgStates))
			print("\t\tHeuristic States Eval / Average: %i/%f"%(hStateCount, avgHStates))
			print("\t\tTotal States Eval / Average: %i/%f"%(totalCount, avgTotal))
	
#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
