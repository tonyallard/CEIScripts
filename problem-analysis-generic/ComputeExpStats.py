#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for computing stats for experiments
#Extracts data to CSV file, including averages.

import sys
import os
import re
import AnalysisCommon
import ExtractSuccess
import ExtractRunningTime
import ExtractStatesEval
import ExtractDeadEnds

LOG_FILE_EXT = ".pddl[-]*[\d]*.txt"

def isProblemLog(filename, file):
	if re.search(LOG_FILE_EXT, filename) and AnalysisCommon.LOG_FILE_START_SEQ in file[0][:3]:
		return True
	return False

def getProblemDetails(filename):
	idx = filename.lower().index(AnalysisCommon.PDDL_FILE_EXT)
	name = filename[:idx]
	numText = re.findall(r'\d+', filename[idx:])
	number = 0
	if len(numText) == 1:
		number = int(numText[0])
	return name, number

def getMeanAndVar(data):
	mean = 0.0
	samples = 0
	for sample in data:
		if data[sample] is not None:
			mean += data[sample]
			samples += 1
	
	#Check samples special conditions
	if samples is 0: #No mean or variance
		return None, None
	elif samples is 1: #Mean but no variance
		return mean, None
	
	mean /= samples
	#Calculate Variance
	meanDiff = 0.0
	for sample in data:
		if data[sample] is not None:
			meanDiff += pow((data[sample] - mean), 2)
	variance = meanDiff / (samples - 1)
	return mean, variance

def createDataStructure(stats, problemName):
	if problemName not in stats:
		stats[problemName] = {}
		stats[problemName][0] = {}
		stats[problemName][1] = {}
		stats[problemName][2] = {}
		stats[problemName][3] = {}
		stats[problemName][4] = {}
		stats[problemName][5] = {}

def main(args):

	logPath = args[0]

	csvFile = open("experiment.csv", 'w')
	csvFile.write("Problem,Success Mean,Success Variance,Computation Time Mean,Computation Time Variance,Heuristic Computation Time Mean,Heuristic Computation Time Variance,States Evaluated Mean,States Evaluated Variance,Heuristic States Evaluated Mean,Heuristic States Evaluated Variance,Dead Ends Mean,Dead Ends Variance\n")

	stats = {}
	totalProbs = 0
	totalSuccess = 0.0
	avgCompTime = 0.0
	avgHTime = 0.0
	avgStates = 0.0
	avgHStates = 0.0
	avgDeadEnds = 0.0

	for filename in os.listdir(logPath):
		fullQialified = os.path.join(logPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)

		if not isProblemLog(filename, buffer):
			continue

		totalProbs += 1

		problemName, probNumber = getProblemDetails(filename)
		createDataStructure(stats, problemName)

		#Problem Success
		success = ExtractSuccess.extractSuccess(buffer)
		stats[problemName][0][probNumber] = success
		totalSuccess += success
		
		#Computational Time
		compTime = ExtractRunningTime.extractRunTime(buffer)
		stats[problemName][1][probNumber] = compTime
		if compTime is not None:
			avgCompTime += compTime
		
		#Heuristic Time
		hTime = ExtractRunningTime.extractHRunTime(buffer)
		stats[problemName][2][probNumber] = hTime
		if hTime is not None:
			avgHTime += hTime
		
		#States Evaluated
		statesEval, hStates, totalStates = ExtractStatesEval.extractStatesEvaluated(buffer)
		stats[problemName][3][probNumber] = statesEval
		stats[problemName][4][probNumber] = hStates
		if statesEval is not None:
			avgStates += statesEval
		if hStates is not None:
			avgHStates += hStates
		
		#Deadends Encountered
		deadEnds = ExtractDeadEnds.extractDeadEndsManually(buffer)
		stats[problemName][5][probNumber] = deadEnds
		if deadEnds is not None:
			avgDeadEnds += deadEnds

	#Print problem statistics to CSV file
	for problem in stats:
		success = stats[problem][0]
		succMean, succVar = getMeanAndVar(success)
		compTime = stats[problem][1]
		compTimeMean, compTimeVar = getMeanAndVar(compTime)
		hTime = stats[problem][2]
		hTimeMean, hTimeVar = getMeanAndVar(hTime)
		statesEval = stats[problem][3]
		statesEvalMean, statesEvalVar = getMeanAndVar(statesEval)
		hStates = stats[problem][4]
		hStatesMean, hStatesVar = getMeanAndVar(hStates)
		deadEnds = stats[problem][5]
		deadEndsMean, deadEndsVar = getMeanAndVar(deadEnds)

		csvFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(problem, succMean, 
			succVar, compTimeMean, compTimeVar, hTimeMean, hTimeVar, 
			statesEvalMean, statesEvalVar, hStatesMean, hStatesVar, 
			deadEndsMean, deadEndsVar))
		
	#Write averages
	csvFile.write("%i,%i,,%f,,%f,,%f,,%f,,%f\n"%(totalProbs, totalSuccess, 
		avgCompTime/totalProbs, avgHTime/totalProbs, avgStates/totalProbs, 
		avgHStates/totalProbs, avgDeadEnds/totalProbs))
	csvFile.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])