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


def main(args):

	logPath = args[0]

	csvFile = open("experiment.csv", 'w')
	csvFile.write("Problem,Success,Computation Time,Heuristic Computation Time,States Evaluated,Heuristic States Evaluated,Dead Ends\n")

	totalSuccess = 0
	avgCompTime = 0.0
	avgHTime = 0.0
	avgStates = 0.0
	avgHStates = 0.0
	avgDeadEnds = 0.0
	totalProbs = 0

	for filename in os.listdir(logPath):
		fullQialified = os.path.join(logPath, filename)
		f = open(fullQialified)
		buffer = AnalysisCommon.bufferFile(f)

		if not AnalysisCommon.isProblemLog(filename, buffer):
			continue

		totalProbs += 1

		success = ExtractSuccess.extractSuccess(buffer)
		totalSuccess += success
		compTime = ExtractRunningTime.extractRunTime(buffer)
		avgCompTime += compTime
		hTime = ExtractRunningTime.extractHRunTime(buffer)
		avgHTime += hTime
		statesEval, hStates, totalStates = ExtractStatesEval.extractStatesEvaluated(buffer)
		avgStates += statesEval
		avgHStates += hStates
		deadEnds = ExtractDeadEnds.extractDeadEnds(buffer)
		avgDeadEnds += deadEnds

		csvFile.write("%s,%i,%f,%f,%i,%i,%i\n"%(filename, success, compTime, hTime, statesEval, hStates, deadEnds))
		
	#Write averages
	csvFile.write("%i,%i,%f,%f,%f,%f,%f\n"%(totalProbs, totalSuccess, avgCompTime/totalProbs, avgHTime/totalProbs, avgStates/totalProbs, avgHStates/totalProbs, avgDeadEnds/totalProbs))
	csvFile.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv[1:])