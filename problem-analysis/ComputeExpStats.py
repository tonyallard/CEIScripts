#! /usr/bin/python
#Author: Tony Allard
#Date: 07 October 2016
#Description: A Python script for computing stats for experiments
#Extracts data to CSV file, including averages.

import sys
import os
import re
import gzip
import AnalysisCommon
from ProblemDomainStats import *

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

def processProblemDomainStatistics(planner, problemDomain, logPath):

	probDomStats = ProblemDomainStats(planner, problemDomain)

	for filename in os.listdir(logPath):
		fullQualified = os.path.join(logPath, filename)
		try:
			with gzip.open(fullQualified, 'rb') as f:
			
				buffer = AnalysisCommon.bufferFile(f)
		except IOError:
			continue

		if not AnalysisCommon.isProblemLog(filename, buffer):
			continue

		problemName, probNumber = getProblemDetails(filename)
		probDomStats.processProblemLog(problemName, probNumber, buffer)

	return probDomStats

def main(args):

	rootLogPath = args[0]
	csvPath = "."
	if len(args) > 1:
		csvPath = args[1]

	logStructure = getLogStructure(rootLogPath)
					
	for planner in logStructure:
		print planner
		for problemDomain in logStructure[planner]:
			logPath = logStructure[planner][problemDomain]

			#open stats file
			csvFile = open(os.path.join(csvPath, "%s-%s.csv"%(planner, problemDomain)), 'w')
			csvFile.write("Problem,Success Mean,Success Variance,Computation Time Mean,Computation Time Variance,Heuristic Computation Time Mean,Heuristic Computation Time Variance,States Evaluated Mean,States Evaluated Variance,Heuristic States Evaluated Mean,Heuristic States Evaluated Variance,Colin States Evaluated Mean,Colin States Evaluated Variance,Dead Ends Mean,Dead Ends Variance,Time Per State Eval Mean,Time Per State Eval Variance,Initial State Heuristic Time Mean,Initial State Heuristic Time Variance,Initial State Heuristic States Mean,Initial State Heuristic States Variance,Initial State Dead Ends Mean,Initial State Dead Ends Variance\n")

			probDomStats = processProblemDomainStatistics(planner, 
				problemDomain, logPath)
			print "\t%s %s"%(probDomStats.problemDomain, probDomStats.totalProbs)
			if (probDomStats.totalProbs <= 0):
				continue
			#Print problem statistics to CSV file
			for problem in sorted(probDomStats.stats):
				success = probDomStats.getProblemSuccess(problem)
				succMean, succVar = getMeanAndVar(success)

				compTime = probDomStats.getProblemCompTime(problem)
				compTimeMean, compTimeVar = getMeanAndVar(compTime)
				
				hTime = probDomStats.getProblemHTime(problem)
				hTimeMean, hTimeVar = getMeanAndVar(hTime)
				
				statesEval = probDomStats.getProblemStatesEval(problem)
				statesEvalMean, statesEvalVar = getMeanAndVar(statesEval)
				
				hStates = probDomStats.getProblemHStatesEval(problem)
				hStatesMean, hStatesVar = getMeanAndVar(hStates)

				colinStates = probDomStats.getProblemColinStatesEval(problem)
				colinStatesMean, colinStatesVar = getMeanAndVar(colinStates)
				
				deadEnds = probDomStats.getProblemDeadEnds(problem)
				deadEndsMean, deadEndsVar = getMeanAndVar(deadEnds)
				
				timePerStateEval = probDomStats.getProblemTimePerStateEval(problem)
				timePerStateEvalMean, timePerStateEvalVar = getMeanAndVar(timePerStateEval)

				initStateHTime = probDomStats.getProblemInitStateHTime(problem)
				initStateHTimeMean, initStateHTimeVar = getMeanAndVar(initStateHTime)

				initStateHStates = probDomStats.getProblemInitStateHStates(problem)
				initStateHStatesMean, initStateHStatesVar = getMeanAndVar(initStateHStates)

				initStateDeadEnds = probDomStats.getProblemInitStateDeadEnds(problem)
				initStateDeadEndsMean, initStateDeadEndsVar = getMeanAndVar(initStateDeadEnds)				

				csvFile.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(problem, succMean, 
					succVar, compTimeMean, compTimeVar, hTimeMean, hTimeVar, 
					statesEvalMean, statesEvalVar, hStatesMean, hStatesVar, 
					colinStatesMean, colinStatesVar,
					deadEndsMean, deadEndsVar,
					timePerStateEvalMean, timePerStateEvalVar,
					initStateHTimeMean, initStateHTimeVar,
					initStateHStatesMean, initStateHStatesVar,
					initStateDeadEndsMean, initStateDeadEndsVar))

			#Write averages
			csvFile.write("%i,%i,,%f,,%f,,%f,,%f,,%f,,%f,,%f,,%f,,%f,,%f"%(probDomStats.totalProbs, 
				probDomStats.totalSuccess, 
				probDomStats.avgCompTime/probDomStats.totalProbs, 
				probDomStats.avgHTime/probDomStats.totalProbs, 
				probDomStats.avgStates/probDomStats.totalProbs, 
				probDomStats.avgHStates/probDomStats.totalProbs,
				probDomStats.avgColinStates/probDomStats.totalProbs,
				probDomStats.avgDeadEnds/probDomStats.totalProbs,
				probDomStats.avgTimePerStateEval/probDomStats.totalProbs,
				probDomStats.avgInitStateHTime/probDomStats.totalProbs,
				probDomStats.avgInitStateHStates/probDomStats.totalProbs,
				probDomStats.avgInitStateDeadEnds/probDomStats.totalProbs))
			csvFile.close()


#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])
