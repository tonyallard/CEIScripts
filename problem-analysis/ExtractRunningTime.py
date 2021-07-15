#! /usr/bin/python
#Author: Tony Allard
#Date: 30 March 2016
#Description: A Python script for extracting the running time of the planner.
#Extracts data to CSV file, including averages.
#NOTE: It omits problems with no solution from CSV file.

import sys
import os
import argparse
import re
import AnalysisCommon

TIME_DELIM = "===TIME TAKEN==="
PDDL_CONVERT_TIME_DELIM = "#; Time spent converting PDDL state:"
PDDL_FILE_WRTIE_TIME_DELIM = "#; Time spent printing state to file:"
H_TIME_DELIM = "#; Time spent in heuristic:"
INITIAL_STATE_H_TIME = "#; Initial State - time spent in heuristic:"
USER_TIME_DELIM = "user "
SYSTEM_TIME_DELIM = "sys "

def extractInitialStateHTime(logFile):
	for line in logFile:
		if INITIAL_STATE_H_TIME in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple PDDL file write times found: %s"%runTime)
			return float(runTime[0])
	return None

def extractPDDLFileWriteTime(logFile):
	for line in logFile:
		if PDDL_FILE_WRTIE_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple PDDL file write times found: %s"%runTime)
			return float(runTime[0])
	return None

def extractPDDLConvertTime(logFile):
	for line in logFile:
		if PDDL_CONVERT_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple PDDL conversion times found: %s"%runTime)
			return float(runTime[0])
	return None

def extractHRunTime(logFile):
	for line in logFile:
		if H_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple heuristic run times found: %s"%runTime)
			return float(runTime[0])
	return None

def extractSystemRunTime(logFile):
	for line in logFile:
		if SYSTEM_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple system run times found: %s"%runTime)
			return float(runTime[0])
	return None

def extractUserRuntime(logFile):
	for line in logFile:
		if USER_TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', line)
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple user run times found: %s"%runTime)
			return float(runTime[0])
	return None

def extractRunTime(logFile):
	user = extractUserRuntime(logFile)
	sys = extractSystemRunTime(logFile)
	if (user is None) or (sys is None):
		return None
	return user + sys

def extractPythonRunTime(logFile):
	i = 0
	for line in logFile:
		if TIME_DELIM in line:
			runTime = re.findall(r'\d+\.\d+', logFile[i+1])
			if len(runTime) != 1:
				raise RuntimeError("Error! Multiple user run times found: %s"%runTime)
			return float(runTime[0])
		i += 1
	raise RuntimeError("Error! Runtime not found.")

def main(args):
	parser = argparse.ArgumentParser(description=' A Python script for extracting the running time of the planner.')
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
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			totalRunTime = 0
			numProbs = 0

			for filename in os.listdir(logPath):
				fullQualified = os.path.join(logPath, filename)
				buffer = AnalysisCommon.bufferCompressedFile(fullQualified)
				if buffer == -1:
					continue
				
				if not AnalysisCommon.isProblemLog(filename, buffer):
					continue
				totalRunTime += extractPythonRunTime(buffer)
				numProbs += 1
			avgRunTime = 0
			if numProbs > 0:
				avgRunTime = totalRunTime/numProbs
			print "\t%s"%problemDomain
			print "\t\tAvg Wall Clock Time: %f"%avgRunTime

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
